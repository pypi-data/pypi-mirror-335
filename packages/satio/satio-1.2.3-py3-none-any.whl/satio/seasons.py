import numpy as np
from matplotlib import pyplot as plt
from datetime import datetime
# from scipy.signal import find_peaks
import warnings
from numba import njit, float32, int64, int16, float64
from numba.types import Tuple
import satio
from satio.features import Features


def second_to_day(seconds):
    return seconds / (24 * 3600)


def day_to_second(days):
    return days * 24 * 3600


def find_nearest(array, value):
    array = np.asarray(array)
    return np.abs(array - value).argmin()


def nearest_date(items, pivot):
    return min(items, key=lambda x: abs(x - pivot))


@njit(int64[:](float32[:]))
def find_peaks(x):

    peak_index = []

    for i, val in enumerate(x[1:-1], 1):

        if val >= x[i-1] and val > x[i+1]:
            peak_index.append(i)

    if x[-1] > x[-2]:
        peak_index.append(len(x) - 1)

    if x[0] > x[1]:
        peak_index.append(0)

    return np.array(peak_index)


def detect_seasons(timeseries,
                   max_seasons=5,
                   amp_thr1=0.1,
                   amp_thr2=0.35,
                   min_window=10,
                   max_window=185,
                   partial_start=False,
                   partial_end=False) -> 'Seasons':
    '''
    Computes peak, SOS and EOS of all seasons from a given timeseries

    SOS, MOS and EOS are stored as datetime.timestamp()

    :param timeseries: the Timeseries object from which to derive the seasons
    (should only contain one band!). The data cannot contain any NaN's!
    :param max_seasons: maximum number of seasons to be detected
    :param amp_thr1: minimum threshold for amplitude of a season
    :param amp_thr2: factor with which to multiply total
        amplitude of signal to derive second minimum amplitude threshold
    :param min_window: search window for finding start and end
        before/after peak - minimum distance from peak in days
    :param max_window: search window for finding start and end
        before/after peak - maximum distance from peak in days
    :param partial_start and partial_end: whether or not to
        detect partial seasons
        (if partial_start = True, season is allowed to have
        SOS prior to start of time series;
        if partial_end = True, season is allowed to have
        EOS after end of time series)

    returns a Seasons object with for each pixel SOS, MOS, EOS and nSeasons
    '''

    if timeseries.data.shape[0] != 1:
        raise ValueError('Timeseries as input for detect_seasons '
                         'should only contain one band!')
    data = np.squeeze(timeseries.data, axis=0)

    if data.ndim != 3:
        raise ValueError('Timeseries does not have the right dimensions')

    times = np.array([t.timestamp() for t in timeseries.timestamps])

    @njit(Tuple((int16[:, :], float32[:, :, :],
                 float32[:, :, :], float32[:, :, :]))(
                     float32[:, :, :], float64[:]))
    def _detect_seasons_fast(data, times):

        def _day_to_second(days):
            return days * 24 * 3600

        def _find_nearest(array, value):
            array = np.asarray(array)
            return np.abs(array - value).argmin()

        # prepare outputs
        nx = data.shape[1]
        ny = data.shape[2]

        nseasons = np.zeros((nx, ny), dtype=np.int16)
        sos = np.zeros((max_seasons, nx, ny), dtype=np.float32)
        mos = np.zeros((max_seasons, nx, ny), dtype=np.float32)
        eos = np.zeros((max_seasons, nx, ny), dtype=np.float32)

        sos[...] = np.nan
        mos[...] = np.nan
        eos[...] = np.nan

        # loop over each individual pixel to define
        # start, peak and end of season(s)

        for i in range(nx):
            for j in range(ny):
                data_pix = data[:, i, j]
                # find all local maxima
                localmax_idx = find_peaks(data_pix)
                if localmax_idx.size == 0:
                    # no peaks found, proceed to next pixel
                    continue
                localmax = data_pix[localmax_idx]

                # sort local maxima according to VI amplitude
                sort_idx = localmax.argsort()
                localmax_idx_sorted = localmax_idx[sort_idx]

                # define outputs
                npeaks = localmax_idx_sorted.shape[0]
                valid = np.ones(npeaks, dtype=np.uint8)
                start = np.zeros(npeaks, dtype=np.int32)
                end = np.zeros(npeaks, dtype=np.int32)

                # setting some threshold values
                totalrange = np.max(data_pix) - np.min(data_pix)
                amp_thr2_fin = amp_thr2 * totalrange

                # find for each peak the associated local minima
                # and decide whether
                # the peak is valid or not
                for p in range(npeaks):

                    skip_sos = False

                    idx = localmax_idx_sorted[p]
                    # define search window for SOS
                    t_idx = times[idx]
                    t_min = t_idx - _day_to_second(max_window)
                    idx_min = _find_nearest(times, t_min)
                    t_max = t_idx - _day_to_second(min_window)
                    idx_max = _find_nearest(times, t_max)

                    # if peak is very close to start of TS...
                    if idx_max == 0:
                        if partial_start:
                            # and partial season mapping is allowed
                            # -> skip SOS detection
                            skip_sos = True
                        else:
                            # else, peak is invalid
                            valid[p] = 0
                            continue

                    # do SOS check if necessary
                    if not skip_sos:
                        # adjust search window in case there is a valid
                        # peak within the window
                        # find all intermediate VALID peaks
                        val_peaks = localmax_idx_sorted.copy()
                        val_peaks[valid == 0] = -1
                        int_peaks_idx = localmax_idx_sorted[(
                            val_peaks > idx_min) & (val_peaks < idx)]
                        # if any, find the peak nearest to original peak
                        # and set t_min to that value
                        if int_peaks_idx.shape[0] > 0:
                            idx_min = np.max(int_peaks_idx)
                            # if, by adjusting the window, idx_max <
                            # idx_min -> label peak as invalid
                            if idx_max < idx_min:
                                valid[p] = 0
                                continue

                        # identify index of local minimum in search window
                        win = data_pix[idx_min:idx_max+1]
                        start[p] = np.where(win == np.amin(win))[0][0] + idx_min

                        # check if amplitude conditions of the identified
                        # starting point are met
                        amp_dif = data_pix[idx] - data_pix[start[p]]
                        if not (amp_dif >= amp_thr1) & (amp_dif >= amp_thr2_fin):
                            # if partial season mapping is allowed,
                            # and search window includes start of TS,
                            # the true SOS could be before start of TS.
                            # So we skip sos check, meaning eos check
                            # should definitely be done
                            if partial_start and (idx_min == 0):
                                skip_sos = True
                            else:
                                valid[p] = 0
                                continue

                    # define search window for EOS
                    t_min = t_idx + _day_to_second(min_window)
                    idx_min = _find_nearest(times, t_min)
                    t_max = t_idx + _day_to_second(max_window)
                    idx_max = _find_nearest(times, t_max)
                    # adjust search window in case there is a valid
                    # peak within the window
                    # find all intermediate VALID peaks
                    val_peaks = localmax_idx_sorted.copy()
                    val_peaks[valid == 0] = -1
                    int_peaks_idx = localmax_idx_sorted[(val_peaks > idx) & (
                        val_peaks < idx_max)]
                    # if any, find the peak nearest to original peak
                    # and set t_max to that value
                    if int_peaks_idx.shape[0] > 0:
                        idx_max = np.min(int_peaks_idx)
                        # if, by adjusting the window, idx_max
                        # < idx_min -> label peak as invalid
                        if idx_max < idx_min:
                            valid[p] = 0
                            continue

                    # in case you've reached the end of the timeseries,
                    # adjust idx_max
                    if idx_max == data_pix.shape[0] - 1:
                        idx_max -= 1
                    # identify index of local minimum in search window
                    if idx_max < idx_min:
                        end[p] = data_pix.shape[0] - 1
                    else:
                        win = data_pix[idx_min:idx_max+1]
                        end[p] = np.where(win == np.amin(win))[0][0] + idx_min

                    # if partial season mapping is allowed
                    # AND sos check was not skipped
                    # AND search window includes end of TS
                    # THEN the end of season check can be skipped

                    if (partial_end and (not skip_sos) and
                            (idx_max == data_pix.shape[0] - 2)):
                        continue
                    else:
                        # check if amplitude conditions of the identified
                        # end point are met
                        amp_dif = data_pix[idx] - data_pix[end[p]]
                        if not (amp_dif >= amp_thr1) & (
                                amp_dif >= amp_thr2_fin):
                            valid[p] = 0

                # now delete invalid peaks
                idx_valid = np.where(valid == 1)[0]
                peaks = localmax_idx_sorted[idx_valid]
                start = start[valid == 1]
                end = end[valid == 1]
                npeaks = peaks.shape[0]

                # if more than max_seasons seasons detected ->
                # select the seasons with highest amplitudes
                if npeaks > max_seasons:
                    toRemove = npeaks - max_seasons
                    maxSeason = data_pix[peaks]

                    baseSeason = np.mean(np.stack((data_pix[start],
                                                   data_pix[end])))
                    amp = maxSeason - baseSeason
                    idx_remove = np.zeros_like(amp)
                    for r in range(toRemove):
                        idx_remove[np.where(amp == np.min(amp))[0][0]] = 1
                        amp[np.where(amp == np.min(amp))[0][0]] = np.max(amp)
                    # check whether enough seasons will be removed
                    check = toRemove - np.sum(idx_remove)
                    if check > 0:
                        # remove random seasons
                        for r in range(int(check)):
                            idx_remove[np.where(idx_remove == 0)[0][0]] = 1
                    # remove the identified peaks
                    peaks = peaks[idx_remove != 1]
                    start = start[idx_remove != 1]
                    end = end[idx_remove != 1]
                    npeaks = max_seasons

                # convert indices to actual corresponding dates
                peaktimes = times[peaks]
                starttimes = times[start]
                endtimes = times[end]

                # if less than max_seasons seasons detected -> add
                # dummy seasons
                if peaktimes.shape[0] < max_seasons:
                    toAdd = np.ones(max_seasons - peaktimes.shape[0],
                                    dtype=np.float32) * -1
                    starttimes = np.concatenate((starttimes, toAdd))
                    endtimes = np.concatenate((endtimes, toAdd))
                    peaktimes = np.concatenate((peaktimes, toAdd))

                # transfer to output
                mos[:, i, j] = peaktimes
                sos[:, i, j] = starttimes
                eos[:, i, j] = endtimes
                nseasons[i, j] = npeaks
        return nseasons, sos, mos, eos

    (nseasons, sos, mos, eos) = _detect_seasons_fast(data, times)

    return Seasons(nseasons, sos, mos, eos, timeseries)


class Seasons:

    def __init__(self,
                 nseasons: np.ndarray,
                 sos: np.ndarray,
                 mos: np.ndarray,
                 eos: np.ndarray,
                 ts: 'satio.timeseries.Timeseries',
                 dtype1: type = np.int16,
                 dtype2: type = np.float32):

        if nseasons.ndim != 2:
            raise ValueError('nseasons should be 2-dimensional')
        if sos.ndim == 2:
            sos = np.expand_dims(sos, axis=0)
        if mos.ndim == 2:
            mos = np.expand_dims(mos, axis=0)
        if eos.ndim == 2:
            eos = np.expand_dims(eos, axis=0)

        nx, ny = nseasons.shape
        if (((sos.shape[1] != nx) or
             (mos.shape[1] != nx)) or
                (eos.shape[1] != nx)):
            raise ValueError('Dimensions of inputs not consistent')
        if (((sos.shape[2] != ny) or
             (mos.shape[2] != ny)) or
                (eos.shape[2] != ny)):
            raise ValueError('Dimensions of inputs not consistent')

        self.ts = ts

        if nseasons.dtype != dtype1:
            self.nseasons = nseasons.astype(dtype1)
        else:
            self.nseasons = nseasons

        if sos.dtype != dtype2:
            self.sos = sos.astype(dtype2)
        else:
            self.sos = sos

        if mos.dtype != dtype2:
            self.mos = mos.astype(dtype2)
        else:
            self.mos = mos

        if eos.dtype != dtype2:
            self.eos = eos.astype(dtype2)
        else:
            self.eos = eos

    def _clone(self,
               nseasons: np.ndarray = None,
               sos: np.ndarray = None,
               mos: np.ndarray = None,
               eos: np.ndarray = None,
               ts: 'satio.timeseries.Timeseries' = None,
               dtype1: type = None,
               dtype2: type = None):

        nseasons = self.nseasons if nseasons is None else nseasons
        sos = self.sos if sos is None else sos
        mos = self.mos if mos is None else mos
        eos = self.eos if eos is None else eos
        ts = self.ts if ts is None else ts
        dtype1 = self.nseasons.dtype if dtype1 is None else dtype1
        dtype2 = self.sos.dtype if dtype2 is None else dtype2

        return self.__class__(nseasons, sos, mos, eos, ts, dtype1, dtype2)

    def visualize(self, x, y, ts=None, outfile=None):
        '''
        Plot seasons for a given pixel x,y

        :param x: row index of pixel to be plotted
        :param y: column index of pixel to be plotted
        :param ts: optional timeseries to be used for plotting,
            if None, then the timeseries will be used from which the seasons
            were derived
        '''

        if ts is None:
            ts = self.ts

        data = np.squeeze(ts.data)
        if data.ndim != 3:
            raise ValueError('Timeseries as input for detect_seasons'
                             'should only contain one band!')
        times = ts.timestamps

        # plot timeseries
        f, ax = plt.subplots()
        ts = np.squeeze(data[:, x, y])
        ax.plot(times, ts)

        # plot all seasons for particular pixel
        npeaks = self.nseasons[x, y]
        for p in range(npeaks):
            startdate = datetime.fromtimestamp(self.sos[p, x, y])
            startidx = np.where(times == nearest_date(times, startdate))[0][0]
            peakdate = datetime.fromtimestamp(self.mos[p, x, y])
            peakidx = np.where(times == nearest_date(times, peakdate))[0][0]
            enddate = datetime.fromtimestamp(self.eos[p, x, y])
            endidx = np.where(times == nearest_date(times, enddate))[0][0]
            ax.plot(times[startidx], ts[startidx], 'go')
            ax.plot(times[peakidx], ts[peakidx], 'k+')
            ax.plot(times[endidx], ts[endidx], 'ro')

        # save resulting plot if requested
        if outfile is not None:
            plt.savefig(outfile)

    def select(self, mode, param, ts=None):
        '''
        Select one or multiple seasons based on some criteria...

        :param mode: method used for the selection.
        Currently the following options are included:
        - first -> selection of first x seasons (x defined by param)
        - last -> selection of last x seasons (x defined by param)
        - year -> select all seasons with their peak in a certain year
            (year defined by param)
        - amplitude -> select x seasons with highest/lowest amplitudes
            (x defined by param; positive means highest, negative means lowest)
        - length -> select x seasons with highest/lowest length of season
            (x defined by param; positive means highest, negative means lowest)
        - date -> select season with sos closest to a certain date
            (date as a string AND max deviation in days
            defined by param as a list)
        :param param: additional parameter(s) to be used during selection,
        see list above
        :param ts: optional timeseries used in the selection
            (only used in case of amplitude mode)

        Returns a Seasons object containing only the selected seasons
        '''

        if ts is None:
            ts = self.ts

        if mode not in ['first', 'last', 'year',
                        'amplitude', 'length', 'date']:
            raise ValueError('Selected mode not supported')

        data = np.squeeze(ts.data)
        times = ts.timestamps
        timesfloat = np.array([t.timestamp() for t in times])

        # prepare output
        nx = data.shape[1]
        ny = data.shape[2]
        nseas = self.sos.shape[0]
        if (mode in ['first', 'last', 'amplitude', 'length']):
            nseas = abs(param)
        elif mode == 'date':
            nseas = 1
        nseasons = np.zeros((nx, ny), dtype='int16')
        sos = np.ones((nseas, nx, ny), dtype='float32') * -1
        mos = np.ones((nseas, nx, ny), dtype='float32') * -1
        eos = np.ones((nseas, nx, ny), dtype='float32') * -1

        # loop over 2D patch of data
        for i in range(nx):
            for j in range(ny):
                # if no seasons detected -> don't do any selection
                npeaks = self.nseasons[i, j]
                if npeaks == 0:
                    continue

                # retrieve valid seasons
                start = np.asarray(self.sos[0:npeaks, i, j])
                peaks = np.asarray(self.mos[0:npeaks, i, j])
                end = np.asarray(self.eos[0:npeaks, i, j])

                # if number of seasons requested is larger or equal than
                # number of valid seasons:
                # select all seasons and fill with dummy seasons
                if ((mode in ['first', 'last', 'amplitude', 'length']) and
                        (npeaks <= abs(param))):
                    ndif = abs(param) - npeaks
                    start_sel = np.concatenate((start,
                                                np.ones(ndif, dtype='float32')
                                                * -1))
                    peaks_sel = np.concatenate((peaks,
                                                np.ones(ndif, dtype='float32')
                                                * -1))
                    end_sel = np.concatenate((end,
                                              np.ones(ndif, dtype='float32')
                                              * -1))

                # selection of first x seasons (x defined by param)
                elif mode == 'first':
                    start_sel = np.zeros(param, dtype='float32')
                    peaks_sel = np.zeros(param, dtype='float32')
                    end_sel = np.zeros(param, dtype='float32')
                    nsel = 0
                    while nsel < param:
                        idx = np.where(start == min(start))[0][0]
                        start_sel[nsel] = start[idx]
                        peaks_sel[nsel] = peaks[idx]
                        end_sel[nsel] = end[idx]
                        start = np.delete(start, idx)
                        nsel += 1

                # selection of last x seasons (x defined by param)
                elif mode == 'last':
                    start_sel = np.zeros(param, dtype='float32')
                    peaks_sel = np.zeros(param, dtype='float32')
                    end_sel = np.zeros(param, dtype='float32')
                    nsel = 0
                    while nsel < param:
                        idx = np.where(start == max(start))[0][0]
                        start_sel[nsel] = start[idx]
                        peaks_sel[nsel] = peaks[idx]
                        end_sel[nsel] = end[idx]
                        start = np.delete(start, idx)
                        nsel += 1

                # select x seasons with highest/lowest amplitudes
                # (x defined by param; positive means highest,
                # negative means lowest)
                elif mode == 'amplitude':
                    d = np.squeeze(data[:, i, j])
                    # convert dates to an index of a timeseries
                    startidx = [find_nearest(timesfloat, s) for s in start]
                    peaksidx = [find_nearest(timesfloat, s) for s in peaks]
                    endidx = [find_nearest(timesfloat, s) for s in end]
                    maxSeason = d[peaksidx]
                    baseSeason = np.average(np.stack((d[startidx],
                                                      d[endidx]), axis=0),
                                            axis=0)
                    amp = maxSeason - baseSeason
                    idx_remove = np.zeros_like(amp)
                    toRemove = npeaks - abs(param)
                    for r in range(toRemove):
                        if param > 0:
                            idx_remove[np.where(amp == np.min(amp))[0][0]] = 1
                            amp[np.where(
                                amp == np.min(amp))[0][0]] = np.max(amp) + 1
                        else:
                            idx_remove[np.where(amp == np.max(amp))[0][0]] = 1
                            amp[np.where(
                                amp == np.max(amp))[0][0]] = np.min(amp) - 1
                    peaks_sel = peaks[idx_remove != 1]
                    start_sel = start[idx_remove != 1]
                    end_sel = end[idx_remove != 1]

                # select x seasons with highest/lowest length
                # (x defined by param; positive means highest,
                # negative means lowest)
                elif mode == 'length':
                    toRemove = npeaks - abs(param)
                    lseason = end - start
                    idx_remove = np.zeros_like(lseason)
                    for r in range(toRemove):
                        if param > 0:
                            idx_remove[np.where(
                                lseason == np.min(lseason))[0][0]] = 1
                            lseason[np.where(
                                lseason == np.min(lseason))[0][0]
                            ] = np.max(lseason) + 1
                        else:
                            idx_remove[np.where(
                                lseason == np.max(lseason))[0][0]] = 1
                            lseason[np.where(
                                lseason == np.max(lseason))[0][0]
                            ] = np.min(lseason) - 1
                    peaks_sel = peaks[idx_remove != 1]
                    start_sel = start[idx_remove != 1]
                    end_sel = end[idx_remove != 1]

                # select all seasons with their peak in a certain year
                elif mode == 'year':
                    peak_times = [datetime.fromtimestamp(p) for p in peaks]
                    peak_years = [x.year for x in peak_times]
                    test_year = [i for i, elem in enumerate(peak_years)
                                 if elem == param]
                    # create selection making sure you end up with same amount
                    # of seasons as was originally in seasons
                    if len(test_year) == 0:
                        peaks_sel = np.ones(nseas, dtype='float32') * -1
                        start_sel = np.ones(nseas, dtype='float32') * -1
                        end_sel = np.ones(nseas, dtype='float32') * -1
                    else:
                        # check how many would be removed from original array
                        ndif = self.sos.shape[0] - len(test_year)
                        start_sel = np.asarray(start[test_year])
                        peaks_sel = np.asarray(peaks[test_year])
                        end_sel = np.asarray(end[test_year])
                        peaks_sel = np.concatenate((peaks_sel,
                                                    np.ones(ndif,
                                                            dtype='float32')
                                                    * -1))
                        start_sel = np.concatenate((start_sel,
                                                    np.ones(ndif,
                                                            dtype='float32')
                                                    * -1))
                        end_sel = np.concatenate((end_sel,
                                                  np.ones(ndif,
                                                          dtype='float32')
                                                  * -1))

                # select season with sos closest to a certain date
                elif mode == 'date':
                    if len(param) != 2:
                        raise ValueError('Param should be a list of 2 '
                                         'elements if mode == date')
                    target = datetime.strptime(param[0], '%Y-%m-%d')
                    target = target.timestamp()
                    idx_sel = find_nearest(start, target)
                    if second_to_day(abs(start[idx_sel] - target)) <= param[1]:
                        peaks_sel = np.array([peaks[idx_sel]])
                        start_sel = np.array([start[idx_sel]])
                        end_sel = np.array([end[idx_sel]])
                    else:
                        peaks_sel = np.array([-1])
                        start_sel = np.array([-1])
                        end_sel = np.array([-1])

                # adjust values according to selection
                sos[:, i, j] = start_sel
                mos[:, i, j] = peaks_sel
                eos[:, i, j] = end_sel
                nseasons[i, j] = np.count_nonzero(peaks_sel != -1)

        return self._clone(nseasons, sos, mos, eos, ts)

    def pheno_mult_season_features(self, resolution):
        '''
        Computes phenological features over multiple seasons.
        Useful to describe seasonality over larger timeframe.
        '''
        features = []

        data = np.squeeze(self.ts.data)
        if data.ndim != 3:
            raise ValueError('Input timeseries should only contain one band!')
        times = np.array([t.timestamp() for t in self.ts.timestamps])

        _, nx, ny = data.shape

        vi = self.ts.bands[0]

        # number of seasons per pixel
        features.append(Features(self.nseasons[:],
                                 [f'{vi}-nSeas-{resolution}m']))

        # minimum, median and maximum length of season(s)
        # compute length of season (in days)
        lSeas = self.eos - self.sos
        lSeas = lSeas / (24 * 3600)
        # convert all zeros to NaN's
        lSeas[lSeas == 0] = np.nan
        # compute features and convert Nan's
        # back to zeros
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            lSeasmin = np.nanmin(lSeas, axis=0)
            lSeasmin[np.isnan(lSeasmin)] = 0
            lSeasmax = np.nanmax(lSeas, axis=0)
            lSeasmax[np.isnan(lSeasmax)] = 0
            lSeasmedian = np.nanmedian(lSeas, axis=0)
            lSeasmedian[np.isnan(lSeasmedian)] = 0
        # add features
        features.append(Features(
            lSeasmin,
            [f'{vi}-lSeasMin-{resolution}m']))
        features.append(Features(
            lSeasmedian,
            [f'{vi}-lSeasMed-{resolution}m']))
        features.append(Features(
            lSeasmax,
            [f'{vi}-lSeasMax-{resolution}m']))

        # minimum, median and maximum amplitude of season(s)
        nz = self.sos.shape[0]
        aSeas = np.zeros((nz, nx, ny))
        for i in range(nx):
            for j in range(ny):
                nseas = self.nseasons[i, j]
                if nseas == 0:
                    continue
                d = np.squeeze(data[:, i, j])
                for ns in range(nseas):
                    # convert dates to an index of a timeseries
                    startidx = find_nearest(times, self.sos[ns, i, j])
                    peaksidx = find_nearest(times, self.mos[ns, i, j])
                    endidx = find_nearest(times, self.eos[ns, i, j])
                    aSeas[ns, i, j] = d[peaksidx] - np.average([d[startidx],
                                                                d[endidx]])
        # convert all zeros to NaN's
        aSeas[aSeas == 0] = np.nan
        # compute features and convert Nan's
        # back to zeros
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            aSeasmin = np.nanmin(aSeas, axis=0)
            aSeasmin[np.isnan(aSeasmin)] = 0
            aSeasmax = np.nanmax(aSeas, axis=0)
            aSeasmax[np.isnan(aSeasmax)] = 0
            aSeasmedian = np.nanmedian(aSeas, axis=0)
            aSeasmedian[np.isnan(aSeasmedian)] = 0
        # add features
        features.append(Features(
            aSeasmin,
            [f'{vi}-aSeasMin-{resolution}m']))
        features.append(Features(
            aSeasmedian,
            [f'{vi}-aSeasMed-{resolution}m']))
        features.append(Features(
            aSeasmax,
            [f'{vi}-aSeasMax-{resolution}m']))

        features = Features.from_features(*features)
        return features

    def pheno_single_season_features(self,
                                     sel_mode,
                                     sel_param,
                                     resolution,
                                     ts=None):
        '''
        Computes a list of pheno features for one particular season
        The season is selected based on the criteria in feat_meta.
        The features are by default computed on the timeseries provided
        in the seasons object, but an optional timeseries can be provided
        as well...
        '''

        # first, select the appropriate season
        sel_season = self.select(sel_mode, sel_param)

        # prepare output
        features = []
        nx = sel_season.nseasons.shape[0]
        ny = sel_season.nseasons.shape[1]

        # first get some feature purely related to timing
        # (day of year and length of season):
        sos = np.zeros((nx, ny))  # sos in day of year
        eos = np.zeros((nx, ny))  # eos in day of year
        mos = np.zeros((nx, ny))  # peak of season in day of year
        for i in range(nx):
            for j in range(ny):
                nseas = sel_season.nseasons[i, j]
                if nseas == 0:
                    continue
                sos[i, j] = datetime.fromtimestamp(
                    sel_season.sos[0, i, j]).timetuple().tm_yday
                eos[i, j] = datetime.fromtimestamp(
                    sel_season.eos[0, i, j]).timetuple().tm_yday
                mos[i, j] = datetime.fromtimestamp(
                    sel_season.mos[0, i, j]).timetuple().tm_yday

        # length of season in days
        los = (sel_season.eos[0, :, :] - sel_season.sos[0, :, :]) / (24*3600)
        # time to peak in days
        ttp = (sel_season.mos[0, :, :] - sel_season.sos[0, :, :]) / (24*3600)
        # time of decline in days
        tod = (sel_season.eos[0, :, :] - sel_season.mos[0, :, :]) / (24*3600)

        vi = self.ts.bands[0]

        # add to features
        features.append(Features(sos, [f'{vi}-phenoSOS-{resolution}m']))
        features.append(Features(eos, [f'{vi}-phenoEOS-{resolution}m']))
        features.append(Features(mos, [f'{vi}-phenoMOS-{resolution}m']))
        features.append(Features(los, [f'{vi}-phenoLOS-{resolution}m']))
        features.append(Features(ttp, [f'{vi}-phenoTTP-{resolution}m']))
        features.append(Features(tod, [f'{vi}-phenoTOD-{resolution}m']))

        # now calculate some features related to amplitude of the timeseries:
        # loop over all bands in the input timeseries
        if ts is None:
            ts = self.ts
        times = np.array([t.timestamp() for t in ts.timestamps])
        bands = ts.bands
        for b in bands:
            data = np.squeeze(ts.select_bands([b]).data)

            # prepare outputs
            phenoAmp = np.zeros((nx, ny))
            phenoBase = np.zeros((nx, ny))
            phenoMax = np.zeros((nx, ny))
            phenoArea = np.zeros((nx, ny))
            phenoSGU = np.zeros((nx, ny))
            phenoMGU = np.zeros((nx, ny))
            phenoMAT = np.zeros((nx, ny))
            phenoSGD = np.zeros((nx, ny))
            phenoMGD = np.zeros((nx, ny))
            phenoDOR = np.zeros((nx, ny))
            for i in range(nx):
                for j in range(ny):
                    nseas = sel_season.nseasons[i, j]
                    if nseas == 0:
                        continue
                    d = np.squeeze(data[:, i, j])
                    # convert dates to an index of a timeseries
                    startidx = find_nearest(times, sel_season.sos[0, i, j])
                    peaksidx = find_nearest(times, sel_season.mos[0, i, j])
                    endidx = find_nearest(times, sel_season.eos[0, i, j])
                    # compute basevalue, max value, amplitude and area under
                    # curve for each pixel
                    phenoMax[i, j] = d[peaksidx]
                    phenoBase[i, j] = np.average([d[startidx], d[endidx]])
                    phenoAmp[i, j] = phenoMax[i, j] - phenoBase[i, j]
                    phenoArea[i, j] = np.sum(d[startidx: endidx])
                    # identify timing of phenological stages:
                    # cut out first half of the season
                    d2 = np.squeeze(d[startidx: peaksidx]) - phenoBase[i, j]
                    t = times[startidx: peaksidx]
                    # timing of green-up phases
                    idx = np.where(d2 > 0.15 * phenoAmp[i, j])
                    if idx[0].shape[0] > 0:
                        phenoSGU[i, j] = datetime.fromtimestamp(
                            t[idx[0][0]]).timetuple().tm_yday
                    idx = np.where(d2 > 0.50 * phenoAmp[i, j])
                    if idx[0].shape[0] > 0:
                        phenoMGU[i, j] = datetime.fromtimestamp(
                            t[idx[0][0]]).timetuple().tm_yday
                    idx = np.where(d2 > 0.90 * phenoAmp[i, j])
                    if idx[0].shape[0] > 0:
                        phenoMAT[i, j] = datetime.fromtimestamp(
                            t[idx[0][0]]).timetuple().tm_yday
                    # cut out second half of the season
                    d2 = np.squeeze(d[peaksidx: endidx]) - phenoBase[i, j]
                    t = times[peaksidx: endidx]
                    # timing of green-down phases
                    idx = np.where(d2 < 0.90 * phenoAmp[i, j])
                    if idx[0].shape[0] > 0:
                        phenoSGD[i, j] = datetime.fromtimestamp(
                            t[idx[0][0]]).timetuple().tm_yday
                    idx = np.where(d2 < 0.50 * phenoAmp[i, j])
                    if idx[0].shape[0] > 0:
                        phenoMGD[i, j] = datetime.fromtimestamp(
                            t[idx[0][0]]).timetuple().tm_yday
                    idx = np.where(d2 < 0.15 * phenoAmp[i, j])
                    if idx[0].shape[0] > 0:
                        phenoDOR[i, j] = datetime.fromtimestamp(
                            t[idx[0][0]]).timetuple().tm_yday

            # add to features
            features.append(Features(phenoBase,
                                     [f'{b}-phenoBase-{resolution}m']))
            features.append(Features(phenoAmp,
                                     [f'{b}-phenoAmp-{resolution}m']))
            features.append(Features(phenoMax,
                                     [f'{b}-phenoMax-{resolution}m']))
            features.append(Features(phenoArea,
                                     [f'{b}-phenoArea-{resolution}m']))
            features.append(Features(phenoSGU,
                                     [f'{b}-phenoSGU-{resolution}m']))
            features.append(Features(phenoMGU,
                                     [f'{b}-phenoMGU-{resolution}m']))
            features.append(Features(phenoMAT,
                                     [f'{b}-phenoMAT-{resolution}m']))
            features.append(Features(phenoSGD,
                                     [f'{b}-phenoSGD-{resolution}m']))
            features.append(Features(phenoMGD,
                                     [f'{b}-phenoMGD-{resolution}m']))
            features.append(Features(phenoDOR,
                                     [f'{b}-phenoDOR-{resolution}m']))

        features = Features.from_features(*features)
        return features
