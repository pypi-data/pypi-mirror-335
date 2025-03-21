"""
Imports from satio.utils.resample were moved inside the functions requiring
them as it takes 1s for compiling the numba functions. This speeds up import
time when those functions are not needed
"""
from typing import List, Tuple
from abc import ABC, abstractmethod, abstractproperty

import joblib
import numpy as np
import pandas as pd
import geopandas as gpd
import scipy
from scipy.fftpack import rfft
from scipy.stats import kurtosis, skew
from loguru import logger
from shapely.geometry import Point
from rasterio.crs import CRS
from skimage.transform import resize
from skimage.morphology import footprints, binary_erosion, binary_dilation
from sklearn.decomposition import PCA

import satio
from satio.rsindices import RSI_META
from satio.utils import rasterize, dem_attrs, TaskTimer
from satio.utils.geotiff import get_rasterio_profile, write_geotiff
from satio.utils.speckle import mtfilter

L2A_BANDS_10M = ['B02', 'B03', 'B04', 'B08']
L2A_BANDS_20M = ['B05', 'B06', 'B07', 'B8A', 'B11', 'B12', 'SCL',
                 'sunAzimuthAngles', 'sunZenithAngles',
                 'viewAzimuthMean', 'viewZenithMean']
L2A_BANDS_DICT = {10: L2A_BANDS_10M,
                  20: L2A_BANDS_20M}
SCL_MASK_VALUES = [0, 1, 3, 8, 9, 10, 11]

GAMMA_BANDS_DICT = {20: ['VV', 'VH']}

AGERA5_BANDS_DICT = {
    1000: [
        'dewpoint_temperature', 'precipitation_flux',
        'solar_radiation_flux', 'temperature_max',
        'temperature_mean', 'temperature_min',
        'vapour_pressure', 'wind_speed'
    ]
}


class Features:

    def __init__(self,
                 data: np.ndarray,
                 names: List,
                 dtype: type = np.float32,
                 attrs: dict = dict()):

        if not isinstance(names, List):
            raise TypeError("`names` should be a list.")

        if data.ndim == 2:
            data = np.expand_dims(data, axis=0)

        if data.shape[0] != len(names):
            raise ValueError('axis 0 of `data` should be equal to '
                             'the length of `names`. Instead arr.shape = '
                             f'{data.shape} and len(names) = {len(names)}.')

        if data.dtype != dtype:
            self.data = data.astype(dtype)
        else:
            self.data = data

        self.names = names
        self.attrs = attrs
        self._df = None

    def _clone(self,
               data: np.ndarray = None,
               names: List = None,
               dtype: type = None,
               attrs: dict = None):

        data = self.data if data is None else data
        names = self.names if names is None else names
        dtype = self.data.dtype if dtype is None else dtype
        attrs = self.attrs if attrs is None else attrs

        return self.__class__(data, names, dtype, attrs)

    def get_feature_index(self, feature_name):
        return self.names.index(feature_name)

    def __getitem__(self, feature_name):
        idx = self.get_feature_index(feature_name)
        return self.data[idx]

    def __setitem__(self, feature_name, value):

        if np.isscalar(value):
            value = np.ones(self.shape[-2:]) * value

        if feature_name not in self.names:
            if value.shape[-2:] != self.data.shape[-2:]:
                raise ValueError("`value` should have the same shape "
                                 "of `self.data` on the last two axis.")
            new_feat = self._clone(value, [feature_name])
            self = self.merge(new_feat)

        else:
            idx = self.get_feature_index(feature_name)
            self.data[idx] = value

    def drop(self, *features_names):
        indices = [self.get_feature_index(f) for f in features_names]
        new_data = np.delete(self.data, indices, axis=0)
        new_names = [f for f in self.names if f not in features_names]
        return self._clone(new_data, new_names)

    @property
    def df(self):
        if self._df is None:
            self._df = self._arr_to_df()
        else:
            # If needed add attrs to df
            for key, value in self.attrs.items():
                if key not in self._df.columns:
                    self._df[key] = value
        return self._df

    @property
    def shape(self):
        return self.data.shape

    @df.setter
    def df(self, value):
        if isinstance(value, pd.DataFrame):
            self._df = value
        else:
            raise TypeError("Trying to set a non DataFrame type to `df`. "
                            f"type(value) = {type(value)}")

    def _arr_to_df(self):
        features_arr, features_names = self.data, self.names
        features_df = pd.DataFrame(
            features_arr.reshape(features_arr.shape[0],
                                 features_arr.shape[1] *
                                 features_arr.shape[2]).T,
            columns=features_names)

        # Convert attributes to columns
        for key, value in self.attrs.items():
            features_df[key] = value

        return features_df

    def downsample_categorical(self) -> 'Features':
        """
        Downsample categorical feature in the space dimensions.
        Based on majority vote within each 2x2 pixel window

        """
        from scipy.stats import mode

        old_data = self.data
        new_shape = (old_data.shape[0],
                     int(round(old_data.shape[1] / 2)),
                     int(round(old_data.shape[2] / 2)))

        new_data = np.empty(new_shape)
        for b in range(new_data.shape[0]):
            x = 0
            for i in range(new_data.shape[1]):
                y = 0
                for j in range(new_data.shape[2]):
                    new_data[b, i, j] = mode(old_data[b, x:x+2, y:y+2], axis=None).mode[0]
                    y += 2
                x += 2

        return self._clone(new_data, self.names)  # type: ignore

    def upsample(self, order=1, times=1, scaling=None) -> 'Features':
        """
        Upsamples Features in the space dimensions

        If order is 0: usese numba upsample implementation, doubles the
        resolution using 'nearest_neighbors' n 'times'. Ignores the 'scaling'
        parameter.

        If order is > 0: uses skimage.transform.rescale on every band
        (casting to float32 each time as rescale returns float64)
        If scaling is specified it will use that to determine the new shape,
        otherwise it will default to '2 ** times'.

        Order can be:
        0: Nearest-neighbor (usese numba custom, ignores scaling)
        1: Bi-linear (default)
        2: Bi-quadratic
        3: Bi-cubic
        4: Bi-quartic
        5: Bi-quintic

        """
        from satio.utils.resample import imresize, upsample

        old_data = self.data

        if order == 0:
            for t in range(times):
                new_data = upsample(old_data)
                old_data = new_data
        else:
            scaling = scaling or (2 ** times)

            new_shape = (old_data.shape[0],
                         int(round(old_data.shape[1] * scaling)),
                         int(round(old_data.shape[2] * scaling)))

            new_data = np.empty(new_shape)
            for i in range(new_data.shape[0]):
                new_data[i, ...] = imresize(old_data[i],
                                            shape=new_shape[1:],
                                            order=order)

        return self._clone(new_data, self.names)  # type: ignore

    def resize(self, scaling, order=1, anti_aliasing=True) -> 'Features':
        """
        Resize Features in the space dimensions

        Order can be:
        0: Nearest-neighbor
        1: Bi-linear (default)
        2: Bi-quadratic
        3: Bi-cubic
        4: Bi-quartic
        5: Bi-quintic

        """
        from satio.utils.resample import imresize

        old_data = self.data

        new_shape = (old_data.shape[0],
                     int(round(old_data.shape[1] * scaling)),
                     int(round(old_data.shape[2] * scaling)))

        new_data = np.empty(new_shape)
        for i in range(new_data.shape[0]):
            new_data[i, ...] = imresize(old_data[i],
                                        shape=new_shape[1:],
                                        order=order,
                                        anti_aliasing=anti_aliasing)

        return self._clone(new_data, self.names)

    def pca(self, num_components, scaling_range=None):
        """
        Calculates principal components from a set of features
        :param features -> numpy array of features
        :param num_components -> number of PC components to retain
        :param scaling_range -> provides minimum and maximum of each feature
        for normalization. Should be a dict with the names of the features
        as keys and [min, max] as value.
        Features not included in the dict won't be normalized.
        """
        # prepare the data
        newdata = self.data.copy()
        nfeat = newdata.shape[0]
        lenx = newdata.shape[1]
        leny = newdata.shape[2]

        # normalize data if needed
        if scaling_range is not None:
            for k, v in scaling_range.items():
                idx = self.get_feature_index(k)
                newdata[idx, :, :] = ((self.data[idx, :, :] - v[0]) /
                                      (v[1] - v[0]))

        # convert data to 2d
        data_2d = newdata.transpose(1, 2, 0).reshape(lenx * leny, nfeat)

        # apply pca and retain n components
        pca = PCA(n_components=num_components)
        pcs_2d = pca.fit_transform(data_2d)

        # reshape to shape required by features
        pcs = pcs_2d.reshape(lenx, leny, num_components).transpose(2, 0, 1)
        pcs = np.asarray(pcs, dtype=np.float32)
        pc_names = ["PC{}".format(x) for x in range(1, num_components+1)]

        return self.__class__(pcs, pc_names)

    def texture(self, win=2, d=[1], theta=[0, np.pi/4],
                levels=256, metrics=('contrast',), avg=True,
                scaling_range={}):

        from satio.utils.texture import haralick_features

        features = []
        # process each input feature separately
        data = self.data.copy()
        for fname in self.names:
            idx = self.get_feature_index(fname)
            img = data[idx, :, :]
            # normalize data and transform to byte
            if fname in scaling_range.keys():
                # use scaling range provided
                srange = scaling_range[fname]
                # make sure all values in img fall in this range
                img[img < srange[0]] = srange[0]
                img[img > srange[1]] = srange[1]
            else:
                # calculate minimum and maximum to be used for scaling
                srange = [np.nanmin(img), np.nanmax(img)]

            # texture not able to deal with nan's
            idxnan = np.argwhere(np.isnan(img))
            if np.isnan(srange[0]):
                # all values in img are nan -> skipping this!
                continue
            else:
                img[idxnan] = srange[0]
            img = (img - srange[0]) / (srange[1] - srange[0]) * (levels - 1)
            img = img.astype('uint32')

            text_features, feature_names = haralick_features(
                img, fname, win=win, d=d, theta=theta,
                levels=levels, metrics=metrics, avg=avg)

            if idxnan.size > 0:
                text_features[:, idxnan[:, 0], idxnan[:, 1]] = np.nan
            features.append(self.__class__(text_features, feature_names))

        if len(features) > 1:
            features = self.__class__.from_features(*features)
        elif len(features) == 1:
            features = features[0]

        return features

    def select(self, features_names, fill_value=None):

        features_names_valid = [f for f in features_names if f in self.names]
        features_names_invalid = [f for f in features_names
                                  if f not in self.names]

        if len(features_names_valid) == 0:

            if fill_value is not None:
                logger.warning("No valid features selected, returning "
                               f"constant features of value: {fill_value}")
                new_names = features_names
                new_shape = (len(features_names),
                             self.data.shape[1],
                             self.data.shape[2])
                new_data = np.ones(new_shape) * fill_value
                return self._clone(new_data, new_names)
            else:
                raise ValueError("No valid features selected")

        new_idxs = [self.names.index(f) for f in features_names_valid]
        try:
            new_data = self.data[new_idxs]
        except IndexError:
            # Temporary workaround for zarr features
            new_data = self.data.get_orthogonal_selection(new_idxs)

        if len(features_names_invalid):

            if fill_value is None:
                raise ValueError(f"Features {features_names_invalid} "
                                 "are not in the data.")
            else:
                logger.warning(f"Features {features_names_invalid} not in "
                               "data, replacing with "
                               f"constant features of value: {fill_value}")
                invalid_idxs = [features_names.index(f) for f in
                                features_names_invalid]
                for idx in invalid_idxs:
                    new_data = np.insert(new_data, idx, fill_value, axis=0)

        return self._clone(new_data, features_names)

    def merge(self, *others):
        """
        Returns a new instance merging data and names of current feature with
        multiple features.
        """
        new_names = self.names.copy()
        new_data = [self.data]

        for other in others:

            common_names = set(other.names) & set(self.names)
            if len(common_names) > 0:
                raise ValueError(f"Feature name: {common_names} "
                                 "already present. Cannot merge 'other'.")

            new_data.append(other.data)
            new_names.extend(other.names)

        new_data = np.concatenate(
            new_data,
            axis=0)

        return self._clone(new_data, new_names)

    def add(self,
            data: np.array,
            names: List):
        """
        Add an array with 1 or more features to the features stack
        """
        return self.merge(self.__class__(data, names))

    def add_constant(self,
                     constant_value,
                     constant_name):
        """
        Add a constant feature to the features array
        """
        if type(constant_value) is str:
            raise ValueError('`constant_value` should be numeric!')
        new_feat_arr = np.ones(self.shape[-2:]) * constant_value

        return self.merge(
            self._clone(new_feat_arr,
                        [constant_name]))

    def add_attribute(self,
                      attr_value,
                      attr_name):
        """
        Add an attribute to the features
        """
        new_attrs = self.attrs.copy()

        new_attrs[attr_name] = attr_value

        return self._clone(attrs=new_attrs)

    def cache_to_zarr(self,
                      filename=None,
                      chunks=(512, 512)):
        # Experimental Zarr caching
        import zarr
        from satio.utils import random_string

        if filename is None:
            filename = f'satio_features_{random_string(8)}.zarr'

        logger.info(f'Caching features to zarr: {filename}')
        z = zarr.open(filename, mode='w',
                      shape=self.data.shape,
                      chunks=chunks, dtype=np.float32)

        z[:] = self.data
        self.data = z

    def add_geodataframe(self,
                         gdf,
                         feature_name,
                         bounds,
                         epsg,
                         resolution=10,
                         value_column='Index'
                         ):

        return self.merge(
            self.__class__.from_geodataframe(gdf,
                                             feature_name,
                                             bounds,
                                             epsg,
                                             resolution=resolution,
                                             value_column=value_column
                                             ))

    def add_l2a(self,
                l2a_collection,
                l2a_settings):

        return self.merge(
            self.__class__.from_l2a(l2a_collection,
                                    l2a_settings))

    def add_gamma0(self,
                   gamma0_collection,
                   gamma0_settings):
        return self.merge(
            self.__class__.from_gamma0(gamma0_collection,
                                       gamma0_settings))

    def add_agera5(self,
                   agera5_collection,
                   agera5_settings,
                   *args,
                   **kwargs):
        return self.merge(
            self.__class__.from_agera5(agera5_collection,
                                       agera5_settings,
                                       *args,
                                       **kwargs))

    def add_dem(self,
                dem_collection,
                dem_settings,
                resolution=10):

        return self.merge(
            self.__class__.from_dem(dem_collection,
                                    dem_settings,
                                    resolution=10))

    def add_latlon(self,
                   bounds,
                   epsg,
                   resolution=10):
        """
        Adds a lat, lon feature from the given bounds/epsg.

        See `from_latlon` for more details.

        """

        return self.merge(
            self.__class__.from_latlon(bounds,
                                       epsg,
                                       resolution=resolution))

    def add_pixelids(self):
        """
        Add a 'pixelids' with a different value for each pixel
        """
        new_shape = self.shape[-2:]
        new_feat_arr = np.arange(np.prod(new_shape)).reshape(new_shape)

        return self.merge(
            self._clone(new_feat_arr,
                        ['pixelids']))

    def onehot_encode(self, feature_name, prefix=None):
        """
        Returns an instance with the given the feature corresponding to
        `feature_name` onehot encoded
        """
        features = self

        if prefix is None:
            prefix = feature_name

        feat_arr = features[feature_name]
        new_features = features.drop(feature_name)

        values = np.unique(feat_arr)
        n = values.size

        encoded = np.zeros((n, *feat_arr.shape))
        encoded_names = []

        for i, v in enumerate(values):
            tmp = encoded[i]
            tmp[np.where(feat_arr == v)] = 1
            encoded[i] = tmp

            if np.isscalar(v):
                v = int(v)
            encoded_names.append(f"{prefix}_{v}")

        new_features = new_features.merge(Features(encoded, encoded_names))

        return new_features

    def show(self):
        from satio.utils.imviewer import ImViewer
        ImViewer(self.data, titles=self.names)

    def to_geotiff(self, bounds, epsg, filename):
        profile = get_rasterio_profile(self.data, bounds, epsg)
        logger.debug(f"Saving {filename}...")
        write_geotiff(self.data, profile, filename, self.names)

    @ classmethod
    def from_features(cls, *features):
        return features[0].merge(*features[1:])

    @ classmethod
    def from_constant(cls, value, name, shape):
        """
        Return an instance with a constant value.
        """
        data = np.ones(shape[-2:]) * value
        return cls(data, [name])

    @ classmethod
    def from_geodataframe(cls,
                          gdf: gpd.GeoDataFrame,
                          feature_name,
                          bounds,
                          epsg,
                          resolution=10,
                          value_column='Index'):
        """
        Returns an instance from the rasterization of the `gdf`.
        `value_column` specifies the value for the geometries intersecting
        bounds and epsg given.
        The CRS of the `gdf` should be defined but doesn't need to be the same
        of epsg
        """
        geom_arr = rasterize(gdf,
                             bounds,
                             epsg,
                             resolution=resolution,
                             value_column=value_column)

        return cls(geom_arr, [feature_name])

    @ classmethod
    def from_l2a(cls,
                 l2a_collection,
                 l2a_settings,
                 rsi_meta=None,
                 features_meta=None,
                 ignore_def_features=False):

        return (l2a_collection
                .features_processor(l2a_settings,
                                    rsi_meta=rsi_meta,
                                    features_meta=features_meta,
                                    ignore_def_features=ignore_def_features)
                .compute_features())

    @ classmethod
    def from_l2a_seasons(cls,
                         l2a_collection,
                         l2a_settings,
                         rsi_meta=None,
                         features_meta=None,
                         ignore_def_features=False):

        return (l2a_collection
                .features_processor_seas(l2a_settings,
                                         rsi_meta=rsi_meta,
                                         features_meta=features_meta,
                                         ignore_def_features=ignore_def_features)  # noqa: E501
                .compute_features())

    @ classmethod
    def from_gamma0(cls,
                    gamma0_collection,
                    gamma0_settings,
                    rsi_meta=None,
                    features_meta=None,
                    ignore_def_features=False):

        return (gamma0_collection
                .features_processor(gamma0_settings,
                                    rsi_meta=rsi_meta,
                                    features_meta=features_meta,
                                    ignore_def_features=ignore_def_features)
                .compute_features().upsample())

    @ classmethod
    def from_sigma0(cls,
                    sigma0_collection,
                    sigma0_settings,
                    rsi_meta=None,
                    features_meta=None,
                    ignore_def_features=False):

        return (sigma0_collection
                .features_processor(sigma0_settings,
                                    rsi_meta=rsi_meta,
                                    features_meta=features_meta,
                                    ignore_def_features=ignore_def_features)
                .compute_features().upsample())

    @ classmethod
    def from_agera5(cls,
                    agera5_collection,
                    agera5_settings,
                    demcol=None,
                    bounds=None,
                    epsg=None,
                    features_meta={},
                    rsi_meta={},
                    ignore_def_features=True):

        return (agera5_collection
                .features_processor(agera5_settings,
                                    demcol=demcol,
                                    bounds=bounds,
                                    epsg=epsg,
                                    features_meta=features_meta,
                                    rsi_meta=rsi_meta,
                                    ignore_def_features=ignore_def_features)
                .compute_features().upsample())

    @ classmethod
    def from_dem(cls,
                 dem_collection,
                 dem_settings=None,
                 resolution=10):

        default_names = ['DEM-alt-20m', 'DEM-slo-20m',
                         'DEM-nor-20m', 'DEM-eas-20m']

        dem_settings = dem_settings or {}
        features_names = dem_settings.get('features_names',
                                          default_names)

        altitude = dem_collection.load().astype(np.float32)

        altitude[altitude < -10000] = np.nan

        slope, aspect = dem_attrs(altitude)
        aspect = np.deg2rad(aspect)
        northness = np.cos(aspect)
        eastness = np.sin(aspect)

        default_arrs = [altitude, slope, northness, eastness]

        dem_features_dict = {fn: fa for fn, fa in zip(default_names,
                                                      default_arrs)}

        dem_features_arr = np.array(
            [dem_features_dict[fn] for fn in features_names])

        feats = cls(dem_features_arr, features_names)

        if resolution == 10:
            feats = feats.upsample()
        elif resolution == 20:
            pass
        else:
            raise ValueError("`resolution` should be 10 or 20.")

        return feats

    @ classmethod
    def from_worldcover(cls,
                        worldcover_collection,
                        resolution=10):

        features_names = ['WORLDCOVER-LABEL-10m']

        label = worldcover_collection.load().astype(np.uint8)

        feats = cls(label, features_names, dtype=np.uint8)

        if resolution == 20:
            feats = feats.downsample_categorical()
        elif resolution == 10:
            pass
        else:
            raise ValueError("`resolution` should be 10 or 20.")

        return feats

    @ classmethod
    def from_latlon(cls,
                    bounds,
                    epsg,
                    resolution=10,
                    steps=5):
        """
        Returns a lat, lon feature from the given bounds/epsg.

        This provide a coarse (but relatively fast) approximation to generate
        lat lon layers for each pixel.

        'steps' specifies how many points per axis should be use to perform
        the mesh approximation of the canvas
        """

        xmin, ymin, xmax, ymax = bounds
        out_shape = (int(np.floor((ymax - ymin) / resolution)),
                     int(np.floor((xmax - xmin) / resolution)))

        xx = np.linspace(xmin + resolution/2, xmax + resolution/2, steps)
        yy = np.linspace(ymax + resolution/2, ymin + resolution/2, steps)

        xx = np.broadcast_to(xx, [steps, steps]).reshape(-1)
        yy = np.broadcast_to(yy, [steps, steps]).T.reshape(-1)

        points = [Point(x0, y0) for x0, y0 in zip(xx, yy)]

        gs = gpd.GeoSeries(points, crs=CRS.from_epsg(epsg))
        gs = gs.to_crs(epsg=4326)

        lon_mesh = gs.apply(lambda p: p.x).values.reshape((steps, steps))
        lat_mesh = gs.apply(lambda p: p.y).values.reshape((steps, steps))

        lon = resize(lon_mesh, out_shape, order=1, mode='edge')
        lat = resize(lat_mesh, out_shape, order=1, mode='edge')

        features_arr = np.array([lat, lon])
        features_names = ['lat', 'lon']

        return cls(features_arr, features_names)

    def __repr__(self):
        attrs_repr = ', '.join([f"{k}: {v}" for k, v in self.attrs.items()])
        if len(attrs_repr):
            attrs_repr = " - " + attrs_repr

        return (f"<Features: {self.data.shape}{attrs_repr}>")

    def save(self, filename, compress=3):
        data = [self.data,
                self.names,
                self.attrs]
        joblib.dump(data, filename, compress=compress)

    @ classmethod
    def load(cls, filename: str) -> 'Features':
        data = joblib.load(filename)
        return cls(data[0],
                   names=data[1],
                   attrs=data[2])


class _FeaturesTimer():

    def __init__(self, *resolutions):

        self.load = {}
        self.prior_rsi = {}
        self.composite = {}
        self.interpolate = {}
        self.features = {}
        self.text_features = {}
        self.seasons = {}
        self.speckle = {}

        for r in resolutions:
            self.load[r] = TaskTimer(f'{r}m loading')
            self.prior_rsi[r] = TaskTimer(f'{r}m prior rsi calculation')
            self.composite[r] = TaskTimer(f'{r}m compositing')
            self.interpolate[r] = TaskTimer(f'{r}m interpolation')
            self.features[r] = TaskTimer(f'{r}m features computation')
            self.text_features[r] = TaskTimer(f'{r}m texture features')
            self.seasons[r] = TaskTimer(f'{r}m season detection')
            self.speckle[r] = TaskTimer(f'{r}m speckle filtering')


class BaseFeaturesProcessor(ABC):

    def __init__(self,
                 collection,
                 settings,
                 rsi_meta=None,
                 features_meta=None,
                 ignore_def_features=False):

        self.collection = collection
        self.sensor = collection.sensor
        self.settings = settings
        self._bands = None
        self._rsis = None
        self._supported_bands = None
        self._supported_rsis = None

        # merge default RSI_META with provided ones
        self._rsi_meta = {**RSI_META[self.sensor], **(rsi_meta or {})}

        # merge default FEATURES_META with provided ones
        if not ignore_def_features:
            self._features_meta = {**FEATURES_META, **(features_meta or {})}
        else:
            if features_meta is None:
                raise ValueError(('With `ignore_def_features`, at least '
                                  'a custom `features_meta` is required.'))
            self._features_meta = features_meta

    @ abstractproperty
    def supported_bands(self):
        ...

    @ abstractproperty
    def supported_rsis(self):
        ...

    @ abstractmethod
    def compute_features(self):
        ...

    @ abstractproperty
    def _reflectance(self):
        """
        True for S2 and False for S1
        """
        ...

    @ property
    def bands(self):
        if self._bands is None:
            self._bands = {res: [b for b in self.settings['bands']
                                 if b in sup_bands]
                           for res, sup_bands in self.supported_bands.items()}
        return self._bands

    @ property
    def rsis(self):
        if self._rsis is None:
            self._rsis = {res: [b for b in self.settings.get('rsis', [])
                                if b in sup_bands]
                          for res, sup_bands in self.supported_rsis.items()}
        return self._rsis


class GAMMA0FeaturesProcessor(BaseFeaturesProcessor):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.timer = _FeaturesTimer(20)

    @ property
    def supported_bands(self):
        return GAMMA_BANDS_DICT

    @ property
    def supported_rsis(self):
        if self._supported_rsis is None:
            rsis_dict = {}
            rsis_dict[20] = [r for r in self._rsi_meta.keys()]
            self._supported_rsis = rsis_dict

        return self._supported_rsis

    @ property
    def _reflectance(self):
        return False

    def load_data(self,
                  resolution=20,
                  timeseries=None,
                  mask=None,
                  speckle_filter=True,
                  composite=True,
                  interpolate=True):
        """
        Load Timeseries from the collection and merge with `timeseries` if
        given.
        """
        from satio.timeseries import load_timeseries

        collection = self.collection
        settings = self.settings

        bands = self.bands[resolution]
        loaded_bands = timeseries.bands if timeseries is not None else []
        bands_to_load = [b for b in bands if b not in loaded_bands]

        # number of obs needs to be calculated here
        self._obs = None

        logger.info(f"GAMMA0 collection products: {collection.df.shape[0]}")

        for band in bands_to_load:

            self.timer.load[resolution].start()
            logger.info(f'{band}: loading')
            band_ts = load_timeseries(collection, band)

            # get number of observations for first band loaded
            if self._obs is None:
                self._obs = band_ts.data[0]
                self._obs = self._obs != 0
                self._obs = self._obs.sum(axis=0)

            if mask is not None:
                # mask 'nan' values. for uint16 we use 0 as nodata value
                # mask values that are False are marked as invalid
                if isinstance(mask, dict):
                    mask = mask[resolution]

                band_ts = band_ts.mask(mask)

            # drop all no data frames
            band_ts = band_ts.drop_nodata()
            self.timer.load[resolution].stop()

            if speckle_filter:
                logger.info(f"{band}: speckle filtering")
                self.timer.speckle[resolution].start()
                data = band_ts.data
                data = gamma_db_to_lin(data)
                for band_idx in range(data.shape[0]):
                    data[band_idx] = multitemporal_speckle(data[band_idx])
                band_ts.data = gamma_lin_to_db(data)
                self.timer.speckle[resolution].stop()

            composite_settings = settings.get('composite')
            if (composite_settings is not None) & composite:
                self.timer.composite[resolution].start()
                logger.info(f"{band}: compositing")
                band_ts = band_ts.composite(**composite_settings)
                self.timer.composite[resolution].stop()

            if interpolate:
                self.timer.interpolate[resolution].start()
                logger.info(f'{band}: interpolating')
                band_ts = band_ts.interpolate()
                self.timer.interpolate[resolution].stop()

            if timeseries is None:
                timeseries = band_ts
            else:
                timeseries = timeseries.merge(band_ts)

        # timeseries.data = gamma_db_to_lin(timeseries.data)
        timeseries.data = timeseries.data.astype(np.float32)
        timeseries.data /= 3000

        return timeseries

    def compute_features(self,
                         chunk_size=None,
                         upsample_order=1):

        lproc = self
        timer = self.timer
        features_meta = self._features_meta
        rsi_meta = self._rsi_meta

        if features_meta is None:
            features_meta = FEATURES_META

        # 20m processing
        resolution = 20

        ts = lproc.load_data(resolution)

        timer.features[resolution].start()
        # compute 10m features and scale to reflectance
        logger.info(f"{resolution}m: computing bands features")
        features = ts.features_from_dict(resolution,
                                         features_meta=features_meta,
                                         chunk_size=chunk_size)

        # add RSI features
        logger.info(f"{resolution}m: computing rsi features")
        rsi_names = lproc.rsis[resolution]
        features_rsi = None
        for rn in rsi_names:
            if features_rsi is None:
                features_rsi = (ts.compute_rsis(rn,
                                                rsi_meta=rsi_meta,
                                                bands_scaling=1)
                                .features_from_dict(resolution,
                                                    features_meta=features_meta,  # NOQA
                                                    chunk_size=chunk_size))
            else:
                features_rsi = features_rsi.merge(
                    ts.compute_rsis(rn,
                                    rsi_meta=rsi_meta,
                                    bands_scaling=1).features_from_dict(
                        resolution,
                        features_meta=features_meta,
                        chunk_size=chunk_size))

        # merge band and rsi features
        if features is None:
            features = features_rsi
        elif features_rsi is not None:
            features = features.merge(features_rsi)

        # add meta features
        features = features.merge(
            Features(np.array([self._obs]),
                     names=['gamma0_obs']))

        for r in [20]:
            timer.load[r].log()
            timer.composite[r].log()
            timer.interpolate[r].log()
            timer.features[r].log()

        return features


def multitemporal_speckle(data):
    data = mtfilter(np.rollaxis(data, 0, 3), 'gamma')
    data = np.rollaxis(data, 2, 0)
    return data


def gamma_db_to_lin(dn):
    lin = np.zeros(dn.shape, dtype=np.float32)
    lin[dn > 0] = 10 ** ((20 * np.log10(dn[dn > 0]) - 83) / 10)
    lin[lin == 0] = np.nan
    return lin


def gamma_lin_to_db(lin):
    lin[~np.isfinite(lin)] = 0
    dn = np.zeros(lin.shape)
    dn[lin > 0] = 10.0 ** ((10 * np.log10(lin[lin > 0]) + 83) / 20)
    return dn.astype(np.uint16)


class SIGMA0FeaturesProcessor(GAMMA0FeaturesProcessor):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def load_data(self,
                  resolution=20,
                  timeseries=None):
        """
        Load Timeseries from the collection and merge with `timeseries` if
        given.
        """

        collection = self.collection

        bands = self.bands[resolution]
        loaded_bands = timeseries.bands if timeseries is not None else []
        bands_to_load = [b for b in bands if b not in loaded_bands]

        logger.info(f"SIGMA0 collection products: {collection.df.shape[0]}")

        if (len(bands_to_load) > 0):
            self.timer.load[resolution].start()

            # Put `mask_and_scale` to true to get physical dB values
            # TODO: a future disk collection does not have this attribute!
            bands_ts = collection.load_timeseries(*bands_to_load,
                                                  mask_and_scale=True)
            if timeseries is None:
                timeseries = bands_ts
            else:
                timeseries = timeseries.merge(bands_ts)
            self.timer.load[resolution].stop()

        return timeseries

    def preprocess_data(self,
                        timeseries: 'satio.timeseries.Timeseries',
                        resolution: int = 20,
                        mask: 'satio.timeseries.Timeseries' = None,
                        speckle_filter: bool = True,
                        composite: bool = True,
                        interpolate: bool = True):
        """
        Pre-processing of loaded timeseries object. Includes masking,
        speckle filtering, compositing and interpolation.
        """

        def _to_db(pwr):
            return 10 * np.log10(pwr)

        def _to_pwr(db):
            return np.power(10, db / 10)

        settings = self.settings
        newtimeseries = None

        # number of obs needs to be calculated here
        self._obs = None
        self._obs_notmasked = None

        for band in timeseries.bands:
            band_ts = timeseries.select_bands([band])

            # get number of observations for first band loaded
            if self._obs is None:
                self._obs = band_ts.data[0]
                self._obs = np.isfinite(self._obs)
                self._obs = self._obs.sum(axis=0)

            if mask is not None:

                # mask 'nan' values. for uint16 we use 0 as nodata value
                # mask values that are False are marked as invalid
                if isinstance(mask, dict):
                    mask = mask[resolution]

                # Subset the mask on the needed timestamps
                mask_subset = mask.select_timestamps(band_ts.timestamps)

                # Apply mask
                band_ts = band_ts.mask(mask_subset.data.astype(bool))

                if self._obs_notmasked is None:
                    self._obs_notmasked = band_ts.data[0]
                    self._obs_notmasked = np.isfinite(self._obs_notmasked)
                    self._obs_notmasked = self._obs_notmasked.sum(axis=0)

            # drop all no data frames
            band_ts = band_ts.drop_nodata()

            # Before doing manupulations
            # first need to get rid of dB
            data_lin = _to_pwr(band_ts.data)

            if speckle_filter:
                logger.info(f"{band}: speckle filtering")
                self.timer.speckle[resolution].start()
                for band_idx in range(data_lin.shape[0]):
                    data_lin[band_idx] = multitemporal_speckle(
                        data_lin[band_idx])
                self.timer.speckle[resolution].stop()

            band_ts.data = data_lin

            composite_settings = settings.get('composite')
            if (composite_settings is not None) & composite:
                self.timer.composite[resolution].start()
                logger.info(f"{band}: compositing")
                band_ts = band_ts.composite(**composite_settings)
                self.timer.composite[resolution].stop()

            if interpolate:
                self.timer.interpolate[resolution].start()
                logger.info(f'{band}: interpolating')
                band_ts = band_ts.interpolate()
                self.timer.interpolate[resolution].stop()

            # Finally back to dB
            data_db = _to_db(band_ts.data)
            band_ts.data = data_db

            if newtimeseries is None:
                newtimeseries = band_ts
            else:
                newtimeseries = newtimeseries.merge(band_ts)

        return newtimeseries

    def load_mask(self):

        from satio.utils.resample import upsample
        from satio.timeseries import Timeseries

        precip_threshold = 4  # mm

        settings = self.settings.get('mask', None)
        precip_threshold = settings.get('precipitation_threshold',
                                        precip_threshold)
        AgERA5 = settings.get('AgERA5_col')

        self.timer.load[20].start()
        logger.info(f'AgERA5: loading precipitation_flux')
        precip_ts = AgERA5.load_timeseries('precipitation_flux')

        logger.info((f"AgERA5: preparing precipitation mask "
                     f"(threshold: {precip_threshold} mm)"))

        # Upsample to proper resolution
        new_data = None
        old_data = precip_ts.data[0, ...]
        for t in range(5):
            new_data = upsample(old_data)
            old_data = new_data

        # Make the mask
        new_data[new_data <= precip_threshold] = 1
        new_data[new_data > precip_threshold] = 0

        # Back to Timeseries for further handling
        mask = Timeseries(np.expand_dims(new_data, axis=0),
                          precip_ts.timestamps, ['mask'])

        self.timer.load[20].stop()

        return mask

    def compute_features(self,
                         chunk_size=None,
                         upsample_order=1):

        lproc = self
        features_meta = self._features_meta
        rsi_meta = self._rsi_meta

        msk_settings = self.settings.get('mask', None)
        if msk_settings:
            if msk_settings.get('AgERA5_col', None):
                mask = self.load_mask()
            else:
                mask = None
        else:
            mask = None

        # check if texture features need to be computed
        # and store features_meta of those separately
        text_feat = False
        text_feat_meta = {}
        if 'texture' in features_meta.keys():
            text_feat = True
            text_feat_meta = features_meta['texture']
            del features_meta['texture']

        # if no other features remain at this point -> abort!
        if not bool(features_meta):
            raise ValueError('At least one other feature required'
                             'other than texture. Aborting...')

        # 20m processing
        resolution = 20

        ts = lproc.load_data(resolution)
        ts_proc = None
        pr_rsi = None

        if ts is not None:

            # check if some rsis need to be calculated first
            rsis = lproc.rsis[resolution]
            prior_rsi = []
            post_rsi = []
            for rsi in rsis:
                if rsi_meta[rsi].get('prior', False):
                    prior_rsi.append(rsi)
                else:
                    post_rsi.append(rsi)
            if len(prior_rsi) > 0:
                logger.info(f"{resolution}m: computing prior rsis")
                self.timer.prior_rsi[resolution].start()
                pr_rsi = ts.compute_rsis(*prior_rsi,
                                         rsi_meta=rsi_meta,
                                         bands_scaling=1)
                self.timer.prior_rsi[resolution].stop()

            # now pre-process the timeseries
            ts_proc = lproc.preprocess_data(ts, resolution, mask=mask)
            if len(prior_rsi) > 0:
                pr_rsi = lproc.preprocess_data(pr_rsi, resolution, mask=mask)

            # start feature calculation
            self.timer.features[resolution].start()

            logger.info(f"{resolution}m: computing bands features")
            features = ts.features_from_dict(resolution,
                                             features_meta=features_meta,
                                             chunk_size=chunk_size)

            # add RSI features
            logger.info(f"{resolution}m: computing rsi features")
            features_rsi = None

            # first up, the ones already calculated:
            for rn in prior_rsi:
                if features_rsi is None:
                    features_rsi = pr_rsi.select_bands(  # type: ignore
                        [rn]).features_from_dict(
                        resolution,
                        features_meta=features_meta,
                        chunk_size=chunk_size)
                else:
                    features_rsi = features_rsi.merge(
                        pr_rsi.select_bands(  # type: ignore
                            [rn]).features_from_dict(
                            resolution,
                            features_meta=features_meta,
                            chunk_size=chunk_size))

            # now those not already calculated:
            for rn in post_rsi:
                if features_rsi is None:
                    features_rsi = (ts_proc
                                    .compute_rsis(rn,
                                                  rsi_meta=rsi_meta,
                                                  bands_scaling=1)
                                    .features_from_dict(
                                        resolution,
                                        features_meta=features_meta,
                                        chunk_size=chunk_size))
                else:
                    features_rsi = features_rsi.merge(
                        ts_proc
                        .compute_rsis(rn,
                                      rsi_meta=rsi_meta,
                                      bands_scaling=1)
                        .features_from_dict(resolution,
                                            features_meta=features_meta,
                                            chunk_size=chunk_size))

            # merge band and rsi features
            if features is None:
                features = features_rsi
            elif features_rsi is not None:
                features = features.merge(features_rsi)

            self.timer.features[resolution].stop()

            # optionally compute texture features based on
            # computed features
            if text_feat:
                logger.info('Computing texture features')
                self.timer.text_features[resolution].start()
                inputFeat = features.select(text_feat_meta['features'])
                params = text_feat_meta['parameters']
                # if desired, run PCA first
                if 'pca' in text_feat_meta.keys():
                    inputFeat = inputFeat.pca(text_feat_meta['pca'],
                                              scaling_range=params.get(
                                                  'scaling_range', None))

                text_features = inputFeat.texture(
                    win=params.get('win', 2),
                    d=params.get('d', [1]),
                    theta=params.get('theta', [0, np.pi/4]),
                    levels=params.get('levels', 256),
                    metrics=params.get('metrics', ('contrast',)),
                    avg=params.get('avg', True),
                    scaling_range=params.get('scaling_range', {}))

                features = features.merge(text_features)

                self.timer.text_features[resolution].stop()

        else:
            features = None

        # add meta features
        features = features.merge(
            Features(np.array([self._obs]),
                     names=['sigma0_obs']))
        if msk_settings:
            features = features.merge(
                Features(np.array([self._obs_notmasked]),
                         names=['sigma0_obs_notmasked']))

        for r in [20]:
            self.timer.load[r].log()
            self.timer.composite[r].log()
            self.timer.interpolate[r].log()
            self.timer.features[r].log()

        return features


class TerrascopeSigma0FeaturesProcessor(SIGMA0FeaturesProcessor):

    def load_data(self,
                  resolution=10,
                  timeseries=None):
        """
        Override of default method to cope with
        Terrascope specific data
        """

        def _to_db(pwr):
            return 10 * np.log10(pwr)

        collection = self.collection

        bands = self.bands[resolution]
        loaded_bands = timeseries.bands if timeseries is not None else []
        bands_to_load = [b for b in bands if b not in loaded_bands]

        logger.info(f"SIGMA0 collection products: {collection.df.shape[0]}")

        if (len(bands_to_load) > 0):
            self.timer.load[resolution].start()

            # The raw data we load needs to be transformed to
            # dB and downsampled to 20m for compatibility
            # with the usual Sigma0/Gamma0 products
            bands_ts = collection.load_timeseries(*bands_to_load)

            if resolution == 20:
                # Need to downsample. Because values
                # are in float, need to use imresize method
                bands_ts = bands_ts.imresize(scaling=0.5)

            bands_ts.data = _to_db(bands_ts.data)

            if timeseries is None:
                timeseries = bands_ts
            else:
                timeseries = timeseries.merge(bands_ts)
            self.timer.load[resolution].stop()

        return timeseries


def _gee_to_gammascaling(db):
    '''
    Helper function to transform GEE extracted dB data
    to GAMMA scaling in uint16
    '''
    logger.debug('Transforming GEE sigma0 to GAMMA scaled values ...')
    nodata = 0
    idxinvalid = np.where(db == nodata)
    dn = 10.0 ** ((db + 83) / 20)
    dn[idxinvalid] = nodata
    return dn.astype(np.uint16)


def _gammascaling_to_db(dn):
    '''
    Helper function to transform GAMMA scaled values
    to dB returning float
    '''
    logger.debug('Transforming GAMMA scaled values to dB...')
    nodata = 0
    idxinvalid = np.where(dn == nodata)
    db = (np.log10(dn) * 20) - 83
    db[idxinvalid] = nodata

    return db.astype(np.float)


class L2AFeaturesProcessor(BaseFeaturesProcessor):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.timer = _FeaturesTimer(10, 20)

    @ property
    def supported_bands(self):
        return L2A_BANDS_DICT

    @ property
    def _reflectance(self):
        return True

    @ property
    def supported_rsis(self):
        if self._supported_rsis is None:
            rsis_dict = {}
            rsi_res = {r: self._rsi_meta[r]['native_res']
                       for r in self._rsi_meta.keys()}
            rsis_dict[10] = [v for v, r in rsi_res.items() if r == 10]
            rsis_dict[20] = [v for v, r in rsi_res.items() if r == 20]
            self._supported_rsis = rsis_dict

        return self._supported_rsis

    def preprocess_data(self,
                        timeseries: 'satio.timeseries.Timeseries',
                        resolution: int,
                        mask: np.ndarray = None,
                        composite: bool = True,
                        interpolate: bool = True):
        """
        Pre-processing of loaded timeseries object. Includes masking,
        compositing and interpolation.
        """
        settings = self.settings
        newtimeseries = None

        for band in timeseries.bands:
            band_ts = timeseries.select_bands([band])
            if mask is not None:
                # mask 'nan' values. for uint16 we use 0 as nodata value
                # mask values that are False are marked as invalid
                if isinstance(mask, dict):
                    mask = mask[resolution]

                band_ts = band_ts.mask(mask)

            # drop all no data frames
            band_ts = band_ts.drop_nodata()

            composite_settings = settings.get('composite')
            if (composite_settings is not None) & composite:
                self.timer.composite[resolution].start()
                logger.info(f"{band}: compositing")
                band_ts = band_ts.composite(**composite_settings)
                self.timer.composite[resolution].stop()

            if interpolate:
                self.timer.interpolate[resolution].start()
                logger.info(f'{band}: interpolating')
                band_ts = band_ts.interpolate()
                self.timer.interpolate[resolution].stop()

            if newtimeseries is None:
                newtimeseries = band_ts
            else:
                newtimeseries = newtimeseries.merge(band_ts)

        return newtimeseries

    def load_data(self,
                  resolution,
                  timeseries=None,
                  no_data=0,
                  dtype=None):
        """
        Load Timeseries from the collection and merge with `timeseries` if
        given.
        `dtype` allows optional explicit casting of the loaded data
        """
        collection = self.collection

        # check which bands are needed for the rsis at this resolution
        rsis = self.rsis[resolution]
        rsi_bands = {'all': []}
        for rsi in rsis:
            rsi_bands['all'].extend(self._rsi_meta[rsi]['bands'])
        # remove duplicates
        rsi_bands['all'] = list(dict.fromkeys(rsi_bands['all']))
        rsi_bands['10'] = [b for b in rsi_bands['all']
                           if b in self.supported_bands[10]]
        rsi_bands['20'] = [b for b in rsi_bands['all']
                           if b in self.supported_bands[20]]
        loaded_bands = timeseries.bands if timeseries is not None else []

        # if resolution == 20 -> check if you need 10 m bands for certain rsi's
        # because these need to be loaded first and downsampled
        if resolution == 20:
            bands_to_load = [b for b in rsi_bands['10']
                             if b not in loaded_bands]
            if (len(bands_to_load) > 0):
                self.timer.load[10].start()
                bands_ts = collection.load_timeseries(*bands_to_load)
                bands_ts.data[bands_ts.data == no_data] = 0
                if dtype is not None:
                    bands_ts.data = bands_ts.data.astype(dtype)
                bands_ts = bands_ts.downsample()
                if timeseries is None:
                    timeseries = bands_ts
                else:
                    timeseries = timeseries.merge(bands_ts)
                self.timer.load[10].stop()

        # now the 20m bands...
        bands = self.bands[resolution].copy()
        # add those for rsi...
        bands.extend([b for b in rsi_bands['{}'.format(resolution)]
                      if b not in bands])
        loaded_bands = timeseries.bands if timeseries is not None else []
        bands_to_load = [b for b in bands if b not in loaded_bands]

        if (len(bands_to_load) > 0):
            self.timer.load[resolution].start()
            bands_ts = collection.load_timeseries(*bands_to_load)
            bands_ts.data[bands_ts.data == no_data] = 0
            if dtype is not None:
                bands_ts.data = bands_ts.data.astype(dtype)
            if timeseries is None:
                timeseries = bands_ts
            else:
                timeseries = timeseries.merge(bands_ts)
            self.timer.load[resolution].stop()
        else:
            logger.info("Did not find bands to "
                        f"load for resolution: {resolution}")

        return timeseries

    def load_mask(self):

        from satio.utils.resample import downsample_n

        logger.info(f"L2A collection products: {self.collection.df.shape[0]}")

        self.timer.load[20].start()
        logger.info(f'SCL: loading')
        scl_ts = self.collection.load_timeseries('SCL')
        self.timer.load[20].stop()

        scl_ts = scl_ts.upsample()

        logger.info(f"SCL: preparing mask")
        mask, obs, invalid_before, invalid_after = _scl_mask(
            scl_ts.data, **self.settings['mask'])

        mask_20 = downsample_n(mask.astype(np.uint16), 1) == 1

        mask_dict = {10: mask,
                     20: mask_20}

        return mask_dict, obs, invalid_before, invalid_after

    def compute_features(self,
                         chunk_size=None,
                         upsample_order=1):

        timer = self.timer
        features_meta = self._features_meta
        rsi_meta = self._rsi_meta

        mask, obs, invalid_before, invalid_after = self.load_mask()

        # 10m processing
        resolution = 10
        ts = None
        ts_proc = None
        ts = self.load_data(resolution)

        if ts is not None:

            # check if some rsis need to be calculated first
            rsis = self.rsis[resolution]
            prior_rsi = []
            post_rsi = []
            for rsi in rsis:
                if rsi_meta[rsi].get('prior', False):
                    prior_rsi.append(rsi)
                else:
                    post_rsi.append(rsi)
            if len(prior_rsi) > 0:
                logger.info(f"{resolution}m: computing prior rsis")
                timer.prior_rsi[resolution].start()
                pr_rsi = ts.compute_rsis(*prior_rsi, rsi_meta=rsi_meta)
                timer.prior_rsi[resolution].stop()

            # now pre-process the timeseries
            ts_proc = self.preprocess_data(ts, resolution, mask=mask)
            if len(prior_rsi) > 0:
                pr_rsi = self.preprocess_data(pr_rsi,  # type: ignore
                                              resolution, mask=mask)

            # start feature calculation
            timer.features[resolution].start()

            # compute 10m features and scale to reflectance
            features_10m = None
            if len(self.bands[resolution]) > 0:
                logger.info(f"{resolution}m: computing bands features")
                features_10m = ts_proc.select_bands(
                    self.bands[resolution]).features_from_dict(
                        resolution,
                        features_meta=features_meta,
                        chunk_size=chunk_size)

                # because bands features are calculated from uint16 bands
                # scale them to reflectance values
                # (fft features should not be scaled though)
                features_10m.data /= 10000

            # add RSI features
            logger.info(f"{resolution}m: computing rsi features")
            features_10m_rsi = None
            # first up, the ones already calculated:
            for rn in prior_rsi:
                if features_10m_rsi is None:
                    features_10m_rsi = pr_rsi.select_bands(  # type: ignore
                        [rn]).features_from_dict(
                        resolution,
                        features_meta=features_meta,
                        chunk_size=chunk_size)
                else:
                    features_10m_rsi = features_10m_rsi.merge(
                        pr_rsi.select_bands(  # type: ignore
                            [rn]).features_from_dict(
                            resolution,
                            features_meta=features_meta,
                            chunk_size=chunk_size))

            # now those not already calculated:
            for rn in post_rsi:
                if features_10m_rsi is None:
                    features_10m_rsi = (ts_proc
                                        .compute_rsis(rn,
                                                      rsi_meta=rsi_meta,
                                                      bands_scaling=10000)
                                        .features_from_dict(
                                            resolution,
                                            features_meta=features_meta,
                                            chunk_size=chunk_size))
                else:
                    features_10m_rsi = features_10m_rsi.merge(
                        ts_proc
                        .compute_rsis(rn,
                                      rsi_meta=rsi_meta,
                                      bands_scaling=10000)
                        .features_from_dict(resolution,
                                            features_meta=features_meta,
                                            chunk_size=chunk_size))

            # merge with band features
            if features_10m is not None:
                if features_10m_rsi is not None:
                    features_10m = features_10m.merge(features_10m_rsi)
            else:
                features_10m = features_10m_rsi

            timer.features[resolution].stop()
        else:
            features_10m = None

        # start 20 m processing
        resolution = 20
        rsis = self.rsis[resolution]
        if (len(self.bands[20]) > 0) or (len(rsis) > 0):

            features_20m = self.compute_features_20m(ts, ts_proc,
                                                     chunk_size,
                                                     mask)

            # upsample 20m features to 10m and merge them
            if features_10m is None:
                features_10m = features_20m.upsample(order=upsample_order)
            elif features_20m is not None:
                features_10m = features_10m.merge(
                    features_20m.upsample(order=upsample_order))

        # add meta features
        features_10m = features_10m.merge(
            Features(np.array([obs, invalid_before, invalid_after]),
                     names=['l2a_observations',
                            'l2a_invalid_before',
                            'l2a_invalid_after'])
        )

        for r in [10, 20]:
            timer.load[r].log()
            timer.prior_rsi[r].log()
            timer.composite[r].log()
            timer.interpolate[r].log()
            timer.features[r].log()

        return features_10m

    def compute_features_20m(self, ts, ts_proc_10m, chunk_size, mask):

        resolution = 20
        timer = self.timer
        features_meta = self._features_meta
        rsi_meta = self._rsi_meta
        # load raw data
        if ts is not None:
            # downsample 10 m bands to 20m
            ts = ts.downsample()
            ts_proc_10m = ts_proc_10m.downsample()
            # load raw 20m bands
            ts = self.load_data(resolution, timeseries=ts)
        else:
            ts = self.load_data(resolution)
        # check if some rsis need to be calculated first
        rsis = self.rsis[resolution]
        prior_rsi = []
        post_rsi = []

        for rsi in rsis:
            if rsi_meta[rsi].get('prior', False):
                prior_rsi.append(rsi)
            else:
                post_rsi.append(rsi)

        if len(prior_rsi) > 0:
            logger.info(f"{resolution}m: computing prior rsis")
            timer.prior_rsi[resolution].start()
            pr_rsi = ts.compute_rsis(*prior_rsi, rsi_meta=rsi_meta)
            timer.prior_rsi[resolution].stop()

        # now pre-process the timeseries
        # (only those which were not pre-processed at 10 m resolution)
        bands = self.bands[resolution].copy()
        # add those bands required to calculate the requested RSI's
        for rsi in post_rsi:
            rsi_bands = self._rsi_meta[rsi]['bands']
            bands.extend([b for b in rsi_bands if b not in bands])
            # remove 10m bands
            if ts_proc_10m is not None:
                bands = [b for b in bands if b not in ts_proc_10m.bands]
        ts_proc_20m = self.preprocess_data(ts.select_bands(bands),
                                           resolution,
                                           mask=mask)

        if ts_proc_10m is not None:
            ts_proc = ts_proc_20m.merge(ts_proc_10m)
        else:
            ts_proc = ts_proc_20m
        if len(prior_rsi) > 0:
            pr_rsi = self.preprocess_data(pr_rsi,  # type: ignore
                                          resolution,
                                          mask=mask)
        timer.features[resolution].start()
        logger.info(f"{resolution}m: computing rsis features")
        features_20m = None

        # compute features of prior rsis first
        for rn in prior_rsi:
            if features_20m is None:
                features_20m = pr_rsi.select_bands(  # type: ignore
                    [rn]).features_from_dict(
                    resolution,
                    features_meta=features_meta,
                    chunk_size=chunk_size)
            else:
                features_20m = features_20m.merge(
                    pr_rsi.select_bands(  # type: ignore
                        [rn]).features_from_dict(
                        resolution,
                        features_meta=features_meta,
                        chunk_size=chunk_size))
        # compute rsis features before dropping 10m bands from timeseries
        for rn in post_rsi:
            if features_20m is None:
                features_20m = (ts_proc
                                .compute_rsis(rn, rsi_meta=rsi_meta)
                                .features_from_dict(resolution,
                                                    features_meta=features_meta,  # NOQA
                                                    chunk_size=chunk_size))
            else:
                features_20m = features_20m.merge(
                    ts_proc
                    .compute_rsis(rn,
                                  rsi_meta=rsi_meta,
                                  bands_scaling=10000)
                    .features_from_dict(resolution,
                                        features_meta=features_meta,
                                        chunk_size=chunk_size))

        if len(self.bands[resolution]) > 0:
            # reduce timeseries to 20m bands only
            ts_proc = ts_proc.select_bands(self.bands[resolution])

            # compute bands features
            logger.info(f"{resolution}m: computing bands features")
            features_20m_bands = ts_proc.features_from_dict(
                resolution,
                features_meta=features_meta,
                chunk_size=chunk_size)

            # scale bands features  (fft features should not be scaled though)
            features_20m_bands.data /= 10000

            # merge with other features
            if features_20m is None:
                features_20m = features_20m_bands
            else:
                features_20m = features_20m.merge(features_20m_bands)

        timer.features[resolution].stop()

        return features_20m


class L2AFeaturesProcessorSeasons(L2AFeaturesProcessor):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def compute_features_10m(self, ts, chunk_size, mask):
        resolution = 10
        timer = self.timer
        features_meta = self._features_meta
        rsi_meta = self._rsi_meta

        # check if some rsis need to be calculated first
        rsis = self.rsis[resolution]
        prior_rsi = []
        post_rsi = []
        for rsi in rsis:
            if rsi_meta[rsi].get('prior', False):
                prior_rsi.append(rsi)
            else:
                post_rsi.append(rsi)
        if len(prior_rsi) > 0:
            logger.info(f"{resolution}m: computing prior rsis")
            timer.prior_rsi[resolution].start()
            pr_rsi = ts.compute_rsis(*prior_rsi, rsi_meta=rsi_meta)
            timer.prior_rsi[resolution].stop()

        # now pre-process the timeseries
        ts_proc = self.preprocess_data(ts, resolution, mask=mask)
        # pre-process computed rsis (if any)
        if len(prior_rsi) > 0:
            pr_rsi = self.preprocess_data(pr_rsi,  # type: ignore
                                          resolution, mask=mask)

        # start feature calculation
        timer.features[resolution].start()

        # compute 10m band features and scale to reflectance
        features_10m = None
        if len(self.bands[resolution]) > 0:
            logger.info(f"{resolution}m: computing bands features")
            features_10m = ts_proc.select_bands(
                self.bands[resolution]).features_from_dict(
                    resolution,
                    features_meta=features_meta,
                    chunk_size=chunk_size)

            # because bands features are calculated from uint16 bands
            # scale them to reflectance values
            # (fft features should not be scaled though)
            features_10m.data /= 10000

        # add RSI features
        logger.info(f"{resolution}m: computing rsi features")
        features_10m_rsi = None
        # first up, the ones already calculated:
        for rn in prior_rsi:
            if features_10m_rsi is None:
                features_10m_rsi = pr_rsi.select_bands(  # type: ignore
                    [rn]).features_from_dict(
                    resolution,
                    features_meta=features_meta,
                    chunk_size=chunk_size)
            else:
                features_10m_rsi = features_10m_rsi.merge(
                    pr_rsi.select_bands(  # type: ignore
                        [rn]).features_from_dict(
                        resolution,
                        features_meta=features_meta,
                        chunk_size=chunk_size))

        # now those not already calculated:
        for rn in post_rsi:
            if features_10m_rsi is None:
                features_10m_rsi = (ts_proc
                                    .compute_rsis(rn,
                                                  rsi_meta=rsi_meta,
                                                  bands_scaling=10000)
                                    .features_from_dict(
                                        resolution,
                                        features_meta=features_meta,
                                        chunk_size=chunk_size))
            else:
                features_10m_rsi = features_10m_rsi.merge(
                    ts_proc
                    .compute_rsis(rn,
                                  rsi_meta=rsi_meta,
                                  bands_scaling=10000)
                    .features_from_dict(resolution,
                                        features_meta=features_meta,
                                        chunk_size=chunk_size))

        # merge with band features
        if features_10m is not None:
            if features_10m_rsi is not None:
                features_10m = features_10m.merge(features_10m_rsi)
        else:
            features_10m = features_10m_rsi

        timer.features[resolution].stop()

        return features_10m, ts_proc

    def compute_features_20m(self, ts, ts_proc_10m, chunk_size, mask):

        resolution = 20
        timer = self.timer
        features_meta = self._features_meta
        rsi_meta = self._rsi_meta

        # load raw data
        if ts is not None:
            # downsample 10 m bands to 20m
            ts = ts.downsample()
            ts_proc_10m = ts_proc_10m.downsample()
            # load raw 20m bands
            ts = self.load_data(resolution, timeseries=ts)
        else:
            ts = self.load_data(resolution)

        # check if some rsis need to be calculated first
        rsis = self.rsis[resolution]
        prior_rsi = []
        post_rsi = []
        for rsi in rsis:
            if rsi_meta[rsi].get('prior', False):
                prior_rsi.append(rsi)
            else:
                post_rsi.append(rsi)

        # calculate prior rsis
        if len(prior_rsi) > 0:
            logger.info(f"{resolution}m: computing prior rsis")
            timer.prior_rsi[resolution].start()
            pr_rsi = ts.compute_rsis(*prior_rsi, rsi_meta=rsi_meta)
            timer.prior_rsi[resolution].stop()

        # now pre-process the timeseries
        # (only those which were not pre-processed at 10 m resolution)
        bands = self.bands[resolution].copy()
        # add those bands required to calculate the requested RSI's
        for rsi in post_rsi:
            rsi_bands = rsi_meta[rsi]['bands']
            bands.extend([b for b in rsi_bands if b not in bands])
            # remove 10m bands (if any)
            if ts_proc_10m is not None:
                bands = [b for b in bands if b not in ts_proc_10m.bands]
        ts_proc_20m = self.preprocess_data(ts.select_bands(bands),
                                           resolution,
                                           mask=mask)
        # add 10 m pre-processed bands
        if ts_proc_10m is not None:
            ts_proc = ts_proc_20m.merge(ts_proc_10m)
        else:
            ts_proc = ts_proc_20m

        # pre-process prior rsis
        if len(prior_rsi) > 0:
            pr_rsi = self.preprocess_data(pr_rsi,  # type: ignore
                                          resolution,
                                          mask=mask)

        # start feature computation
        timer.features[resolution].start()
        logger.info(f"{resolution}m: computing rsis features")
        features_20m = None

        # compute features of prior rsis first
        for rn in prior_rsi:
            if features_20m is None:
                features_20m = pr_rsi.select_bands(  # type: ignore
                    [rn]).features_from_dict(
                    resolution,
                    features_meta=features_meta,
                    chunk_size=chunk_size)
            else:
                features_20m = features_20m.merge(
                    pr_rsi.select_bands(  # type: ignore
                        [rn]).features_from_dict(
                        resolution,
                        features_meta=features_meta,
                        chunk_size=chunk_size))

        # compute rsis features before dropping 10m bands from timeseries
        for rn in post_rsi:
            if features_20m is None:
                features_20m = (ts_proc
                                .compute_rsis(rn, rsi_meta=rsi_meta)
                                .features_from_dict(resolution,
                                                    features_meta=features_meta,  # NOQA
                                                    chunk_size=chunk_size))
            else:
                features_20m = features_20m.merge(
                    ts_proc
                    .compute_rsis(rn,
                                  rsi_meta=rsi_meta)
                    .features_from_dict(resolution,
                                        features_meta=features_meta,
                                        chunk_size=chunk_size))

        # compute 20m bands features
        if len(self.bands[resolution]) > 0:
            # reduce timeseries to 20m bands only
            ts_proc = ts_proc.select_bands(self.bands[resolution])

            # compute bands features
            logger.info(f"{resolution}m: computing bands features")
            features_20m_bands = ts_proc.features_from_dict(
                resolution,
                features_meta=features_meta,
                chunk_size=chunk_size)

            # scale bands features  (fft features should not be scaled though)
            features_20m_bands.data /= 10000

            # merge with other features
            if features_20m is None:
                features_20m = features_20m_bands
            else:
                features_20m = features_20m.merge(features_20m_bands)

        timer.features[resolution].stop()

        return features_20m, ts, ts_proc

    def _get_seasons(self, ts, ts_proc, mask, seasonSettings, resolution):

        rsi_meta = self._rsi_meta
        rsi_seas = seasonSettings.get('rsi', 'evi')
        timer = self.timer

        logger.info(f"{resolution}m: detecting growing seasons")
        timer.seasons[resolution].start()

        # compute required rsi first...
        if rsi_meta[rsi_seas].get('prior', False):
            rsi = ts.compute_rsis(rsi_seas, rsi_meta=rsi_meta)
            rsi = self.preprocess_data(rsi, resolution, mask=mask)
        else:
            rsi = ts_proc.compute_rsis(rsi_seas, rsi_meta=rsi_meta)
        # get parameters
        max_seasons = seasonSettings.get('max_seasons', 5)
        amp_thr1 = seasonSettings.get('amp_thr1', 0.1)
        amp_thr2 = seasonSettings.get('amp_thr2', 0.35)
        min_window = seasonSettings.get('min_window', 10)
        max_window = seasonSettings.get('max_window', 185)
        partial_start = seasonSettings.get('partial_start', False)
        partial_end = seasonSettings.get('partial_end', False)
        # run season detection
        seasons = rsi.detect_seasons(max_seasons=max_seasons,
                                     amp_thr1=amp_thr1,
                                     amp_thr2=amp_thr2,
                                     min_window=min_window,
                                     max_window=max_window,
                                     partial_start=partial_start,
                                     partial_end=partial_end)

        timer.seasons[resolution].stop()

        return seasons

    def compute_phen_features(self, seasons, pheno_feat_meta, resolution):

        # TODO: for now, all pheno features are only computed on the RSI
        # from which the seasons were derived. This should be extended
        # towards multiple bands or rsis, but requires some more thinking...
        # The idea is that you specify in the features_meta for which bands
        # the single_season features need to be computed and you make sure
        # these timeseries are imported in this function

        timer = self.timer
        phen_feat = None

        logger.info(f"{resolution}m: computing pheno features")
        if 'pheno_mult_season' in pheno_feat_meta.keys():
            timer.features[resolution].start()
            phen_feat = seasons.pheno_mult_season_features(resolution)
            timer.features[resolution].stop()

        if 'pheno_single_season' in pheno_feat_meta.keys():
            timer.features[resolution].start()
            sel_mode = pheno_feat_meta['pheno_single_season'][
                'select_season']['mode']
            sel_param = pheno_feat_meta['pheno_single_season'][
                'select_season']['param']
            if phen_feat is None:
                phen_feat = seasons.pheno_single_season_features(sel_mode,
                                                                 sel_param,
                                                                 resolution)
            else:
                phen_feat = phen_feat.merge(
                    seasons.pheno_single_season_features(sel_mode,
                                                         sel_param,
                                                         resolution))
            timer.features[resolution].stop()

        return phen_feat

    def compute_features(self,
                         chunck_size=None,
                         upsample_order=1):

        timer = self.timer
        settings = self.settings
        features_meta = self._features_meta

        # check if texture features need to be computed
        # and store features_meta of those separately
        text_feat = False
        text_feat_meta = {}
        if 'texture' in features_meta.keys():
            text_feat = True
            text_feat_meta = features_meta['texture']
            del features_meta['texture']

        # if no other features remain at this point -> abort!
        if not bool(features_meta):
            raise ValueError('At least one other feature required'
                             'other than texture. Aborting...')

        # check if pheno features need to be computed
        # and store features_meta of those in separate variable
        seas_feat = False
        pheno_feat_meta = {}
        pheno_keys = ['pheno_mult_season', 'pheno_single_season']
        for p_key in pheno_keys:
            if p_key in features_meta.keys():
                seas_feat = True
                pheno_feat_meta.update({p_key: features_meta[p_key]})
                del features_meta[p_key]

        # check whether all bands and rsis are represented
        # in features_meta. If not, drop the ones not needed!
        check = False
        for key, value in features_meta.items():
            if value.get("bands", None) is None:
                check = True
        if not check:
            feat_bands = []
            for key, value in features_meta.items():
                feat_bands.extend(value.get("bands", []))
            to_remove_b = [b for b in settings['bands']
                           if b not in feat_bands]
            for b in to_remove_b:
                settings['bands'].remove(b)
            to_remove_r = [r for r in settings['rsis']
                           if r not in feat_bands]
            for r in to_remove_r:
                settings['rsis'].remove(r)

        # if seasons need to be detected:
        # make sure the RSI required for this is included in the rsi list
        # to be computed!
        seasonSettings = settings.get('seasons', {})
        if bool(seasonSettings) or (seas_feat):
            rsi_seas = seasonSettings.get('rsi', 'evi')
            if rsi_seas not in settings['rsis']:
                settings['rsis'].append(rsi_seas)
            # determine at which resolution the season detection needs to be
            # done
            if rsi_seas in self.supported_rsis[10]:
                resolution_seas = 10
            else:
                resolution_seas = 20
        else:
            seasons = None
            resolution_seas = 0

        # load 10m data
        resolution = 10
        ts = None
        ts_proc = None
        ts = self.load_data(resolution)

        # get mask
        mask, obs, invalid_before, invalid_after = self.load_mask()

        # feature computuation at 10 m
        if ts is not None:
            features_10m, ts_proc = self.compute_features_10m(ts,
                                                              chunck_size,
                                                              mask)

            # if season detection needs to be done on 10m -> do it now!
            if resolution_seas == 10:
                seasons = self._get_seasons(ts, ts_proc,
                                            mask, seasonSettings,
                                            resolution_seas)

                # compute pheno features
                phen_feat_10m = self.compute_phen_features(seasons,
                                                           pheno_feat_meta,
                                                           resolution)

                # merge with other 10m features
                if features_10m is not None:
                    if phen_feat_10m is not None:
                        features_10m = features_10m.merge(phen_feat_10m)
                else:
                    features_10m = phen_feat_10m
        else:
            features_10m = None

        # start 20 m feature computation
        resolution = 20
        rsis = self.rsis[resolution]
        if (len(self.bands[resolution]) > 0) or (len(rsis) > 0):

            features_20m, ts, ts_proc = self.compute_features_20m(ts, ts_proc,
                                                                  chunck_size,
                                                                  mask)

            # if season detection needs to be done on 20m -> do it now!
            if resolution_seas == 20:
                seasons = self._get_seasons(ts, ts_proc,
                                            mask, seasonSettings,
                                            resolution_seas)

                # compute pheno features
                phen_feat_20m = self.compute_phen_features(seasons,
                                                           pheno_feat_meta,
                                                           resolution)

                # merge with other 20m features
                if features_20m is not None:
                    if phen_feat_20m is not None:
                        features_20m = features_20m.merge(phen_feat_20m)
                else:
                    features_20m = phen_feat_20m

            # upsample 20m features to 10m and merge them
            if features_10m is None:
                features_10m = features_20m.upsample(order=upsample_order)
            elif features_20m is not None:
                features_10m = features_10m.merge(
                    features_20m.upsample(order=upsample_order))

        # optionally compute texture features based on
        # computed features
        if text_feat:
            logger.info('Computing texture features')
            timer.text_features[10].start()
            inputFeat = features_10m.select(text_feat_meta['features'])
            params = text_feat_meta['parameters']
            # if desired, run PCA first
            if 'pca' in text_feat_meta.keys():
                inputFeat = inputFeat.pca(text_feat_meta['pca'],
                                          scaling_range=params.get(
                    'scaling_range', None))

            text_features = inputFeat.texture(
                win=params.get('win', 2),
                d=params.get('d', [1]),
                theta=params.get('theta', [0, np.pi/4]),
                levels=params.get('levels', 256),
                metrics=params.get('metrics', ('contrast',)),
                avg=params.get('avg', True),
                scaling_range=params.get('scaling_range', {}))

            features_10m = features_10m.merge(text_features)

            timer.text_features[10].stop()

        # add meta features
        features_10m = features_10m.merge(
            Features(np.array([obs, invalid_before, invalid_after]),
                     names=['l2a_observations',
                            'l2a_invalid_before',
                            'l2a_invalid_after']))

        for r in [10, 20]:
            timer.load[r].log()
            timer.prior_rsi[r].log()
            timer.composite[r].log()
            timer.interpolate[r].log()
            timer.features[r].log()
            timer.text_features[r].log()
            timer.seasons[r].log()

        return features_10m, seasons


class MAJAFeaturesProcessor(L2AFeaturesProcessor):

    def load_mask(self):

        from satio.utils.resample import downsample_n
        from satio.timeseries import load_timeseries

        logger.info(f"L2A collection products: {self.collection.df.shape[0]}")

        self.timer.load[10].start()
        logger.info(f'CLM: loading')
        scl_ts = load_timeseries(self.collection, 'CLM')
        self.timer.load[10].stop()

        mask = scl_ts.data[0] == 0
        obs = np.ones(mask.shape[-2:]) * mask.shape[0]
        invalid_before = 1 - mask.mean(axis=0)
        invalid_after = invalid_before

        mask_20 = downsample_n(mask.astype(np.uint16), 1) == 1

        mask_dict = {10: mask,
                     20: mask_20}

        return mask_dict, obs, invalid_before, invalid_after

    def load_data(self,
                  resolution,
                  timeseries=None,
                  mask=None,
                  composite=True,
                  interpolate=True):
        """
        Load Timeseries from the collection and merge with `timeseries` if
        given.
        """
        from satio.timeseries import load_timeseries

        collection = self.collection
        settings = self.settings

        bands = self.bands[resolution]
        loaded_bands = timeseries.bands if timeseries is not None else []
        bands_to_load = [b for b in bands if b not in loaded_bands]

        for band in bands_to_load:

            self.timer.load[resolution].start()
            logger.info(f'{band}: loading')
            band_ts = load_timeseries(collection, band)

            # if (band == 'B08') and (resolution == 20):
            #     band_ts = band_ts.downsample()

            if mask is not None:
                # mask 'nan' values. for uint16 we use 0 as nodata value
                # mask values that are False are marked as invalid
                if isinstance(mask, dict):
                    mask = mask[resolution]

                band_ts = band_ts.mask(mask, nodata_value=-10000)

            band_ts.data[band_ts.data == -10000] = 0
            band_ts.data = band_ts.data.astype(np.uint16)

            # drop all no data frames
            band_ts = band_ts.drop_nodata()
            self.timer.load[resolution].stop()

            composite_settings = settings.get('composite')
            if (composite_settings is not None) & composite:
                self.timer.composite[resolution].start()
                logger.info(f"{band}: compositing")
                band_ts = band_ts.composite(**composite_settings)
                self.timer.composite[resolution].stop()

            if interpolate:
                self.timer.interpolate[resolution].start()
                logger.info(f'{band}: interpolating')
                band_ts = band_ts.interpolate()
                self.timer.interpolate[resolution].stop()

            if timeseries is None:
                timeseries = band_ts
            else:
                timeseries = timeseries.merge(band_ts)

        return timeseries


class ICORFeaturesProcessor(L2AFeaturesProcessor):

    def load_mask(self):

        from satio.utils.resample import upsample
        from satio.timeseries import load_timeseries

        logger.info(f"L2A collection products: {self.collection.df.shape[0]}")

        self.timer.load[10].start()
        logger.info(f'IPX: loading')
        scl_ts = load_timeseries(self.collection, 'IPX')
        self.timer.load[10].stop()

        mask = scl_ts.data[0] == 1

        mask_10 = upsample(mask.astype(np.uint8)) == 1
        obs = np.ones(mask_10.shape[-2:]) * mask_10.shape[0]
        invalid_before = 1 - mask_10.mean(axis=0)
        invalid_after = invalid_before

        mask_dict = {10: mask_10,
                     20: mask}

        # zero_arr = np.zeros(mask_10.shape[-2:])

        return mask_dict, obs, invalid_before, invalid_after

    def load_data(self,
                  resolution,
                  timeseries=None,
                  mask=None,
                  composite=True,
                  interpolate=True):
        """
        Load Timeseries from the collection and merge with `timeseries` if
        given.
        """
        from satio.timeseries import load_timeseries

        collection = self.collection
        settings = self.settings

        bands = self.bands[resolution]
        loaded_bands = timeseries.bands if timeseries is not None else []
        bands_to_load = [b for b in bands if b not in loaded_bands]

        for band in bands_to_load:

            self.timer.load[resolution].start()
            logger.info(f'{band}: loading')
            band_ts = load_timeseries(collection, band)

            # if (band == 'B08') and (resolution == 20):
            #     band_ts = band_ts.downsample()

            if mask is not None:
                # mask 'nan' values. for uint16 we use 0 as nodata value
                # mask values that are False are marked as invalid
                if isinstance(mask, dict):
                    mask = mask[resolution]

                band_ts = band_ts.mask(mask, nodata_value=0)

            band_ts.data[band_ts.data < 0] = 0
            band_ts.data = band_ts.data.astype(np.uint16)

            # drop all no data frames
            band_ts = band_ts.drop_nodata()
            self.timer.load[resolution].stop()

            composite_settings = settings.get('composite')
            if (composite_settings is not None) & composite:
                self.timer.composite[resolution].start()
                logger.info(f"{band}: compositing")
                band_ts = band_ts.composite(**composite_settings)
                self.timer.composite[resolution].stop()

            if interpolate:
                self.timer.interpolate[resolution].start()
                logger.info(f'{band}: interpolating')
                band_ts = band_ts.interpolate()
                self.timer.interpolate[resolution].stop()

            if timeseries is None:
                timeseries = band_ts
            else:
                timeseries = timeseries.merge(band_ts)

        return timeseries


class TerrascopeV200FeaturesProcessor(L2AFeaturesProcessor):

    def load_mask(self):

        from satio.utils.resample import downsample_n
        from satio.timeseries import load_timeseries

        nodata = 32767  # Terrascope S2-TOC nodata value

        logger.info(("Terrascope L2A collection "
                     f"products: {self.collection.df.shape[0]}"))

        self.timer.load[20].start()
        logger.info(f'SCL: loading')
        scl_ts = load_timeseries(self.collection, 'SCENECLASSIFICATION')
        scl_ts.data[scl_ts.data == nodata] = 0
        self.timer.load[20].stop()

        scl_ts = scl_ts.upsample()

        logger.info(f"SCL: preparing mask")
        mask, obs, invalid_before, invalid_after = _scl_mask(
            scl_ts.data, **self.settings['mask'])

        mask_20 = downsample_n(mask.astype(np.uint16), 1) == 1

        mask_dict = {10: mask,
                     20: mask_20}

        return mask_dict, obs, invalid_before, invalid_after

    def load_data(self,
                  resolution,
                  timeseries=None):
        """
        Load Timeseries from the collection and merge with `timeseries` if
        given.
        We need to override the default method to account for specific no data
        and explicitly cast dtype
        """

        return super().load_data(resolution,
                                 timeseries=timeseries,
                                 no_data=32767,
                                 dtype=np.uint16)


class TerrascopeV200FeaturesProcessorSeasons(L2AFeaturesProcessorSeasons):

    def load_mask(self):

        from satio.utils.resample import downsample_n
        from satio.timeseries import load_timeseries

        nodata = 32767  # Terrascope S2-TOC nodata value

        logger.info(("Terrascope L2A collection "
                     f"products: {self.collection.df.shape[0]}"))

        self.timer.load[20].start()
        logger.info(f'SCL: loading')
        scl_ts = load_timeseries(self.collection, 'SCENECLASSIFICATION')
        scl_ts.data[scl_ts.data == nodata] = 0
        self.timer.load[20].stop()

        scl_ts = scl_ts.upsample()

        logger.info(f"SCL: preparing mask")
        mask, obs, invalid_before, invalid_after = _scl_mask(
            scl_ts.data, **self.settings['mask'])

        mask_20 = downsample_n(mask.astype(np.uint16), 1) == 1

        mask_dict = {10: mask,
                     20: mask_20}

        return mask_dict, obs, invalid_before, invalid_after

    def load_data(self,
                  resolution,
                  timeseries=None):
        """
        Load Timeseries from the collection and merge with `timeseries` if
        given.
        We need to override the default method to account for specific no data
        and explicitly cast dtype
        """

        return super().load_data(resolution,
                                 timeseries=timeseries,
                                 no_data=32767,
                                 dtype=np.uint16)


def get_array_windows(n_rows, n_cols, chunk_size):
    """
    Return tuple of tuples ((row_start, row_end), (col_start, col_end))
    for a set of windows of arrays of shape 'chunk_size'.
    """
    if isinstance(chunk_size, int):
        chunk_size = (chunk_size, chunk_size)

    rows_ids = list(range(0, n_rows, chunk_size[0])) + [n_rows]
    cols_ids = list(range(0, n_cols, chunk_size[1])) + [n_cols]

    windows = []
    for ridx in range(len(rows_ids) - 1):
        for cidx in range(len(cols_ids) - 1):
            win = ((rows_ids[ridx], rows_ids[ridx + 1]),
                   (cols_ids[cidx], cols_ids[cidx + 1]))
            windows.append(win)

    return windows


def compute_chunked_features(data,
                             func,
                             n_features,
                             chunk_size=256,
                             **kwargs):
    raise NotImplementedError


def _scl_mask(scl_data,
              *,
              mask_values,
              erode_r=None,
              dilate_r=None,
              max_invalid_ratio=None):
    """
    From a timeseries (t, y, x) returns a binary mask False for the
    given mask_values and True elsewhere.

    Parameters:
    -----------
    slc_data: 3D array
        Input array for computing the mask

    mask_values: list
        values to set to False in the mask

    erode_r : int
        Radius for eroding disk on the mask

    dilate_r : int
        Radius for dilating disk on the mask

    max_invalid_ratio : float
        Will set mask values to True, when they have an
        invalid_ratio > max_invalid_ratio

    Returns:
    --------
    mask : 3D bool array
        mask True for valid pixels, False for invalid

    obs : 2D int array
        number of valid observations (different from 0 in scl_data)

    invalid_before : 2D float array
        ratio of invalid obs before morphological operations

    invalid_after : 2D float array
        ratio of invalid obs after morphological operations
    """
    scl_data = scl_data[0]

    ts_obs = scl_data != 0

    obs = ts_obs.sum(axis=0)

    mask = np.isin(scl_data, mask_values)
    ma_mask = (mask & ts_obs)

    invalid_before = ma_mask.sum(axis=0) / obs

    if (erode_r is not None) | (erode_r > 0):
        erode_disk = footprints.disk(erode_r)
        for i in range(mask.shape[0]):
            mask[i] = binary_erosion(mask[i], erode_disk)

    if (dilate_r is not None) | (dilate_r > 0):
        dilate_disk = footprints.disk(dilate_r)
        for i in range(mask.shape[0]):
            mask[i] = binary_dilation(mask[i], dilate_disk)

    ma_mask = (mask & ts_obs)
    invalid_after = ma_mask.sum(axis=0) / obs

    # invert values to have True for valid pixels and False for clouds
    mask = ~mask

    if max_invalid_ratio is not None:
        max_invalid_mask = invalid_after > max_invalid_ratio
        mask = mask | np.broadcast_to(max_invalid_mask, mask.shape)

    return mask, obs, invalid_before, invalid_after


class _iLocIndexer:

    def __init__(self, feat_coll):
        self._feat_coll = feat_coll

    def __getitem__(self, idx):
        key = self._feat_coll.indices[idx]
        return self._feat_coll.__getitem__(key)


class FeaturesCollection:

    def __init__(self, features: List[Features], indices: List = None):

        if indices is None:
            indices = list(range(len(features)))

        def _raise_type(f, i):
            raise TypeError(f"'features' should be Features objects. "
                            f'Instead is {type(f)} at index {i}.')

        self.features = {i: f.add_attribute(i, 'collection_idx')
                         if isinstance(f, Features)
                         else _raise_type(f, i)
                         for f, i in zip(features, indices)}

        self._df = None
        self._iter_idx = 0

    def __getitem__(self, key) -> Features:

        if isinstance(key, list):
            return [self.features[k] for k in key]
        else:
            return self.features[key]

    def __setitem__(self, key, value):
        if not isinstance(value, Features):
            raise TypeError('value type should be `Features`')
        self.features[key] = value

    @ property
    def iloc(self):
        return _iLocIndexer(self)

    @ property
    def indices(self):
        return list(self.features.keys())

    @ property
    def df(self):
        if self._df is None:
            self._df = pd.concat([f.df for f in self.features.values()],
                                 ignore_index=True, axis=0)
        return self._df

    @ classmethod
    def from_df(cls,
                df: pd.DataFrame,
                attr_cols: List[str] = [],
                index_column: str = None,
                canvas_shape: Tuple[int] = None):
        """
        index_column should be the column name of a unique location identifier.
        The canvas shape is assumed to be square if None is provided.

        If no index_column is provided, the indices will be read from the
        default column 'collection_idx' which is created when generating
        a DataFrame from a FeaturesCollection
        """
        if index_column is None:
            index_column = 'collection_idx'

        indices = df[index_column].unique().tolist()

        cols_drop = attr_cols + [index_column]

        features = []
        features_names = [c for c in df.columns
                          if c not in cols_drop]

        for idx in indices:
            feat_df = df[df[index_column] == idx]

            if canvas_shape is None:
                rows = cols = int(feat_df.shape[0] ** 0.5)
                canvas_shape = rows, cols

            features_arr = (feat_df
                            .drop(columns=cols_drop)
                            .values
                            .T
                            .reshape(len(features_names),
                                     canvas_shape[0],
                                     canvas_shape[1])
                            )

            features.append(Features(features_arr,
                                     features_names,
                                     attrs={k: feat_df[k].unique()[0]
                                            for k in attr_cols}))

        return cls(features, indices)

    def add(self, values, name):
        """
        values should be an iterable with same length as df.shape[0]
        """
        df = self.df
        df[name] = values
        return self.__class__.from_df(df)

    def _cluster_features(self,
                          distance_threshold,
                          features_names=None,
                          conditions_handle=None):
        """
        Perform AgglomerativeClustering on dataframe
        """
        from sklearn.cluster import AgglomerativeClustering

        features_names = features_names or []

        if conditions_handle:
            features_names_cond = [f for f in self.df.columns
                                   if conditions_handle(f)]
        else:
            raise ValueError("One for 'features_name' or 'conditions_handle'"
                             " should be provided, they are both None")

        features_names += features_names_cond
        df = self.df.fillna(0)
        df = df.drop(columns=[c for c in df.columns
                              if c not in features_names])

        clusters = (AgglomerativeClustering(n_clusters=None,
                                            distance_threshold=distance_threshold)  # noqa: E501
                    .fit(df.values))

        return clusters.labels_

    def add_cluster(self,
                    distance_threshold,
                    features_names=None,
                    conditions_handle=None):

        cluster_labels = self._cluster_features(distance_threshold,
                                                features_names,
                                                conditions_handle)

        return self.add(cluster_labels, 'cluster')

    def __repr__(self):
        return f'<FeaturesCollection - n: ({len(list(self.features.keys()))})>'

    def __iter__(self):
        self._iter_idx = 0
        return self

    def __next__(self):
        try:
            idx = self.indices[self._iter_idx]
        except IndexError:
            raise StopIteration
        self._iter_idx += 1
        return self[idx]


"""
Below is a set of deafault temporal features computation functions
"""


def fft_coeffs(x, n_coeffs=5):
    t = rfft(x, axis=0)
    t = t[:n_coeffs, ...]
    return t


def tsteps(x, n_steps=6):
    return scipy.signal.resample(x, n_steps, axis=0)


def percentile(x, q=[10, 30, 50, 70, 90]):
    return np.percentile(x, q=q, axis=0)


def percentile_iqr(x, q=[10, 50, 90], iqr=[25, 75]):

    q_all = list(set(q + iqr))
    q_ids = [q_all.index(qv) for qv in q]
    iqr_ids = [q_all.index(qv) for qv in iqr]

    perc = np.percentile(x, q=q_all, axis=0)

    perc_arr = perc[q_ids]
    iqr_arr = perc[iqr_ids[1]] - perc[iqr_ids[0]]

    iqr_arr = np.expand_dims(iqr_arr, axis=0)

    arr = np.concatenate([perc_arr, iqr_arr], axis=0)

    return arr


def std(x):
    return np.std(x, axis=0)


def amp_disp(x):
    # amplitude dispersion
    return np.std(x, axis=0) / np.mean(x, axis=0)


def skewness(x):
    return skew(x, axis=0)


def kurto(x):
    return kurtosis(x, axis=0)


def summation(x):
    return np.sum(x, axis=0, keepdims=True)


FEATURES_META = {
    "percentile_iqr": {
        "function": percentile_iqr,
        "parameters": {
            'q': [10, 50, 90],
            'iqr': [25, 75]
        },
        "names": ['p10', 'p50', 'p90', 'iqr']
    },
    "tsteps": {
        "function": tsteps,
        "parameters": {
            'n_steps': 6,
        },
        "names": ['ts0', 'ts1', 'ts2', 'ts3', 'ts4', 'ts5']
    }
}

# features_meta = {
#   "percentile": {
#       "function": percentile,
#       "parameters": {
#           'q': [10, 30, 50, 70, 90],
#       },
#       "names": ['p10', 'p30', 'p50', 'p70', 'p90']
#   },
#   "std": {
#       "function": std,
#       "names": ['std']
#   },
#   "fft_coeffs": {
#       "function": fft_coeffs,
#       "parameters": {
#           'n_coeffs': 5,
#       },
#       "names": ['fft00', 'fft01', 'fft02', 'fft03', 'fft04']
#   },
#   "tsteps": {
#       "function": tsteps,
#       "parameters": {
#           'n_steps': 6,
#       },
#       "names": ['ts0', 'ts1', 'ts2', 'ts3', 'ts4', 'ts5']
#   }
# }
