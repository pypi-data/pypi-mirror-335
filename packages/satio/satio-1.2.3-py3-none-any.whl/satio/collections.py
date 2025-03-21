"""
Tools to build collections of Sentinel 1 and Sentinel 2 products stored
locally
"""
# import below only works from Python 3.7, can we avoid that?
# this import needs to be at the beginning of the file
# from __future__ import annotations

from typing import TypeVar, Dict, List
from abc import (ABC,
                 abstractmethod,
                 abstractproperty)
import re
import os
import glob
import json
from datetime import datetime
import concurrent.futures
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr
from tqdm import tqdm
from shapely.geometry import Polygon
import geopandas as gpd
import rasterio
from rasterio.crs import CRS
from rasterio.enums import Resampling
from dateutil.parser import parse
import requests
from loguru import logger

import satio
from satio.features import (L2AFeaturesProcessor as L2AFeatProc,
                            L2AFeaturesProcessorSeasons as L2AFeatProcSeas,
                            GAMMA0FeaturesProcessor,
                            SIGMA0FeaturesProcessor,
                            MAJAFeaturesProcessor,
                            ICORFeaturesProcessor,
                            TerrascopeV200FeaturesProcessor as TSV2FeatProc,
                            TerrascopeV200FeaturesProcessorSeasons as TSV2FeatProcSeas,  # NOQA
                            TerrascopeSigma0FeaturesProcessor as TSS0FeatProc)
from satio.grid import tile_to_epsg
from satio.geoloader import (get_l2a_filenames, get_jp2_filenames,
                             ParallelLoader,
                             AWSParallelLoader,
                             AWSCOGSLoader,
                             LatLonReprojectLoader,
                             WarpLoader)
from satio.utils import glob_subfolder, glob_level_subfolders, parallelize
from satio.utils.aws import S3BucketReader
from satio.utils.errors import EmptyCollection
import tempfile


L2A_10M_BANDS = ['AOT', 'B02', 'B03', 'B04', 'B08', 'TCI', 'WVP']
L2A_20M_BANDS = ['AOT', 'B02', 'B03', 'B04', 'B05',
                 'B06', 'B07', 'B08', 'B11', 'B12',
                 'B8A', 'SCL', 'TCI', 'WVP',
                 'sunAzimuthAngles', 'sunZenithAngles',
                 'viewAzimuthMean', 'viewZenithMean']
L2A_60M_BANDS = ['AOT', 'B01', 'B02', 'B03', 'B04',
                 'B05', 'B06', 'B07', 'B08', 'B09',
                 'B10', 'B11', 'B12', 'B8A', 'SCL', 'TCI',
                 'WVP']

L2A_RES_BANDS = [L2A_10M_BANDS,
                 L2A_20M_BANDS,
                 L2A_60M_BANDS]

L2A_BANDS = ['B01', 'B02', 'B03', 'B04', 'B05', 'B06', 'B07', 'B08',
             'B8A', 'B09', 'B11', 'B12']

L2A_OPTIONAL_BANDS = ['SCL', 'SNW', 'CLD',
                      'AOT', 'WVP', 'TCI']

MAJA_BANDS = ['B02', 'B03', 'B04', 'B05', 'B06', 'B07', 'B08',
              'B8A', 'B11', 'B12']
MAJA_MASKS = ['CLM']

ICOR_BANDS = ['B01', 'B02', 'B03', 'B04', 'B05', 'B06', 'B07', 'B08',
              'B8A', 'B09', 'B11', 'B12']
ICOR_MASKS = ['IPX']

TERRASCOPE_BANDS = ['B01', 'B02', 'B03', 'B04', 'B05', 'B06', 'B07', 'B08',
                    'B8A', 'B09', 'B11', 'B12']
TERRASCOPE_OPTIONAL_BANDS = ['SCENECLASSIFICATION', 'RAA',
                             'AOT', 'WVP', 'VZA', 'SZA']

GAMMA_BANDS = ['VV', 'VH']

AGERA5_BANDS = ['wind-speed', 'vapour-pressure', 'temperature-min',
                'temperature-max', 'temperature-mean',
                'solar-radiation-flux', 'precipitation-flux',
                'dewpoint-temperature']

NODATA_VALUE = -2**15
SCL_MASK_VALUES = [0, 1, 3, 8, 9, 10, 11]

# Terrascope
_S2_BASEDIR = '/data/MTDA/TERRASCOPE_Sentinel2/NDVI_V2'
_TS_S2_BASEURL = ('https://services.terrascope.be/catalogue/'
                  'products?collection=urn%3Aeop%3AVITO%3A'
                  'TERRASCOPE_S2')
_S1_BASEDIR = '/data/MTDA/CGS_S1_GRD_SIGMA0_L1'
_TS_S1_BASEURL = ('https://services.terrascope.be/catalogue/'
                  'products?collection=urn%3Aeop%3AVITO%3A'
                  'CGS_S1_GRD_SIGMA0_L1')


def is_s2esa_product(filename):
    basename = os.path.basename(filename)
    pattern = (r'^S2[AB]_MSIL(1C|2A)_\d{8}T\d{6}_N\d{4}_R\d{3}_'
               + r'T\d{2}[A-Z]{3}_\d{8}T\d{6}.(SAFE|zip)$')
    if re.match(pattern, basename):
        return True
    else:
        return False


def is_s2maja_product(filename):
    basename = os.path.basename(filename)
    maja_pattern = (r'^SENTINEL2[AB]_\d{8}-\d{6}-\d{3}_L2A_'
                    r'T\d{2}[A-Z]{3}')
    if re.match(maja_pattern, basename):
        return True
    else:
        return False


def is_s2aws_product(filename):
    basename = os.path.basename(filename)
    pattern = (r'^S2[AB]_MSIL(1C|2A)_\d{8}T\d{6}_N\d{4}_R\d{3}_'
               + r'T\d{2}[A-Z]{3}_\d{8}T\d{6}$')
    if re.match(pattern, basename):
        return True
    else:
        return False


def is_s2icor_product(filename):
    basename = os.path.basename(filename)
    icor_pattern = (r'^S2[AB]_MSIL1C_\d{8}T\d{6}_N\d{4}_R\d{3}_'
                    + r'T\d{2}[A-Z]{3}_\d{8}T\d{6}_iCOR$')
    if re.match(icor_pattern, basename):
        return True
    else:
        return False
    # raise NotImplementedError


def is_idepix_product(filename):
    basename = os.path.basename(filename)
    idepix_pattern = (r'^S2[AB]_MSIIPX_\d{8}T\d{6}_N\d{4}_R\d{3}_'
                      + r'T\d{2}[A-Z]{3}_\d{8}T\d{6}')
    if re.match(idepix_pattern, basename):
        return True
    else:
        return False
    # raise NotImplementedError


def is_sentinel1_product(filename):
    # S1A_IW_GRDH_1SDV_20190117T052837_20190117T052902_025513_02D435_70BB
    basename = os.path.basename(filename)
    s1_pattern = (r'^S1[AB]_IW_GRDH_1SDV_\d{8}T\d{6}_\d{8}T\d{6}_')
    if re.match(s1_pattern, basename):
        return True
    else:
        return False


def is_sentinel2_product(filename):
    """Check if file has L1C/L2A name and returns True or False"""
    if not isinstance(filename, str):
        raise TypeError("Input should be of string type")

    if (is_s2esa_product(filename)
            or is_s2maja_product(filename)
            or is_s2icor_product(filename)
            or is_s2aws_product(filename)):

        return True
    else:
        return False


def glob_sentinel2_products(path):
    """
    Generator of sentinel2 products filenames from directory.
    Scans recursively for .zip and .SAFE products
    """
    root_dir, folders, files = next(os.walk(path))

    for f in files:
        if is_sentinel2_product(f):
            yield os.path.join(root_dir, f)

    for d in folders:
        new_path = os.path.join(root_dir, d)
        if is_sentinel2_product(d):
            yield new_path
        else:
            yield from glob_sentinel2_products(new_path)


def glob_sentinel1_products(path):
    """
    Generator of sentinel2 products filenames from directory.
    Scans recursively for .zip and .SAFE products
    """
    root_dir, folders, files = next(os.walk(path))

    for f in files:
        if is_sentinel1_product(f):
            yield os.path.join(root_dir, f)

    for d in folders:
        new_path = os.path.join(root_dir, d)
        if is_sentinel1_product(d):
            yield new_path
        else:
            yield from glob_sentinel1_products(new_path)


def s2esa_entry(filename):
    """
    Returns dictionary of sentinel 2 product with specifications from filename
    """
    basename = os.path.basename(filename)
    product_id, ext = basename.split('.')
    mission_id, level, date, baseline, orbit, tile, _ = product_id.split('_')

    entry = dict(level=level[3:],
                 product_id=product_id,
                 mission_id=mission_id,
                 date=datetime.strptime(date, '%Y%m%dT%H%M%S'),
                 baseline=baseline,
                 orbit=orbit,
                 tile=tile[1:],
                 zipped=(True if ext == 'zip' else False),
                 path=filename)

    return entry


def s2maja_entry(filename):
    """
    Returns dictionary of MAJA sentinel 2 product with specifications
    from filename
    """
    basename = os.path.basename(filename)
    product_id = basename
    mission_id_ext, date_ext, level, tile, _, _ = product_id.split('_')
    mission_id = 'S' + mission_id_ext[-2:]

    entry = dict(level=level,
                 product_id=product_id,
                 mission_id=mission_id,
                 date=datetime.strptime(date_ext[:-4], '%Y%m%d-%H%M%S'),
                 baseline=None,
                 orbit=None,
                 tile=tile[1:],
                 zipped=False,
                 path=filename)

    return entry


def s2aws_entry(filename):
    """
    Returns dictionary of sentinel 2 product with specifications from filename
    """
    basename = os.path.basename(filename)
    product_id = basename
    mission_id, level, date, baseline, orbit, tile, _ = product_id.split('_')

    entry = dict(level=level[3:],
                 product_id=product_id,
                 mission_id=mission_id,
                 date=datetime.strptime(date, '%Y%m%dT%H%M%S'),
                 baseline=baseline,
                 orbit=orbit,
                 tile=tile[1:],
                 path=filename)

    return entry


def s2idepix_entry(filename):
    """
    Returns dictionary of sentinel 2 product with specifications from filename
    """
    basename = os.path.basename(filename)
    product_id = basename
    mission_id, level, date, baseline, orbit, tile, _ = product_id.split('_')

    entry = dict(level=level[3:],
                 product_id=product_id[:-4],
                 mission_id=mission_id,
                 date=datetime.strptime(date, '%Y%m%dT%H%M%S'),
                 baseline=baseline,
                 orbit=orbit,
                 tile=tile[1:],
                 path=filename)

    return entry


def s2icor_entry(filename):
    """
    Returns dictionary of sentinel 2 product with specifications from filename
    """
    basename = os.path.basename(filename)
    product_id = basename
    mission_id, level, date, baseline, orbit, tile, _, _ = product_id.split(
        '_')

    entry = dict(level=level[3:],
                 product_id=product_id,
                 mission_id=mission_id,
                 date=datetime.strptime(date, '%Y%m%dT%H%M%S'),
                 baseline=baseline,
                 orbit=orbit,
                 tile=tile[1:],
                 path=filename)

    return entry


def sentinel2_entry(filename):
    if is_s2esa_product(filename):
        return s2esa_entry(filename)
    elif is_s2maja_product(filename):
        return s2maja_entry(filename)
    elif is_s2aws_product(filename):
        return s2aws_entry(filename)
    elif is_s2icor_product(filename):
        return s2icor_entry(filename)
    else:
        raise ValueError('filename: {} is not a valid sentinel2 product'
                         .format(filename))


def _build_s2products_df(folder, threads=20):
    """
    Globs sentinel2 products in folder (SAFE and ZIP) and
    returns a Pandas dataframe with the filenames and basic metadata
    info
    """
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as ex:
        products = list(
            ex.map(lambda x: x, glob_sentinel2_products(folder)))
    # products = list(glob_sentinel2_products(folder))

    entries = [sentinel2_entry(f) for f in products]
    if len(entries):
        df = pd.DataFrame(entries)
    else:
        df = pd.DataFrame([], columns=['level',
                                       'product_id',
                                       'mission_id',
                                       'date',
                                       'baseline',
                                       'orbit',
                                       'tile',
                                       'zipped',
                                       'path'])

    return df


def build_s2products_df(*folders):
    """
    Globs sentinel2 products in given folders (SAFE and ZIP) and
    returns a Pandas dataframe with the filenames and basic metadata
    info
    """
    dfs_list = [_build_s2products_df(folder) for folder in folders]
    return pd.concat(dfs_list, axis=0)


def get_maja_filenames(maja_product):
    filenames_list = glob.glob(os.path.join(maja_product, '**', '*.tif'),
                               recursive=True)
    filenames = {}
    bands_10m = ['B02', 'B03', 'B04', 'B08']
    # bands_20m = ['B05', 'B06', 'B07', 'B8A', 'B11', 'B12']

    for f in filenames_list:
        if 'FRE' in f:
            short_band = f.split('_')[-1].split('.')[0]
            if len(short_band) == 2:
                band = short_band[0] + '0' + short_band[1]
            else:
                band = short_band

            if band in bands_10m:
                resolution = 10
            else:
                resolution = 20

            filenames[band] = {resolution: f}

        if 'CLM' in f:
            d = filenames.get('CLM', {})
            if f.endswith('R1.tif'):
                resolution = 10
            else:
                resolution = 20

            d[resolution] = f
            filenames['CLM'] = d

    return filenames


def get_icor_filenames(icor_product):
    filenames_list = glob.glob(os.path.join(icor_product, '*.tif'),
                               recursive=True)
    filenames = {}
    bands_10m = ['B02', 'B03', 'B04', 'B08']
    # bands_20m = ['B05', 'B06', 'B07', 'B8A', 'B11', 'B12']

    for f in filenames_list:
        band = f.split('_')[-1].split('.')[0]

        if band in bands_10m:
            resolution = 10
        elif band == 'B09':
            resolution = 60
        else:
            resolution = 20

        filenames[band] = {resolution: f}

    return filenames


def _get_gamma_entry(tif):

    basename = os.path.basename(tif)
    split = basename.split('_')

    product = os.path.basename(os.path.dirname(tif))
    tile = split[0]
    date = datetime.strptime(product.split('_')[4], "%Y%m%dT%H%M%S")

    return dict(product=product,
                tile=tile,
                epsg=tile_to_epsg(tile),
                date=date,
                path=tif
                )


def _get_gamma_entries(p):
    tifs = glob.glob(os.path.join(p, '**', '*_vv_*.tif'), recursive=True)
    entries = [_get_gamma_entry(tif) for tif in tifs]
    return entries


def _build_s1products_df(folder, threads=20):
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as ex:
        products = list(
            ex.map(lambda x: x, glob_sentinel1_products(folder)))

    # products = [p for p in glob_sentinel1_products(folder)]
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as ex:
        results = list(ex.map(_get_gamma_entries, products))

    entries = [e for r in results for e in r]

    if len(entries):
        df = pd.DataFrame(entries)
    else:
        df = pd.DataFrame([], columns=['product', 'tile',
                                       'epsg', 'date', 'path'])

    return df


def build_s1products_df(*folders):
    dfs = [_build_s1products_df(folder) for folder in folders]
    return pd.concat(dfs, axis=0)


def get_maja_band_filename(filenames, band, resolution):
    """Returns filename for band (MAJA product) closest to target resolution"""
    bands_10m = ['B02', 'B03', 'B04', 'B08']
    bands_20m = ['B05', 'B06', 'B07', 'B8A', 'B11', 'B12']

    if band in bands_10m:
        resolution = 10
    elif band in bands_20m:
        resolution = 20
    elif band == 'CLM':
        if resolution > 20:
            resolution = 20
        else:
            resolution = 10
    else:
        raise ValueError("Band {} not supported.".format(band))

    return filenames[band][resolution]


def get_icor_band_filename(filenames, band, resolution):
    """Returns filename for band (ICOR product) closest to target resolution"""
    bands_10m = ['B02', 'B03', 'B04', 'B08']
    bands_20m = ['B05', 'B06', 'B07', 'B8A', 'B11', 'B12', 'IPX']

    # BAND 9 !
    # Resolution 60

    if band in bands_10m:
        resolution = 10
    elif band in bands_20m:
        resolution = 20
    else:
        raise ValueError("Band {} not supported.".format(band))

    return filenames[band][resolution]


def _get_aws_gamma_entry(tif):

    basename = os.path.basename(tif)
    split = basename.split('_')

    product = os.path.basename(os.path.dirname(tif))

    tile = split[0]
    # date = datetime.strptime(f'{split[1]}T{split[2]}', "%Y%m%dT%H%M%S")
    date = datetime.strptime(f'{split[1]}', "%Y%m%d")

    path = tif

    entry = dict(product=product,
                 tile=tile,
                 epsg=tile_to_epsg(tile),
                 date=date,
                 path=path
                 )
    return entry


def _glob_aws_tifs(client, prefix):
    subfolder_files = [f's3://{client.bucket}/{f}'
                       for tf in client.list_dirs(prefix)
                       for f in client.list_files(tf)
                       if '_vv_' in f]
    current_files = [f's3://{client.bucket}/{f}'
                     for f in client.list_files(prefix)
                     if '_vv_' in f]

    return subfolder_files + current_files


def _build_aws_gamma0_products_df(client, folders, max_workers=50):
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as ex:
        results = list(tqdm(ex.map(lambda x: _glob_aws_tifs(client, x),
                                   folders),
                            total=len(folders)))

    files = [f for r in results for f in r]
    entries = [_get_gamma_entry(f) for f in files]

    return pd.DataFrame(entries)


def build_products_df(sensor, *folders):
    if sensor == 'S1':
        return build_s1products_df(*folders)
    elif sensor == 'S2':
        return build_s2products_df(*folders)
    else:
        raise NotImplementedError(f"Unrecognized sensor: {sensor}")


def get_s2_product_date(product):
    return pd.to_datetime(str(Path(product).stem).split('_')[1])


def get_s1_product_date(product):
    return pd.to_datetime(str(Path(product).stem).split('_')[5])


def create_terrascope_products_df(products, tile, epsg, sensor='s2'):
    df = pd.DataFrame(columns=['product', 'date', 'path'],
                      index=None)

    if sensor == 's2':
        df['date'] = [get_s2_product_date(x) for x in products]
    elif sensor == 's1':
        df['date'] = [get_s1_product_date(x) for x in products]
    else:
        raise ValueError(f'Unrecognized sensor: {sensor}')

    df['product'] = [str(Path(product).stem) for product in products]
    df['path'] = products
    df['tile'] = tile
    df['epsg'] = epsg
    df = df.sort_values('date', axis=0)

    return df


class BaseCollection(ABC):
    """
    Abstract class describing the base methods of a collection class
    """

    @abstractproperty
    def supported_bands(self):
        pass

    @abstractproperty
    def supported_resolutions(self):
        pass

    @abstractproperty
    def bands(self):
        pass

    @abstractproperty
    def products(self):
        pass

    @abstractproperty
    def timestamps(self):
        pass

    @abstractproperty
    def loader(self):
        pass

    @abstractmethod
    def get_band_filenames(self, band, resolution):
        pass


class DiskCollection(BaseCollection):
    """
    Abstract class base for all collections of files stored on a local
    filesystem. The products must be tiled using the Sentinel-2 grid
    """

    def __init__(self, df, s2grid=None):

        if df.empty:
            df = self._empty_df()

        self.df = df.sort_values('date')
        self.tiles = sorted(self.df.tile.unique().tolist())
        self.start_date = datetime(2000, 1, 1)
        self.end_date = datetime(2100, 1, 1)

        self._s2grid = (s2grid if s2grid is not None
                        else satio.layers.load('s2grid'))

        self._bounds = None
        self._filenames = None
        self._bands = None
        self._epsg = None
        self._loader = None
        self._sensor = NotImplementedError

    @classmethod
    def from_path(cls, path, s2grid=None):
        path = Path(path)
        if path.is_file():
            return cls.from_file(path, s2grid=s2grid)
        elif path.is_dir():
            return cls.from_folders(path, s2grid=s2grid)
        else:
            raise ValueError(f'{path} is neither a folder nor a file.')

    @classmethod
    def from_file(cls, filename, s2grid=None):
        df = pd.read_csv(filename)
        df.date = pd.to_datetime(df.date)
        return cls(df, s2grid=s2grid)

    @classmethod
    def from_folders(cls, *folders, s2grid=None):
        df = build_products_df(cls.sensor, *folders)
        df = df.sort_values('date', ascending=True)
        collection = cls(df, s2grid=s2grid)
        return collection

    def save(self, filename):
        self.df.to_csv(filename, index=False)

    @property
    def epsg(self):
        return self._epsg

    @property
    def bounds(self):
        return self._bounds

    @property
    def bands(self):
        if self._bands is None:
            self.bands = self.supported_bands
        return self._bands

    @bands.setter
    def bands(self, bands):
        for b in bands:
            if b not in self.supported_bands:
                raise ValueError("Band {} not supported.".format(b))
        self._bands = bands

    @property
    def products(self):
        return self.df.path.values.tolist()

    @property
    def timevector(self):
        return self.df.date.values

    @property
    def timestamps(self):
        return self.df.date.apply(lambda x: str(x)).values.tolist()

    @property
    def loader(self):
        if self._loader is None:
            self._loader = ParallelLoader()
        return self._loader

    @loader.setter
    def loader(self, value):
        self._loader = value

    def filter_dates(self, start_date, end_date):
        df = self.df[(self.df.date >= start_date)
                     & (self.df.date < end_date)]
        return self._clone(df=df, start_date=start_date, end_date=end_date)

    def filter_bounds(self, bounds, epsg):
        self._epsg = int(epsg)
        self._bounds = bounds
        products = self._get_products(self._bounds, self._epsg)
        return self._clone(df=products)

    def filter_bands(self, *bands):
        return self._clone(bands=bands)

    def filter_tiles(self, *tiles):
        df = self.df[self.df.tile.isin(tiles)]
        return self._clone(df=df)

    def _get_products(self,
                      bounds: List,
                      epsg: int) -> pd.DataFrame:
        """
        Returns subset of products df that intersect with the given
        bounds and EPSG
        """
        gs = gpd.GeoSeries(Polygon.from_bounds(*bounds),
                           crs=CRS.from_epsg(epsg)).to_crs(epsg=4326)
        bbox = gs.iloc[0]

        tiles = self._s2grid[self._s2grid.intersects(bbox)].tile

        if tiles.size == 0:
            raise ValueError("No products available for the specified bounds "
                             " and EPSG.")

        products = self.df[self.df.tile.isin(tiles)]

        products = products.sort_values('date',
                                        ascending=True)

        # drop data duplicated in overlapping zones
        # products = products_sorted.drop_duplicates(subset=['date'])
        return products

    def _clone(self,
               df=None,
               bands=None,
               start_date=None,
               end_date=None):
        """
        Returns an instance of self with updated parameters
        """
        new_collection = (self.__class__(self.df, self._s2grid) if df is None
                          else self.__class__(df, self._s2grid))
        new_collection.bands = self.bands if bands is None else bands
        new_collection._bounds = self._bounds
        new_collection._epsg = self._epsg
        new_collection._loader = self._loader
        new_collection.start_date = (self.start_date if start_date is None
                                     else start_date)
        new_collection.end_date = (self.end_date if end_date is None
                                   else end_date)

        return new_collection

    def load(self,
             bands=None,
             resolution=None,
             loader=None,
             resample=False):

        resolution = (resolution if resolution is not None
                      else self.supported_resolutions[0])

        if resolution not in self.supported_resolutions:
            raise NotImplementedError("Given resolution is not supported.")

        bands = bands if bands is not None else self.bands

        data_loader = loader if loader is not None else self.loader

        data = data_loader.load(self, bands, resolution,
                                resample=resample)

        return data

    def load_timeseries(self,
                        *bands,
                        **kwargs):
        from satio.timeseries import load_timeseries
        return load_timeseries(self, *bands, **kwargs)

    @staticmethod
    def _empty_df():
        columns = ['level', 'product_id', 'date', 'tile', 'path']
        df = pd.DataFrame([], columns=columns)
        return df


class GAMMA0Collection(DiskCollection):

    sensor = 'S1'
    processing_level = 'GAMMA0'

    @property
    def supported_bands(self):
        return ['VV', 'VH', 'angle', 'lsmap']

    @property
    def supported_resolutions(self):
        return [20]

    @staticmethod
    def _gamma_band(band):
        return {'VV': '_vv_PWR',
                'VH': '_vh_PWR',
                'angle': '_inc',
                'lsmap': '_lsmap'}.get(band)

    def get_band_filenames(self, band, resolution=20):
        if band not in self.supported_bands:
            raise ValueError(f"Band '{band}' is not supported. Supported "
                             f"bands: {self.supported_bands}")

        self._filenames = self.df['path'].apply(
            lambda x: x.replace('_vv_PWR', self._gamma_band(band)))

        return self._filenames.values.tolist()

    @staticmethod
    def get_file_size(filename):
        try:
            return Path(filename).stat().st_size / 1e6
        except Exception as e:
            return 0

    def filter_daily(self):

        def _get_day_orbit_id(product_id):
            s = product_id.split('_')
            day = s[4][:8]
            orbit = s[6]
            return f"{day}_{orbit}"

        if self.df.shape[0] == 0:
            return self

        df = self.df.copy()
        df['day'] = df.date.apply(lambda x: str(x)[:10])
        df['filesize'] = parallelize(self.get_file_size,
                                     self.get_band_filenames('VV'),
                                     progressbar=False,
                                     max_workers=4)
        df['day_orbit'] = df['product'].apply(_get_day_orbit_id)

        day_orbit_size = (df.groupby('day_orbit')['filesize']
                          .sum().to_frame().reset_index())
        df = pd.merge(df.drop(columns='filesize'),
                      day_orbit_size, on='day_orbit')
        keep_dayorbit = (df
                         .drop_duplicates('day_orbit')
                         .sort_values(['day', 'filesize'],
                                      ascending=[True, False])
                         .drop_duplicates('day')['day_orbit']
                         .values)

        df = df[df['day_orbit'].isin(keep_dayorbit)]

        return self._clone(df)

    def features_processor(
            self,
            settings: Dict,
            rsi_meta: Dict = {},
            features_meta: Dict = {},
            ignore_def_features: bool = False) -> GAMMA0FeaturesProcessor:

        return GAMMA0FeaturesProcessor(self,
                                       settings,
                                       rsi_meta=rsi_meta,
                                       features_meta=features_meta,
                                       ignore_def_features=ignore_def_features)


class TerrascopeSigma0Collection(GAMMA0Collection):

    sensor = 'S1'
    processing_level = 'SIGMA0'

    @property
    def supported_bands(self):
        return GAMMA_BANDS

    @property
    def supported_resolutions(self):
        return [10]

    @property
    def loader(self):
        if self._loader is None:
            self._loader = ParallelLoader(fill_value=np.nan)
        return self._loader

    def get_band_filenames(self, band, resolution):
        if self._filenames is None:
            self._filenames = self.df['path'].apply(
                lambda x: self.get_terrascope_filenames(x))

        tif_filenames = self._filenames.apply(
            lambda x: self.get_terrascope_band_filename(x, band, resolution))

        return tif_filenames.values.tolist()

    def features_processor(self,
                           settings: Dict,
                           rsi_meta: Dict = {},
                           features_meta: Dict = {},
                           ignore_def_features: bool = False) -> TSS0FeatProc:
        return TSS0FeatProc(self,
                            settings,
                            rsi_meta=rsi_meta,
                            features_meta=features_meta,
                            ignore_def_features=ignore_def_features)

    @staticmethod
    def get_terrascope_filenames(terrascope_product):
        filenames_list = glob.glob(str(Path(terrascope_product) / '*.tif'),
                                   recursive=True)
        filenames = {}
        resolution = 10

        for f in filenames_list:

            band = str(Path(f).stem).split('_')[-1].split('.')[0]

            filenames[band] = {resolution: f}

        return filenames

    @staticmethod
    def get_terrascope_band_filename(filenames, band, resolution=10):
        """Returns filename for band (TERRASCOPE product)
        closest to target resolution"""

        bands_10m = ['VV', 'VH', 'angle']

        if band not in bands_10m:
            raise ValueError("Band {} not supported.".format(band))

        return filenames[band][resolution]


class NoLoaderSet(Exception):
    pass


class AWSGAMMA0Collection(GAMMA0Collection):

    @property
    def loader(self):
        if self._loader is None:
            raise NoLoaderSet("Please set `loader` property to an "
                              "instance of AWSParallelLoader. Check the "
                              "class method `_get_loader()`")
        return self._loader

    @loader.setter
    def loader(self, value):
        self._loader = value

    @classmethod
    def from_file(cls,
                  aws_access_key_id,
                  aws_secret_access_key,
                  filename,
                  s2grid=None,
                  rio_gdal_options=None):

        df = pd.read_csv(filename)
        df.date = pd.to_datetime(df.date)
        df = df.sort_values('date', ascending=True)

        loader = cls._get_loader(aws_access_key_id,
                                 aws_secret_access_key,
                                 rio_gdal_options=rio_gdal_options)

        collection = cls(df, s2grid=s2grid)
        collection.loader = loader

        return collection

    @classmethod
    def from_folders(cls, *folders, s2grid=None):
        raise NotImplementedError

    @classmethod
    def from_bucket(cls,
                    aws_access_key_id,
                    aws_secret_access_key,
                    bucket='world-cover',
                    prefix='output/s1-preprocess/',
                    requester_pays=False,
                    globber_workers=50,
                    loader_workers=50,
                    s2grid=None,
                    rio_gdal_options=None,
                    loader_progressbar=False):

        client = S3BucketReader.from_credentials(aws_access_key_id,
                                                 aws_secret_access_key,
                                                 bucket=bucket,
                                                 requester_pays=requester_pays)

        folders = client.list_dirs(prefix)
        df = _build_aws_gamma0_products_df(
            client, folders, max_workers=globber_workers)

        loader = cls._get_loader(aws_access_key_id,
                                 aws_secret_access_key,
                                 rio_gdal_options,
                                 max_workers=loader_workers,
                                 progressbar=loader_progressbar)

        collection = cls(df, s2grid=s2grid)
        collection.loader = loader
        return collection

    @classmethod
    def _get_loader(cls,
                    aws_access_key_id,
                    aws_secret_access_key,
                    rio_gdal_options=None,
                    max_workers=50,
                    progressbar=False):

        if rio_gdal_options is None:
            rio_gdal_options = {
                'GDAL_DISABLE_READDIR_ON_OPEN': 'EMPTY_DIR',
                'CPL_VSIL_CURL_ALLOWED_EXTENSIONS': 'tif',
                'VSI_CACHE': False}

        loader = AWSParallelLoader(aws_access_key_id,
                                   aws_secret_access_key,
                                   rio_gdal_options=rio_gdal_options,
                                   max_workers=max_workers,
                                   progressbar=progressbar)

        return loader


class S2Collection(DiskCollection):

    sensor = 'S2'

    @property
    def supported_resolutions(self):
        return [10, 20, 60]


class L1CCollection(S2Collection):

    processing_level = 'L1C'

    def __init__(self, df, s2grid=None):
        super().__init__(df, s2grid=s2grid)
        self.df = self.df[self.df.level == self.processing_level]

    @property
    def supported_bands(self):
        return L2A_BANDS

    def get_band_filenames(self, band, resolution):
        raise NotImplementedError


class L2ACollection(S2Collection):

    processing_level = 'L2A'

    def __init__(self, df, s2grid=None):
        super().__init__(df, s2grid=s2grid)
        self.df = self.df[self.df.level == self.processing_level]

    @property
    def supported_bands(self):
        return L2A_BANDS + ['SCL']

    def filter_nodata(self,
                      resolution=60,
                      mask_values=[0, 1, 3, 8, 9, 10],
                      mask_th=0.05):
        """
        Load SCL mask and filter collection based on the relative amount
        of valid pixels. Minimum is specified by `mask_th`.
        e.g. a frame is valid if the mean of the binary mask obtained by
        `SCL != mask_values` is above `mask_th`. Or in other words,
        keep frames with more than `mask_th * 100` % valid pixels.
        """
        scl_60 = self.load(['SCL'], resolution=resolution)['SCL']

        valid_mask = ~np.isin(scl_60.data, mask_values)
        valid_ids = np.where(valid_mask.mean(axis=(1, 2)) > mask_th)[0]

        return self._clone(df=self.df.iloc[valid_ids])

    def get_band_filenames(self, band, resolution):
        if self._filenames is None:
            self._filenames = self.df['path'].apply(
                lambda x: get_l2a_filenames(x))

        jp2_filenames = self._filenames.apply(
            lambda x: get_jp2_filenames(x, band, resolution))

        return jp2_filenames.values.tolist()

    def features_processor(self,
                           settings: Dict,
                           rsi_meta: Dict = {},
                           features_meta: Dict = {},
                           ignore_def_features: bool = False) -> L2AFeatProc:
        return L2AFeatProc(self,
                           settings,
                           rsi_meta=rsi_meta,
                           features_meta=features_meta,
                           ignore_def_features=ignore_def_features)

    def features_processor_seas(
            self,
            settings: Dict,
            rsi_meta: Dict = {},
            features_meta: Dict = {},
            ignore_def_features: bool = False) -> L2AFeatProcSeas:
        return L2AFeatProcSeas(self,
                               settings,
                               rsi_meta=rsi_meta,
                               features_meta=features_meta,
                               ignore_def_features=ignore_def_features)


class MAJACollection(S2Collection):

    processing_level = 'MAJA'

    @property
    def supported_bands(self):
        return MAJA_BANDS + MAJA_MASKS

    def get_band_filenames(self, band, resolution):
        if self._filenames is None:
            self._filenames = self.df['path'].apply(
                lambda x: get_maja_filenames(x))

        jp2_filenames = self._filenames.apply(
            lambda x: get_maja_band_filename(x, band, resolution))

        return jp2_filenames.values.tolist()

    def features_processor(self,
                           settings: Dict,
                           rsi_meta: Dict = {},
                           features_meta: Dict = {},
                           ignore_def_features: bool = False) -> MAJAFeaturesProcessor:  # NOQA
        return MAJAFeaturesProcessor(self,
                                     settings,
                                     rsi_meta=rsi_meta,
                                     features_meta=features_meta,
                                     ignore_def_features=ignore_def_features)


class ICORCollection(S2Collection):

    processing_level = 'ICOR'

    @property
    def supported_bands(self):
        return ICOR_BANDS + ICOR_MASKS

    def get_band_filenames(self, band, resolution):
        if self._filenames is None:
            self._filenames = self.df['path'].apply(
                lambda x: get_icor_filenames(x))

        tif_filenames = self._filenames.apply(
            lambda x: get_icor_band_filename(x, band, resolution))

        return tif_filenames.values.tolist()

    def features_processor(self,
                           settings: Dict,
                           rsi_meta: Dict = {},
                           features_meta: Dict = {},
                           ignore_def_features: bool = False) -> ICORFeaturesProcessor:  # NOQA
        return ICORFeaturesProcessor(self,
                                     settings,
                                     rsi_meta=rsi_meta,
                                     features_meta=features_meta,
                                     ignore_def_features=ignore_def_features)


class TerrascopeV200Collection(S2Collection):

    processing_level = 'V200'

    @property
    def supported_bands(self):
        return TERRASCOPE_BANDS + TERRASCOPE_OPTIONAL_BANDS

    @classmethod
    def from_query(cls,
                   tile,
                   startdate,
                   enddate,
                   max_cloud_cover=95,
                   s2grid=None):

        s2_products = cls._query_products(tile,
                                          startdate,
                                          enddate,
                                          max_cloud_cover)

        df = create_terrascope_products_df(s2_products,
                                           tile,
                                           tile_to_epsg(tile),
                                           sensor='s2')

        return cls(df, s2grid)

    @staticmethod
    def _query_products(tile, startdate, enddate, max_cloud_cover=95):
        logger.info(f'Getting S2 products for tile {tile} ...')

        # Make a query to the catalog to retrieve an example file
        response = requests.get((f'{_TS_S2_BASEURL}_TOC_V2&tileId={tile}'
                                 f'&cloudCover=[0,{max_cloud_cover}]'
                                 f'&start={startdate}&end={enddate}'
                                 '&accessedFrom=MEP'))
        response = json.loads(response.text)

        if response['totalResults'] == 0:
            logger.warning('No Sentinel-2 products found.')
            return []

        products = []
        for acquisition in response['features']:
            for band in acquisition['properties']['links']['data']:
                if 'B08' in band['title']:
                    products.append(str(Path(band['href'][7:]).parent))

        while len(products) != response['totalResults']:
            response = requests.get(
                response['properties']['links']['next'][0]['href'])
            response = json.loads(response.text)
            for acquisition in response['features']:
                for band in acquisition['properties']['links']['data']:
                    if 'B08' in band['title']:
                        products.append(str(Path(band['href'][7:]).parent))
        return products

    def get_band_filenames(self, band, resolution):
        if self._filenames is None:
            self._filenames = self.df['path'].apply(
                lambda x: self.get_terrascope_filenames(x))

        tif_filenames = self._filenames.apply(
            lambda x: self.get_terrascope_band_filename(x, band, resolution))

        return tif_filenames.values.tolist()

    def filter_nodata(self,
                      resolution=60,
                      mask_values=[0, 1, 3, 8, 9, 10],
                      mask_th=0.05):
        """
        Load SCL mask and filter collection based on the relative amount
        of valid pixels. Minimum is specified by `mask_th`.
        e.g. a frame is valid if the mean of the binary mask obtained by
        `SCL != mask_values` is above `mask_th`. Or in other words,
        keep frames with more than `mask_th * 100` % valid pixels.
        """
        scl_60 = self.load(['SCENECLASSIFICATION'], resolution=resolution)[
            'SCENECLASSIFICATION']
        scl_60.data[scl_60.data == 32767] = 0

        valid_mask = ~np.isin(scl_60.data, mask_values)
        valid_ids = np.where(valid_mask.mean(axis=(1, 2)) > mask_th)[0]

        return self._clone(df=self.df.iloc[valid_ids])

    def features_processor(self,
                           settings: Dict,
                           rsi_meta: Dict = {},
                           features_meta: Dict = {},
                           ignore_def_features: bool = False) -> TSV2FeatProc:
        return TSV2FeatProc(self,
                            settings,
                            rsi_meta=rsi_meta,
                            features_meta=features_meta,
                            ignore_def_features=ignore_def_features)

    def features_processor_seas(
            self,
            settings: Dict,
            rsi_meta: Dict = {},
            features_meta: Dict = {},
            ignore_def_features: bool = False) -> TSV2FeatProcSeas:
        return TSV2FeatProcSeas(self,
                                settings,
                                rsi_meta=rsi_meta,
                                features_meta=features_meta,
                                ignore_def_features=ignore_def_features)

    @staticmethod
    def get_terrascope_filenames(terrascope_product):
        filenames_list = glob.glob(str(Path(terrascope_product) / '*.tif'),
                                   recursive=True)
        filenames = {}
        bands_10m = ['B02', 'B03', 'B04', 'B08']
        bands_20m = ['B05', 'B06', 'B07', 'B8A', 'B11', 'B12',
                     'SCENECLASSIFICATION']

        for f in filenames_list:
            if 'QUICKLOOK' in f:
                continue

            band = str(Path(f).stem).split('_')[3].split('-')[-1]

            if band in bands_10m:
                resolution = 10
            elif band in bands_20m:
                resolution = 20
            else:
                resolution = 60

            filenames[band] = {resolution: f}

        return filenames

    @staticmethod
    def get_terrascope_band_filename(filenames, band, resolution):
        """Returns filename for band (TERRASCOPE product)
        closest to target resolution"""

        bands_10m = ['B02', 'B03', 'B04', 'B08']
        bands_20m = ['B05', 'B06', 'B07', 'B8A', 'B11', 'B12',
                     'SCENECLASSIFICATION']
        bands_60m = ['VZA', 'SZA', 'RAA']

        if band in bands_10m:
            resolution = 10
        elif band in bands_20m:
            resolution = 20
        elif band in bands_60m:
            resolution = 60
        else:
            raise ValueError("Band {} not supported.".format(band))

        return filenames[band][resolution]


class L2AAWSCOGSCollection(L2ACollection):

    @classmethod
    def from_query(cls,
                   *,
                   bounds,
                   epsg,
                   tiles=None,
                   start_date='2001-01-01',
                   end_date='2100-01-01',
                   max_cloudcover=100,
                   s2grid=None):

        from satsearch import Search
        bbox_bounds = cls._get_latlon_bbox(bounds, epsg)

        search = Search(url='https://earth-search.aws.element84.com/v0',
                        bbox=bbox_bounds,
                        datetime=f'{start_date}/{end_date}',
                        query={'eo:cloud_cover': {'lt': max_cloudcover},
                               'eo:bands': ['B02']
                               },
                        collections=['sentinel-s2-l2a-cogs'])

        df = cls._get_search_df(search)

        coll = cls(df, s2grid=s2grid)

        coll._bounds = bounds
        coll._epsg = epsg
        coll._start_date = parse(start_date)
        coll._end_date = parse(end_date)

        if tiles is not None:
            coll = coll.filter_tiles(*tiles)

        return coll

    @property
    def loader(self):
        if self._loader is None:
            self._loader = AWSCOGSLoader()
        return self._loader

    @loader.setter
    def loader(self, value):
        self._loader = value

    @classmethod
    def from_folders(cls, *folders, s2grid):
        raise NotImplementedError("This method is not available"
                                  " for this collection.")

    def get_band_filenames(self, band, resolution=None):
        filenames = self.df.path.apply(lambda x: f'{x}/{band}.tif')
        return filenames.values.tolist()

    @staticmethod
    def _get_latlon_bbox(bounds, epsg):
        gs = gpd.GeoDataFrame([Polygon.from_bounds(*bounds)],
                              columns=['geometry'],
                              crs=CRS.from_epsg(epsg))
        gs['geometry'] = gs.centroid
        gs = gs.to_crs(epsg=4326)
        bbox = gs.buffer(0.00001)
        bbox = gs.iloc[0].geometry

        return bbox.bounds

    @staticmethod
    def _get_search_df(search):

        items_coll = search.items()

        urls = [it.assets['B02']['href'] for it in items_coll._items]

        entries = [l2a_aws_cog_entry(url) for url in urls]

        df = pd.DataFrame(entries)

        return df


def l2a_aws_cog_entry(url):
    """
    Returns dictionary of sentinel 2 product with specifications from filename
    """
    product_url = url[:-8]  # remove file suffix /B02.tif
    s3_path = product_url.replace(
        'https://sentinel-cogs.s3.us-west-2.amazonaws.com/',
        's3://sentinel-cogs/')

    product_id = Path(product_url).name

    mission_id, tile, date, date_idx, level = product_id.split('_')

    entry = dict(level=level,
                 product_id=product_id,
                 mission_id=mission_id,
                 date=datetime.strptime(f'{date}T{date_idx}', '%Y%m%dT%S'),
                 tile=tile,
                 path=s3_path,
                 url=product_url)

    return entry


TC = TypeVar('TC', bound='TrainingCollection')


class TrainingCollection:

    sensor = None
    processing_level = None

    def __init__(self,
                 df: pd.DataFrame,
                 dataformat: str = 'ewoco'):

        if dataformat not in ['ewoco', 'worldcereal']:
            raise ValueError(('"dataformat" should be one of '
                              '["ewoco", "worldcereal"] but '
                              f'got "{dataformat}"'))

        self.df = df
        self._location_ids = None
        self._dataformat = dataformat

    def _clone(self, df):
        return self.__class__(df, dataformat=self._dataformat)

    @classmethod
    def from_folder(cls,
                    folder: str,
                    pattern: str = r'\d{7}',
                    level: int = None) -> TC:

        if level is None:
            locs_subfolders = glob_subfolder(folder, pattern)
        else:
            locs_subfolders = glob_level_subfolders(folder, level=level)

        entries = list(map(cls._get_tloc_entry, locs_subfolders))
        df = pd.DataFrame(entries)
        return cls(df)

    @classmethod
    def from_file(cls, file: str) -> TC:
        df = pd.read_csv(file)
        return cls(df)

    @classmethod
    def from_path(cls, path, level=None):
        """
        If path is a folder, level specifies how many levels down the directory
        tree the .nc files are located.
        E.g. if the structure is path/{epsg}/{tile}/{location_id}/{filename}.nc
        then level will be 3. This speeds up the globbing of the files
        """
        path = Path(path)
        if path.is_file():
            return cls.from_file(path)
        elif path.is_dir():
            return cls.from_folder(path, level=level)
        else:
            raise ValueError(f'{path} is neither a folder nor a file.')

    def save(self, filename: str):
        self.df.to_csv(filename, index=False)

    @property
    def location_ids(self) -> List:
        return self.df.location_id.values.tolist()

    @staticmethod
    def _get_tloc_entry(path: str) -> Dict:
        s = path.split('/')
        location_id = int(s[-1])
        tile = s[-2]
        epsg = s[-3]
        return dict(location_id=location_id,
                    tile=tile,
                    epsg=epsg,
                    path=path)

    def filter_location(self, *location_ids) -> TC:
        new_df = self.df[self.df.location_id.isin(location_ids)]
        if new_df.shape[0] == 0:
            raise EmptyCollection("No products in collection for given "
                                  f"location_ids: '{location_ids}'")

        return self._clone(new_df)

    def filter_tiles(self, *tiles) -> TC:
        new_df = self.df[self.df.location_id.isin(tiles)]
        return self._clone(new_df)

    def _load_ewoco(self,
                    row,
                    bands) -> Dict:

        nc_files = glob.glob(os.path.join(row['path'], '*nc'))

        avail_bands = list(map(lambda x: os.path.basename(x).split('_')[2],
                               nc_files))

        if bands is None:
            bands = avail_bands

        for b in bands:
            if b not in avail_bands:
                raise ValueError("Given band is not available."
                                 f"Available bands: {avail_bands}")

        nc_bands_files = {b: [f for f in nc_files if b in f][0]
                          for b in bands}
        xarrs = {b: xr.open_dataarray(nc_bands_files[b]) for b in bands}

        return xarrs

    def _load_worldcereal(self,
                          row,
                          bands,
                          mask_and_scale=False) -> Dict:
        nc_files = glob.glob(
            os.path.join(
                row['path'],
                f'*{self.sensor}*{self.processing_level}*nc'))

        avail_bands = dict()

        for nc_file in nc_files:
            ds = xr.open_dataset(nc_file, engine='h5netcdf',
                                 mask_and_scale=mask_and_scale)
            avail_bands.update(dict.fromkeys(ds.keys(), nc_file))
            if 'spatial_ref' in avail_bands.keys():
                avail_bands.pop('spatial_ref')

        if bands is None:
            bands = list(avail_bands.keys())

        for b in bands:
            if b not in avail_bands:
                raise ValueError("Given band is not available."
                                 f"Available bands: {avail_bands}")

        xarrs = {b: xr.open_dataset(
            avail_bands[b], engine='h5netcdf',
            mask_and_scale=mask_and_scale)[b] for b in bands}

        for b in xarrs.keys():
            if xarrs[b].values.dtype == np.float64:
                # Cast to float32
                xarrs[b].values = xarrs[b].values.astype(np.float32)

        # broadcast angle bands to dimensions (timestamp, y, x)
        angle_bands = [b for b in xarrs.keys() if b in
                       ['sunAzimuthAngles', 'sunZenithAngles',
                        'viewAzimuthMean', 'viewZenithMean']]
        if len(angle_bands) > 0:
            timeco = xarrs[b].coords['timestamp']  # type: ignore
            yco = np.arange(start=1, stop=33, step=1, dtype='int32')
            for b in angle_bands:
                newdata = np.empty((32, 32, xarrs[b].shape[0]))
                newdata[:] = xarrs[b].data
                newdata = np.transpose(newdata, (2, 0, 1))
                newxarr = xr.DataArray(data=newdata,
                                       dims=['timestamp', 'y', 'x'],
                                       coords=[timeco, yco, yco],
                                       attrs=xarrs[b].attrs)
                xarrs[b] = newxarr

        return xarrs

    def _load_openeo(self,
                     row,
                     bands) -> Dict:

        # TODO: use TempFile
        translation = {
            "B02": "TOC-B02_10M",
            "B03": "TOC-B03_10M",
            "B04": "TOC-B04_10M",
            "B05": "TOC-B05_20M",
            "B06": "TOC-B06_20M",
            "B07": "TOC-B07_20M",
            "B08": "TOC-B08_10M",
            "B11": "TOC-B11_20M",
            "B12": "TOC-B12_20M",
            "SCL": "SCENECLASSIFICATION_20M"
        }
        import openeo.rest
        import openeo.rest.conversions
        oeoarr = {}
        igeom = row['geometry']
        extent = dict(zip(["west", "south", "east", "north"], igeom.bounds))
        eoconn = openeo.connect('https://openeo.vito.be')
        eoconn.authenticate_basic('satio', 'satio123')

        for iband in bands:

            with tempfile.NamedTemporaryFile() as f:
                tmpf = f.name
                ibandname = translation[iband]
                (eoconn
                 .load_collection('TERRASCOPE_S2_TOC_V2', bands=[ibandname])
                 .filter_temporal(row['start_date'], row['end_date'])
                 .filter_bbox(**extent)
                 .download(tmpf, format="json"))

                # calling the private loader because the direct datarray load
                # requires openeo-udf
                oa = openeo.rest.conversions._load_DataArray_from_JSON(tmpf)
                oa = (oa
                      .rename({'t': 'timestamp'})[:, 0, :, :]
                      .astype(np.uint16))

                # changing resolution divisible by 2 (otherwise up and
                # downsamplings result in mismatching shapes)
                xsize = (oa.shape[-2] >> 1) * 2
                ysize = (oa.shape[-1] >> 1) * 2
                oa = oa[:, :xsize, :ysize]

                # downsampling because for L2A openeo returns everything
                # on 10m resolution
                if ibandname.split('_')[-1].upper() != '10M':
                    oa = oa[:, ::2, ::2]
                oeoarr[iband] = oa

        return oeoarr

    def load(self,
             bands: List = None,
             resolution: int = None,
             location_id: int = None,
             mask_and_scale: bool = False,
             force_dtype: type = np.uint16) -> Dict:

        if mask_and_scale:
            raise ValueError(('`mask_and_scale=True` is not supported'
                              ' for this collection.'))

        if location_id is None:
            # get first location available
            location_id = self.location_ids[0]

        row = self.df[self.df.location_id == location_id].iloc[0]

        path = row['path']

        if not os.path.isdir(path):
            raise FileNotFoundError(f"{path} not found.")

        # Here we split up the worldcover and worldcereal approaches
        # if self._dataformat == 'openeo':
        #     return self._load_openeo(row, bands)

        if self._dataformat == 'worldcereal':
            xarrs = self._load_worldcereal(row,
                                           bands,
                                           mask_and_scale=mask_and_scale)

        elif self._dataformat == 'ewoco':
            xarrs = self._load_ewoco(row, bands)

        else:
            raise ValueError("Please set `self._dataformat` to either"
                             "'ewoco' or 'worldcereal")
        # monkey patch for points in int16 instead of uint16
        if force_dtype:
            for b in xarrs.keys():
                if not b == 'SCL':
                    xarrs[b] = xarrs[b].astype(force_dtype)

        return xarrs

    def load_timeseries(self,
                        *bands,
                        mask_and_scale=False,
                        dataformat=None,
                        **kwargs):
        '''
        "mask_and_scale" flag allows to apply encoded scale/offse
        from netcdf file returning physical data instead of scaled values
        '''
        from satio.timeseries import load_timeseries

        if dataformat is not None:
            self._dataformat = dataformat

        return load_timeseries(self, *bands, mask_and_scale=mask_and_scale,
                               **kwargs)


class L2ATrainingCollection(TrainingCollection):

    sensor = 'S2'
    processing_level = 'L2A'

    def features_processor(self,
                           settings: Dict,
                           rsi_meta: Dict = {},
                           features_meta: Dict = {},
                           ignore_def_features: bool = False) -> L2AFeatProc:
        return L2AFeatProc(self,
                           settings,
                           rsi_meta=rsi_meta,
                           features_meta=features_meta,
                           ignore_def_features=ignore_def_features)

    def features_processor_seas(
            self,
            settings: Dict,
            rsi_meta: Dict = {},
            features_meta: Dict = {},
            ignore_def_features: bool = False) -> L2AFeatProcSeas:
        return L2AFeatProcSeas(self,
                               settings,
                               rsi_meta=rsi_meta,
                               features_meta=features_meta,
                               ignore_def_features=ignore_def_features)


class GAMMA0TrainingCollection(TrainingCollection):

    sensor = 'S1'
    processing_level = 'GAMMA0'

    def features_processor(self, settings, *args, **kwargs):
        return GAMMA0FeaturesProcessor(self, settings, *args, **kwargs)


class SIGMA0TrainingCollection(TrainingCollection):
    '''
    A collection for Sigma0 data extracted from GEE
    '''

    sensor = 'S1'
    processing_level = '*'

    def features_processor(self, settings, *args, **kwargs):
        return SIGMA0FeaturesProcessor(self, settings, *args, **kwargs)

    def load(self,
             bands: List = None,
             resolution: int = None,
             location_id: int = None,
             mask_and_scale: bool = False) -> Dict:
        '''
        Override of parent class method to support native
        Int32 datatype of GEE-processed sigma0
        '''

        if location_id is None:
            # get first location available
            location_id = self.location_ids[0]

        row = self.df[self.df.location_id == location_id].iloc[0]
        path = row['path']

        if not os.path.isdir(path):
            raise FileNotFoundError(f"{path} not found.")

        # Here we split up the worldcover and worldcereal approaches
        if self._dataformat == 'worldcereal':
            xarrs = self._load_worldcereal(row, bands,
                                           mask_and_scale=mask_and_scale)
        else:
            xarrs = self._load_satio(row, bands)

        return xarrs


class LabelsTrainingCollection(TrainingCollection):

    sensor = 'LC'
    processing_level = 'LABELS'

    def load(self, location_id: int = None) -> Dict:
        """
        Load a labels array of a given location_id. If no location_id is
        specified, the first available location_id is loaded.
        """
        if location_id is None:
            # get first location available
            location_id = self.location_ids[0]

        row = self.df[self.df.location_id == location_id]

        if row.shape[0] > 0:
            row = row.iloc[0]
        else:
            raise EmptyCollection(f"'location_id': {location_id} not "
                                  "in collection.")

        path = row['path']

        if not os.path.isdir(path):
            raise FileNotFoundError(f"{path} not found.")

        nc_files = glob.glob(os.path.join(row['path'], '*npy'))

        return np.load(nc_files[0])


class PatchLabelsTrainingCollection(TrainingCollection):

    sensor = 'OUTPUT'
    processing_level = '*'

    def load(self, bands: List = None,
             location_id: int = None) -> Dict:
        """
        Load a labels array of a given location_id. If no location_id is
        specified, the first available location_id is loaded.
        """
        if location_id is None:
            # get first location available
            location_id = self.location_ids[0]

        row = self.df[self.df.location_id == location_id].iloc[0]
        path = row['path']

        if not os.path.isdir(path):
            raise FileNotFoundError(f"{path} not found.")

        nc_files = glob.glob(
            os.path.join(
                row['path'],
                f'*{self.sensor}*{self.processing_level}*nc'))

        avail_bands = dict()

        for nc_file in nc_files:
            ds = xr.open_dataset(nc_file, engine='h5netcdf',
                                 mask_and_scale=False)
            avail_bands.update(dict.fromkeys(ds.keys(), nc_file))
            if 'spatial_ref' in avail_bands.keys():
                avail_bands.pop('spatial_ref')

        if bands is None:
            bands = list(avail_bands.keys())

        for b in bands:
            if b not in avail_bands:
                raise ValueError("Given band is not available."
                                 f"Available bands: {avail_bands}")

        xarrs = {b: xr.open_dataset(
            avail_bands[b], engine='h5netcdf',
            mask_and_scale=False)[b] for b in bands}

        return xarrs


class XArrayTrainingCollection(TrainingCollection):
    """
    A very simple collection that simply wraps an in-memory xarray.
    """

    def __init__(self, sensor: str, processing_level: str,
                 df: pd.DataFrame, array: xr.DataArray):
        """

        @param sensor:
        @param processing_level:
        @param df:
        @param array: an xarray, with dimensions: (bands,timestamp,x,y)
        """
        super().__init__(df)
        self.sensor = sensor
        self.processing_level = processing_level
        self.array = array
        assert 'timestamp' in self.array.dims

    def load(self,
             bands: List = None,
             resolution: int = None,
             location_id: int = None,
             mask_and_scale: bool = False) -> Dict:

        def get_band(b):
            data = self.array.sel(bands=b)
            if 'SCL' in b:
                # satio makes the assumption that SCL is 20M
                data = data[:, ::2, ::2]
            return data

        bands_dict = {b: get_band(b) for b in bands}

        return bands_dict


class AgERA5TrainingCollection(TrainingCollection):

    sensor = 'AgERA5'
    processing_level = 'DAILY'

    def load(self,
             bands: List = None,
             resolution: int = None,
             location_id: int = None,
             mask_and_scale: bool = False,
             force_dtype: type = np.float32) -> Dict:
        '''
        Override from parent method to load meteo as float32
        '''

        return super().load(bands, resolution, location_id,
                            mask_and_scale, force_dtype)


FC = TypeVar('FC', bound='FolderCollection')


class FolderCollection(ABC):
    """
    Load data from a folder containing a global raster split in S2 tiles.
    """

    def __init__(self, folder, loader=None, s2grid=None):

        self.folder = Path(folder)

        self._loader = (loader if loader is not None
                        else ParallelLoader())
        self._s2grid = s2grid
        self._bounds = None
        self._epsg = None
        self._tile = None

    @property
    def s2grid(self):
        if self._s2grid is None:
            self._s2grid = satio.layers.load('s2grid')
        return self._s2grid

    @abstractmethod
    def _filename(self, tile):
        """
        Return the filename for the raster of given tile
        """
        ...

    def _clone(self, bounds=None, epsg=None, tile=None) -> FC:
        new_cls = self.__class__(self.folder,
                                 self._loader,
                                 self._s2grid)

        new_cls._bounds = bounds if bounds is not None else self._bounds
        new_cls._epsg = epsg if epsg is not None else self._epsg
        new_cls._tile = tile if tile is not None else self._tile

        return new_cls

    def filter_tile(self, tile) -> FC:
        return self._clone(tile=tile)

    def filter_bounds(self, bounds, epsg) -> FC:
        return self._clone(bounds=bounds, epsg=epsg)

    def _get_closest_tile(self, bounds, epsg):
        s2grid = self.s2grid
        box = gpd.GeoSeries(Polygon.from_bounds(*bounds),
                            crs=CRS.from_epsg(epsg))
        box = box.to_crs(epsg=4326)

        tgrid = s2grid[s2grid.epsg == epsg]
        tgrid = tgrid[tgrid.intersects(box.unary_union)]

        if tgrid.shape[0] > 1:

            tgrid['distance'] = tgrid.to_crs(epsg=epsg).centroid.distance(
                box.to_crs(epsg=epsg).centroid.iloc[0])
            tgrid = tgrid.sort_values('distance', ascending=True)

        tile = tgrid.iloc[0].tile

        return tile

    def load(self):

        tile, bounds, epsg = self._tile, self._bounds, self._epsg

        if tile is None:
            if (self._bounds is None) | (self._epsg is None):
                raise ValueError("'bounds' and 'epsg' should be set by"
                                 " 'filter_bounds' method before loading data,"
                                 " when 'filter_tile' was not use to specify"
                                 " at least the tile id.")
            tile = self._get_closest_tile(bounds, epsg)

        filename = self._filename(tile)

        if bounds is None:
            with rasterio.open(filename, 'r') as src:
                arr = np.squeeze(src.read())

        else:
            arr = self._loader._load_array_bounds(filename, bounds)
        return arr

    @property
    def loader(self):
        if self._loader is None:
            self._loader = ParallelLoader()
        return self._loader

    @loader.setter
    def loader(self, value):
        self._loader = value


class DEMCollection(FolderCollection):

    def _filename(self, tile, *args, **kwargs):
        return self.folder / f'dem_{tile}.tif'


class WorldCoverCollection(FolderCollection):

    def _filename(self, tile, *args, **kwargs):
        return (self.folder /
                f'{tile}_ESA_WorldCover_2020_10m.tif')


class OSMCollection(FolderCollection):

    def __init__(self,
                 folder,
                 loader=None,
                 s2grid=None,
                 year=2019):
        super().__init__(folder, loader=loader, s2grid=s2grid)
        self._year = year

    def _filename(self, tile):
        return self.folder / f"OSM_{self._year}_10m_{tile}.tif"


class WSFCollection(FolderCollection):

    def _filename(self, tile):
        return self.folder / f"WSF_2015_10m_{tile}.tif"


class GSWCollection(FolderCollection):

    def _filename(self, tile):
        return self.folder / f"GSW_2019_{tile}_20m.tif"


class GMWCollection(FolderCollection):

    def _filename(self, tile):
        return self.folder / f"GMW_2016_300_{tile}.tif"


def _get_agera5_entry(fn):
    split = fn.split('/')

    entry = dict(
        product=f'AgERA5_{split[-1]}',
        date=parse(split[-1]),
        path=fn,
        tile='global',
        epsg=4326,
    )

    return entry


def build_agera_products_df(agera_path):
    names = glob_level_subfolders(agera_path, level=2)
    entries = list(map(_get_agera5_entry, names))
    return pd.DataFrame(entries)


class AgERA5Collection(DiskCollection):

    sensor = 'AgERA5'

    def __init__(self, df, s2grid=None):
        self.df = df.sort_values('date')
        self.tiles = sorted(self.df.tile.unique().tolist())
        self.start_date = datetime(2000, 1, 1)
        self.end_date = datetime(2100, 1, 1)

        self._s2grid = s2grid

        self._bounds = None
        self._filenames = None
        self._bands = None
        self._epsg = None
        self._sensor = NotImplementedError
        self._loader = WarpLoader(max_workers=40,
                                  progressbar=False,
                                  buffer_bounds=15000)

    @classmethod
    def from_path(cls, path, s2grid=None):
        path = Path(path)
        if path.is_file():
            return cls.from_file(path, s2grid=s2grid)
        elif path.is_dir():
            return cls.from_folder(path, s2grid=s2grid)
        else:
            raise ValueError(f'{path} is neither a folder nor a file.')

    @classmethod
    def from_folder(cls, folder, s2grid=None):
        df = build_agera_products_df(folder)
        df = df.sort_values('date', ascending=True)
        collection = cls(df, s2grid=s2grid)
        return collection

    def get_band_filenames(self, band, resolution=None):
        filenames = self.df.apply(
            lambda x:
            f"{x.path}/AgERA5_{band}_"
            f'{datetime.strftime(x.date, "%Y%m%d")}.tif',
            axis=1)
        return filenames.values.tolist()

    @property
    def supported_bands(self):
        return AGERA5_BANDS

    @property
    def supported_resolutions(self):
        return [10, 20, 60, 100, 1000, 10000]

    def filter_bounds(self, bounds, epsg):
        new = self._clone()
        new._bounds = bounds
        new._epsg = epsg
        return new

    def load_timeseries(self,
                        *bands,
                        resolution=100,
                        resampling=Resampling.cubic_spline,
                        **kwargs):
        '''
        Override default method to deal
        with scaling and change the band names
        '''

        from satio.timeseries import Timeseries

        AGERA5ATTRS = {
            'dewpoint-temperature': {
                'scale': 0.01,
                'nodata': 65535
            },
            'precipitation-flux': {
                'scale': 0.01,
                'nodata': 65535
            },
            'solar-radiation-flux': {
                'scale': 1,
                'nodata': 0
            },
            'temperature-min': {
                'scale': 0.01,
                'nodata': 65535
            },
            'temperature-max': {
                'scale': 0.01,
                'nodata': 65535
            },
            'temperature-mean': {
                'scale': 0.01,
                'nodata': 65535
            },
            'vapour-pressure': {
                'scale': 0.001,
                'nodata': 0
            },
            'wind-speed': {
                'scale': 0.01,
                'nodata': 65535
            }
        }

        bands = [band.replace('_', '-') for band in bands]

        scaled_ts = None

        for band in bands:

            src_nodata = dst_nodata = AGERA5ATTRS[band]['nodata']
            scale = AGERA5ATTRS[band]['scale']

            ts = self._loader.load(self, [band], resolution,
                                   src_nodata=src_nodata,
                                   dst_nodata=dst_nodata,
                                   resampling=resampling)

            ts.data = ts.data.astype(np.float32)

            ts_banddata = ts[band].data
            ts_banddata[ts_banddata == src_nodata] = np.nan
            ts_banddata = ts_banddata * scale

            ts_band = Timeseries(
                data=ts_banddata,
                timestamps=ts.timestamps,
                bands=[band.replace('-', '_')],
                attrs=ts.attrs
            )
            scaled_ts = (ts_band if scaled_ts is None
                         else scaled_ts.merge(ts_band))

        return scaled_ts
