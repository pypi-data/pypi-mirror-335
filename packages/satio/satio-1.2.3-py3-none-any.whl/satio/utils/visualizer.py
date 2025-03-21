import warnings
import ipywidgets as widgets
from IPython.display import display
import os
import sys
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.backend_bases import KeyEvent
from matplotlib.colors import Normalize
from matplotlib import cm
from matplotlib.dates import date2num


class Click:
    """
    Handles clicks of the mouse on the different axes.
    Also controls that it is a single click and not a drag and release which
    is used to zoom and would instead trigger an action without this control
    """

    def __init__(self, visualizer, select_buttons=[1, 't'], debug=False):
        self.vis = visualizer
        self.select_buttons = select_buttons

        self.press = False
        self.move = False

        self._debug = debug

        events_connections = {'button_press_event': self.onpress,
                              'button_release_event': self.onrelease,
                              'motion_notify_event': self.onmove,
                              'scroll_event': self.onscroll,
                              'key_press_event': self.onclick}

        self._mpl_connections = [self.vis.fig.canvas.mpl_connect(k, f) for
                                 k, f in events_connections.items()]

    def onclick(self, event):
        if isinstance(event, KeyEvent):
            button = event.key
        else:
            button = event.button

        if button == 'r':
            self.vis.reset_zoom()
        elif button == 'y':
            self.vis._toggle_mask()
        elif button in self.select_buttons:
            if event.inaxes == self.vis.axs[0]:
                self.vis.select_pixel(event)
            elif event.inaxes == self.vis.axs[1]:
                self.vis.select_slice(event)

    def onscroll(self, event):
        if event.inaxes == self.vis.axs[1]:
            self.vis.slicetime(event)

        elif event.inaxes == self.vis.axs[0]:
            self.vis.zoom(event)

    def onpress(self, event):
        self.press = True

    def onmove(self, event):
        if self.press:
            self.move = True

    def onrelease(self, event):
        if self.press and not self.move:
            self.onclick(event)
        self.press = False
        self.move = False


class Visualizer:
    """
    TODO: Add RGB support, change band orders to work easy with collections
    Visualizer tool for images timeseries in Matplotlib.
    Enables to select one pixel of the image to display the time series through
    it, or select a point of the time series to display the image in that date
    """

    def __init__(self, arr, time_vector=None, mask=None,
                 vmin=None, vmax=None,
                 select_buttons=[1, 't'], debug=False,
                 rgb_indices=[0, 1, 2], bands_labels=None,
                 **figure_options):
        """
        Initialize tool by providing the datacube 'arr' and the order of
        dimensions if different from [x, y, time], e.g. if the datacube has
        [time, x, y] dimensions, provide dimensions_order=[2, 0, 1] as
        parameter to transpose the data in the correct form.
        """
        if (vmin is None) | (vmax is None):
            p = np.nanpercentile(arr, [10, 80])
            vmin = vmin if vmin is not None else p[0]
            vmax = vmax if vmax is not None else p[1]

        self.data = self._prepare_input(arr, rgb_indices, vmax)
        self.mask = self._prepare_mask(mask)
        self._mask_active = False
        # handling indices of displayed images, skipping empty layers
        not_empty = np.nansum(np.array(
            np.squeeze(self.data[:, :, 0, :])), (0, 1)) != 0

        if np.all(~not_empty):
            raise ValueError("Check input, all data is NaNs or 0...")
        self._indices = np.array([i for i, v in enumerate(not_empty) if v])
        self._ind_pos = int(len(self._indices)/2)
        self._ind = self._indices[self._ind_pos]

        self.px, self.py = int(self.data.shape[1]/2), int(self.data.shape[0]/2)
        self.time_vector = (time_vector if time_vector is not None
                            else list(range(self.data.shape[3])))

        self.fig, self.axs = plt.subplots(1, 2, **figure_options)
        self.fig.canvas.capture_scroll = True

        self._click_handler = Click(self, select_buttons=select_buttons,
                                    debug=debug)

        # scaling and axes limits for left figure
        self._norm = Normalize(vmin=vmin, vmax=vmax, clip=True)
        self._vmax = vmax
        self._left_xlim = [0 - 0.5, self.data.shape[1] - 0.5]
        self._left_ylim = [self.data.shape[0] - 0.5, 0 - 0.5]
        self._right_xlim = None  # set on first draw
        self._right_ylim = (np.nanmin(self.data),
                            np.nanpercentile(self.data, 99)*1.1)
        self._right_aspect_ratio = None  # set on first draw
        # color palette for time series
        self._colors = cm.rainbow(np.linspace(0, 1, self.data.shape[2]))
        self.bands_labels = (bands_labels if bands_labels is not None
                             else [str(i) for i in range(self.data.shape[2])])

        self._gamma_value = 1/2.2

        with warnings.catch_warnings():
            self.draw()
            plt.show()

        @widgets.interact(timestamp=(0, len(self._indices) - 1, 1))
        def slider_time(timestamp):
            self.ind_pos = timestamp
            self.draw()

        @widgets.interact(zoom_factor=(1, self.data.shape[1] // 2, 0.2))
        def slider_zoom(zoom_factor=1):
            ax = self.axs[0]
            position = (self.px, self.py)
            self._cur_xlim = cur_xlim = ax.get_xlim()
            self._cur_ylim = cur_ylim = ax.get_ylim()

            cur_xlim = [0 - 0.5, self.data.shape[1] - 0.5]
            cur_ylim = [0 - 0.5, self.data.shape[0] - 0.5]
            cur_xrange = (cur_xlim[1] - cur_xlim[0])*.5
            cur_yrange = (cur_ylim[1] - cur_ylim[0])*.5

            xdata, ydata = position  # get event x, y location

            scaling_factor = 1 / zoom_factor

            # set new limits
            self._left_xlim = [xdata - cur_xrange * scaling_factor,
                               xdata + cur_xrange * scaling_factor]
            self._left_ylim = [ydata + cur_yrange * scaling_factor,
                               ydata - cur_yrange * scaling_factor]

            ax.set_xlim(self._left_xlim)
            ax.set_ylim(self._left_ylim)
            plt.draw()  # force re-draw

        @widgets.interact(gamma_value=(0.01, 4, 0.1))
        def slider_gamma(gamma_value=1.5):
            self._gamma_value = gamma_value
            self.draw()

    @property
    def ind(self):
        return self._ind

    @ind.setter
    def ind(self, value):
        self._ind_pos = np.argmin(np.abs(self._indices - value))
        self._ind = self._indices[self._ind_pos]

    @property
    def ind_pos(self):
        return self._ind_pos

    @ind_pos.setter
    def ind_pos(self, value):
        if value < 0:
            self._ind_pos = 0
        elif value >= len(self._indices):
            self._ind_pos = len(self._indices) - 1
        else:
            self._ind_pos = value

        self.ind = self._indices[self._ind_pos]

    @property
    def tseries(self):
        """Time series for given pixel"""
        data = self.data[self.py, self.px, :, :]
        return data

    @property
    def rect(self):
        """Rectangular patch to draw around selected image pixel"""
        self._rect = patches.Rectangle((self.px - 0.5, self.py - 0.5), 1, 1,
                                       linewidth=3, edgecolor='r',
                                       facecolor='none')
        return self._rect

    def _prepare_input(self, arr, rgb_indices, vmax):
        """
        arr should have shape (bands, time, px, py)
        if a single band is loaded with shape (time, px, py)
        this expands the array adding a singleton dimension
        """
        if isinstance(arr, list):
            arr = np.array(arr)
        if len(arr.shape) == 3:
            arr = arr[np.newaxis, ...]
            self._rgb_indices = [0]
        else:
            self._rgb_indices = rgb_indices
            # handle case in which only two bands are given
            if arr.shape[0] == 2:
                arr[2, :, :, :] = np.zeros(1,
                                           arr.shape[1],
                                           arr.shape[2],
                                           arr.shape[3])

        arr = np.transpose(arr, [2, 3, 0, 1]) / vmax

        return arr

    def _prepare_mask(self, mask):
        mask = np.transpose(mask, [1, 2, 0]) if mask is not None else None
        return mask

    def _toggle_mask(self):
        if self.mask is not None:
            self._mask_active = not self._mask_active
            self.draw()

    def _gamma_corr(self, data):
        return data ** (1 / self._gamma_value)

    def _draw_left(self):
        """Draw the left canvas"""
        axs = self.axs
        data = np.squeeze(self.data[:, :, self._rgb_indices, self.ind])

        data = self._gamma_corr(data)

        if self._mask_active:
            mask = self.mask[:, :, self.ind]
            if len(data.shape) == 3:
                mask = mask[..., np.newaxis]
            mask = np.broadcast_to(mask, data.shape)
            data[mask] = np.nan
        axs[0].clear()
        # axs[0].imshow(np.squeeze(self.data[:, :,
        # self._rgb_indices, self.ind]),
        #               norm=self._norm)
        axs[0].imshow(data)
        axs[0].add_patch(self.rect)
        axs[0].set_xlim(self._left_xlim)
        axs[0].set_ylim(self._left_ylim)

    def _draw_right(self):
        """Draw the right canvas"""
        axs = self.axs
        axs[1].clear()
        plt.xticks(rotation=70)

        if self._mask_active:
            mask = np.squeeze(self.mask[self.py, self.px, :])

        for i, c in enumerate(self._colors):
            tseries = np.squeeze(self.tseries[i, :].copy())
            if self._mask_active:
                tseries[mask] = np.nan  # type: ignore
            axs[1].plot(self.time_vector, tseries,
                        marker='o', linestyle='-', color=c,
                        label=self.bands_labels[i],
                        alpha=0.5)
        # axs[1].plot(self.time_vector[self.ind], self.tseries[self.ind], 'ob')
        axs[1].axvline(self.time_vector[self.ind], color='r')
        axs[1].legend(loc='center left',
                      bbox_to_anchor=(1, 0.5),
                      fontsize='x-small')

        if not self._right_xlim:
            self._right_xlim = axs[1].get_xlim()
        # axs[1].set_xlim(self.time_vector[0], self.time_vector[-1])
        axs[1].set_xlim(self._right_xlim)
        axs[1].set_ylim(self._right_ylim)

        if not self._right_aspect_ratio:
            ratio = ((self._right_ylim[1] - self._right_ylim[0])
                     / (self._right_xlim[1] - self._right_xlim[0]))
            # ratio = axs[1].get_data_ratio()
            self._right_aspect_ratio = 1/ratio
        axs[1].set_aspect(self._right_aspect_ratio)  # make plot a square
        axs[1].set_title(self.time_vector[self.ind])

    def draw(self, left=True, right=True):
        if left:
            self._draw_left()
        if right:
            self._draw_right()
        mask_legend = "'Y' to apply mask\n" if self.mask is not None else ""
        plt.text(0, 0,
                 "'T' to select a point\n"
                 "'R' to reset zoom\n"
                 + mask_legend,
                 fontsize=10, transform=plt.gcf().transFigure)
        plt.draw()

    def update_rect(self):
        """Update only the rectangle patch around the pixel. (Keeps zoom
        instead of redrawing whole axes which resets everything)
        """
        self._rect.remove()
        self.axs[0].add_patch(self.rect)

    def select_pixel(self, event):
        """
        Actions performed when clicking the image to select a pixel from
        which the timeseries is extracted
        """
        self.px, self.py = (int(np.round(event.xdata)),
                            int(np.round(event.ydata)))
        self.update_rect()
        self.draw()

    def select_slice(self, event):
        """
        Actions to perform when selecting a point in the right axes, in order
        to view the corresponding image at the selected date.
        """
        if type(self.time_vector[0]) in [datetime, np.datetime64]:
            time_vector = date2num(self.time_vector)
        else:
            time_vector = self.time_vector

        tseries = self.tseries[:, :]
        distance_x = (time_vector - event.xdata)**2 / time_vector.max()
        distance_y = (tseries - event.ydata)**2 / np.nanmax(tseries)
        distance = (np.broadcast_to(distance_x, distance_y.shape)
                    + distance_y) ** 0.5

        self.ind = np.unravel_index(np.nanargmin(distance), distance.shape)[1]
        self.draw()

    def slicetime(self, event):
        if event.button == 'up':
            self.ind_pos = self.ind_pos + 1
            self.draw()
        elif event.button == 'down':
            self.ind_pos = self.ind_pos - 1
            self.draw()

    def zoom(self, event, base_scale=1.2):
        ax = self.axs[0]
        position = (self.px, self.py)
        self._cur_xlim = cur_xlim = ax.get_xlim()
        self._cur_ylim = cur_ylim = ax.get_ylim()
        cur_xrange = (cur_xlim[1] - cur_xlim[0])*.5
        cur_yrange = (cur_ylim[0] - cur_ylim[1])*.5
        if position is None:
            position = event.xdata, event.ydata
        xdata, ydata = position  # get event x, y location

        if event.button == 'up':
            # deal with zoom in
            scale_factor = 1/base_scale
        elif event.button == 'down':
            # deal with zoom out
            scale_factor = base_scale
        else:
            # deal with something that should never happen
            scale_factor = 1

        # set new limits
        self._left_xlim = [xdata - cur_xrange*scale_factor,
                           xdata + cur_xrange*scale_factor]
        self._left_ylim = [ydata + cur_yrange*scale_factor,
                           ydata - cur_yrange*scale_factor]
        ax.set_xlim(self._left_xlim)
        ax.set_ylim(self._left_ylim)
        plt.draw()  # force re-draw

    def reset_zoom(self):
        ax = self.axs[0]
        self._left_xlim = [0 - 0.5, self.data.shape[1] - 0.5]
        self._left_ylim = [self.data.shape[0] - 0.5, 0 - 0.5]
        ax.set_xlim(self._left_xlim)
        ax.set_ylim(self._left_ylim)
        plt.draw()


def zoom(event, ax, position=None, base_scale=1.2):
    # get the current x and y limits
    cur_xlim = ax.get_xlim()
    cur_ylim = ax.get_ylim()
    cur_xrange = (cur_xlim[1] - cur_xlim[0])*.5
    cur_yrange = (cur_ylim[1] - cur_ylim[0])*.5
    if position is None:
        position = event.xdata, event.ydata
    xdata, ydata = position  # get event x, y location

    if event.button == 'up':
        # deal with zoom in
        scale_factor = 1/base_scale
    elif event.button == 'down':
        # deal with zoom out
        scale_factor = base_scale
    else:
        # deal with something that should never happen
        scale_factor = 1

    # set new limits
    ax.set_xlim([xdata - cur_xrange*scale_factor,
                 xdata + cur_xrange*scale_factor])
    ax.set_ylim([ydata + cur_yrange*scale_factor,
                 ydata - cur_yrange*scale_factor])
    plt.draw()  # force re-draw


def get_time_vector(n):
    """
    Get random time vector for testing purpose
    """
    v = [0]
    for i in range(1, n):
        v.append(v[i - 1] + np.random.randint(1, 5))
    return np.array(v)


class ImViewer:

    def __init__(self, *arrs, max_cols=3, titles=None, vmins=None, vmaxs=None):

        self.idx = 0
        self.n_ids = arrs[0].shape[0]
        self.arrs = arrs

        rows, cols = self._get_rows_cols(max_cols)
        self.fig, self.axs = plt.subplots(rows, cols, sharex=True, sharey=True)

        if len(arrs) == 1:
            self.axs = np.array([self.axs])

        self.vmins = vmins
        self.vmaxs = vmaxs

        self.titles = titles

        button_prev = widgets.Button(description="Prev")  # type: ignore
        button_next = widgets.Button(description="Next")  # type: ignore

        display(button_prev, button_next)

        def click_prev(b):
            self.idx = max(0, self.idx - 1)
            self.show()

        def click_next(b):
            self.idx = min(self.idx + 1, self.n_ids - 1)
            self.show()

        button_prev.on_click(click_prev)
        button_next.on_click(click_next)

        self.show()

    def _get_rows_cols(self, max_cols):
        n_arrs = len(self.arrs)
        if n_arrs <= max_cols:
            cols = n_arrs
            rows = 1
        else:
            cols = max_cols
            rows = (n_arrs // max_cols) + 1

        return rows, cols

    def show(self):
        ims = [arr[self.idx, ...] for arr in self.arrs]
        self.imshow(self.axs.flatten(),
                    *ims,
                    vmins=self.vmins,
                    vmaxs=self.vmaxs,
                    title=self.titles[self.idx])

    @staticmethod
    def imshow(axs, *ims, vmins, vmaxs, title):

        if vmins is None:
            vmins = [None for i in range(len(ims))]

        if vmaxs is None:
            vmaxs = [None for i in range(len(ims))]

        for im, ax, vmin, vmax in zip(ims,
                                      axs[:len(ims)],
                                      vmins,
                                      vmaxs):

            ax.imshow(im, vmin=vmin, vmax=vmax)

        ax.set_title(title)  # type: ignore


def test_visualizer_single_random(mask=True):
    """Test the visualizer interactions manually"""
    n = 50
    arr = np.random.rand(n, 400, 400) * 6000
    time_vector = get_time_vector(arr.shape[0])
    mask = np.random.rand(n, 400, 400) > 0.8 if mask else None

    Visualizer(arr, time_vector, mask=mask, figsize=(15, 8))


def test_visualizer(mode='single', mask=True, **options):
    """ 'mode' should be 'single' or 'multi' """
    # scp mep2:/data/sentinel_data/swap/timeseries_* /home/dzanaga/repos/data
    data_folder = "/home/dzanaga/repos/sentinel-preprocessing/data"
    # data_folder = "/data/sentinel_data/swap"
    arr = np.load(os.path.join(
        data_folder, f"timeseries_visualizer_test_{mode}_band2.npy"))
    time_vector = np.load(os.path.join(
        data_folder, "timeseries_visualizer_test_multi_band2_tv.npy"))

    if mask:
        mask = np.load(os.path.join(
            data_folder, "timeseries_visualizer_test_single_band_mask.npy"))
    else:
        mask = None

    Visualizer(arr, time_vector, mask=mask, **options, figsize=(15, 8))


if __name__ == '__main__':
    if '-m' in sys.argv:
        mask = True
    else:
        mask = False

    if '-s' in sys.argv:
        test_visualizer(mode='single', mask=mask)
    else:
        test_visualizer(mode='multi', mask=mask, rgb_indices=[0, 1, 2],
                        bands_labels=['B04', 'B03', 'B02', 'B06'])
