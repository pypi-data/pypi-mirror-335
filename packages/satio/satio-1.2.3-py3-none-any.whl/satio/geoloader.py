import concurrent.futures
import json
import os
import random
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List

import boto3
import geopandas as gpd
import numpy as np
import rasterio
import xarray as xr
from loguru import logger
from rasterio.crs import CRS
from rasterio.enums import Resampling
from rasterio.errors import RasterioIOError
from rasterio.session import AWSSession
from rasterio.warp import reproject
from shapely.geometry import Polygon
from skimage.transform import rescale
from tqdm.auto import tqdm

from satio.utils import timeout
from satio.utils.retry import retry

S2_BANDS = "B01,B02,B03,B04,B05,B06,B07,B08,B8A,B09,B10,B11,B12".split(",")

L2A_BANDS = S2_BANDS + ["SCL"]

L2A_HRES_BANDS = [
    "B02",
    "B03",
    "B04",
    "B05",
    "B06",
    "B07",
    "B08",
    "B8A",
    "B11",
    "B12",
    "SCL",
]

L1C_BANDS = S2_BANDS
GRD_BANDS = ["VV", "VH"]
FEATURE_TYPES = ["L2A", "L1C", "GRD-DESCENDING", "GRD-ASCENDING", "GOOGLEMAPS"]

L2A_10M_BANDS = ["AOT", "B02", "B03", "B04", "B08", "TCI", "WVP"]
L2A_20M_BANDS = [
    "AOT",
    "B02",
    "B03",
    "B04",
    "B05",
    "B06",
    "B07",
    "B08",
    "B11",
    "B12",
    "B8A",
    "SCL",
    "TCI",
    "WVP",
]
L2A_60M_BANDS = [
    "AOT",
    "B01",
    "B02",
    "B03",
    "B04",
    "B05",
    "B06",
    "B07",
    "B08",
    "B09",
    "B10",
    "B11",
    "B12",
    "B8A",
    "SCL",
    "TCI",
    "WVP",
]

L2A_RES_BANDS = [L2A_10M_BANDS, L2A_20M_BANDS, L2A_60M_BANDS]

RETRIES = int(os.environ.get("SATIO_RETRIES", 50))
DELAY = int(os.environ.get("SATIO_DELAY", 5))
BACKOFF = int(os.environ.get("SATIO_BACKOFF", 1))
TIMEOUT = int(os.environ.get("SATIO_TIMEOUT", 30))


class ParallelLoader:
    def __init__(
        self,
        max_workers=20,
        progressbar=False,
        rio_gdal_options=None,
        fill_value=0,
        random_order=True,
    ):
        self._max_workers = max_workers
        self._progressbar = progressbar

        if rio_gdal_options is None:
            rio_gdal_options = {"GDAL_CACHEMAX": 0}

        self._rio_gdal_options = rio_gdal_options
        self._fill_value = fill_value
        self._random_order = random_order

    def _load_array_bounds(self, fname, bounds):
        with rasterio.Env(**self._rio_gdal_options):
            with rasterio.open(fname) as src:
                window = rasterio.windows.from_bounds(*bounds, src.transform)

                vals = np.array(window.flatten())
                if (vals % 1 > 0).any():
                    # logger.warning("Rounding floating window"
                    #                "offsets and shape")
                    window = window.round_lengths(op="ceil").round_offsets(
                        op="floor"
                    )

                arr = src.read(
                    window=window, boundless=True, fill_value=self._fill_value
                )

        arr = arr[0]
        return arr

    def _load_array_bounds_safe(self, fname, bounds, max_retries=50):
        """
        to be tested
        """
        with rasterio.Env(**self._rio_gdal_options):
            with rasterio.open(fname) as src:
                window = rasterio.windows.from_bounds(*bounds, src.transform)

                try:
                    arr = src.read(
                        window=window,
                        boundless=True,
                        fill_value=self._fill_value,
                    )
                    arr = np.squeeze(arr)

                except RasterioIOError as e:
                    if max_retries:
                        logger.error(
                            f"Error reading data from {fname}: {e}" " Retrying"
                        )
                        return self._load_array_bounds_safe(
                            fname, bounds, max_retries - 1
                        )
                    else:
                        logger.error(
                            f"Error reading data from {fname}: {e}"
                            " Returning an array of zeros."
                        )
                        arr = np.zeros((window.height, window.width))

        return arr

    def load_arrays(self, filenames, bounds):
        def f_handle(filename):
            return self._load_array_bounds(filename, bounds)

        if self._random_order:
            ids = list(range(len(filenames)))
            ids_random = ids.copy()
            random.shuffle(ids_random)
            ids_map = [ids_random.index(i) for i in ids]
            filenames = [filenames[i] for i in ids_random]

        arrs_list = self._run_parallel(
            f_handle,
            filenames,
            self._max_workers,
            threads=True,
            progressbar=self._progressbar,
        )

        if self._random_order:
            arrs_list = [arrs_list[i] for i in ids_map]

        return arrs_list

    def _load_raw(self, collection, bands, resolution=10):
        bounds = collection.bounds

        filenames = [
            f
            for band in bands
            for f in collection.get_band_filenames(band, resolution)
        ]

        arrs_list_flat = self.load_arrays(filenames, bounds)

        arrs_list = self._split_arrs_list(arrs_list_flat, n_bands=len(bands))

        return arrs_list

    def _split_arrs_list(
        self, arrs: List[np.ndarray], n_bands: int
    ) -> List[np.ndarray]:
        """
        'arrs' is a list of arrays with shape [y, x] loaded from filenames.
        The length of the list should be n_bands * n_timestamps.
        This function returns a list of leght n_bands with arrays of shape
        [n_timestamps, y, x].
        """
        n_timestamps = len(arrs) // n_bands
        if len(arrs) % n_bands:
            raise ValueError(
                "Number of files loaded is not a multiple "
                "of the number of bands as expected."
            )

        out_list = [
            np.array(arrs[n_timestamps * i : n_timestamps * (i + 1)])
            for i in range(n_bands)
        ]

        return out_list

    def load(self, collection, bands, resolution, resample=False):
        """
        Load data for the given bands. resolution should be 10 or 20.
        If resolution is 10, only 'B02', 'B03', 'B04' and 'B08' will be
        loaded at 10 m resolution, the rest at 20 m. Unless 'resample' is
        set to True. In that case, 20 m bands will be upsampled to 10 m with
        a bilinear filter (except 'SCL' which will be resampled with
        nearest neighbors method).
        """
        if not isinstance(bands, (list, tuple)):
            raise TypeError(
                "'bands' should be a list/tuple of bands. "
                f"Its type is: {type(bands)}"
            )
        if resolution not in [10, 20, 60]:
            raise ValueError(
                f"Resolution value: '{resolution}' not supported"
                " Should be 10, 20 or 60."
            )

        arrs_list = self._load_raw(collection, bands, resolution)

        if resample:
            arrs_list = self._resample(arrs_list, bands, resolution, order=1)

        products = collection.products
        timestamps = collection.timestamps
        bands = list(bands)
        bounds = list(collection.bounds)
        epsg = collection.epsg

        xds_dict = {
            band: self._arr_to_xarr(
                arrs_list[i], bounds, timestamps, name=band
            )
            for i, band in enumerate(bands)
        }

        xds_dict.update(
            {
                "epsg": epsg,
                "bounds": bounds,
                "products": products,
                "bands": bands,
            }
        )
        # xds = xr.Dataset(xds_dict)

        return xds_dict

    @staticmethod
    def _run_parallel(f, my_iter, max_workers, threads=True, progressbar=True):
        if threads:
            Pool = concurrent.futures.ThreadPoolExecutor
        else:
            Pool = concurrent.futures.ProcessPoolExecutor

        with Pool(max_workers=max_workers) as executor:
            if progressbar:
                results = list(
                    tqdm(executor.map(f, my_iter), total=len(my_iter))
                )
            else:
                results = list(executor.map(f, my_iter))

        return results

    def _resample(self, arrs, bands, resolution, order=1):
        if resolution == 20:
            return arrs

        elif resolution == 10:
            new_arrs = []
            for i, b in enumerate(bands):
                arr = arrs[i]

                if b not in L2A_10M_BANDS:
                    scale = 2
                    order = 0 if b == "SCL" else order
                    arr = self._resample_arr(arr, scale, order)

                new_arrs.append(arr)
        else:
            raise NotImplementedError(
                "Can only resample 10 m or 20 m bands" "resolution."
            )

        return new_arrs

    @staticmethod
    def _resample_arr(arr, scale, order):
        dtype_ori = arr.dtype
        arr = rescale(
            arr, scale=scale, order=order, preserve_range=True, channel_axis=0
        )
        arr = arr.astype(dtype_ori)
        return arr

    @staticmethod
    def _arr_resolution(arr, bounds):
        x_meters = bounds[2] - bounds[0]
        return x_meters // arr.shape[-1]

    def _arr_to_xarr(self, arr, bounds, timestamps, name=None):
        if arr.ndim == 1:
            # single pixel
            arr = np.expand_dims(arr, axis=-1)
            arr = np.expand_dims(arr, axis=-1)

        resolution = self._arr_resolution(arr, bounds)

        dims = ["timestamp", "y", "x"]
        dims = {k: arr.shape[i] for i, k in enumerate(dims)}

        center_shift = resolution / 2
        xmin, xmax = (bounds[0] + center_shift), (bounds[2] - center_shift)
        ymin, ymax = (bounds[1] + center_shift), (bounds[3] - center_shift)

        x = np.linspace(xmin, xmax, dims["x"])

        y = np.linspace(ymin, ymax, dims["y"])

        coords = {"timestamp": timestamps, "x": x, "y": y}

        da = xr.DataArray(
            arr,
            coords=coords,
            dims=dims,
            name=name,
            attrs={"resolution": resolution},
        )

        return da


class LandsatLoader(ParallelLoader):
    def load(self, collection, bands, resolution, resample=False):
        """
        Load data for the given bands. resolution should be 10 or 30.
        If resolution is 10, 'resample' should be set to True.
        In that case, 30 m bands will be upsampled to 10 m with
        a bilinear filter (except 'SCL' which will be resampled with
        nearest neighbors method).
        """
        if not isinstance(bands, (list, tuple)):
            raise TypeError(
                "'bands' should be a list/tuple of bands. "
                f"Its type is: {type(bands)}"
            )
        if resolution not in [10, 30]:
            raise ValueError(
                f"Resolution value: '{resolution}' not supported"
                " Should be 10 or 30."
            )

        loadres = 30
        # adjust bounds if not multiple of 30
        old_bounds = np.array(collection.bounds)
        shifts = np.array(
            [
                -(old_bounds[0] % 30),
                -(old_bounds[1] % 30),
                30 - (old_bounds[2] % 30),
                30 - (old_bounds[3] % 30),
            ]
        )
        shifts = np.where(shifts == 30, 0, shifts)
        new_bounds = old_bounds + shifts
        collection._bounds = new_bounds.tolist()

        arr_shifts = shifts / 10
        arr_shifts = arr_shifts.astype(np.int16)

        arrs_list = self._load_raw(collection, bands, loadres)

        if resample:
            arrs_list = self._resample(arrs_list, bands, resolution, order=1)

            arrs_list = [
                a[
                    :,
                    arr_shifts[3] : a.shape[1] + arr_shifts[1],
                    -arr_shifts[0] : a.shape[2] - arr_shifts[2],
                ]
                for a in arrs_list
            ]

        products = collection.products
        timestamps = collection.timestamps
        bands = list(bands)
        collection._bounds = list(old_bounds)
        bounds = list(collection.bounds)
        epsg = collection.epsg

        xds_dict = {
            band: self._arr_to_xarr(
                arrs_list[i], bounds, timestamps, name=band
            )
            for i, band in enumerate(bands)
        }

        xds_dict.update(
            {
                "epsg": epsg,
                "bounds": bounds,
                "products": products,
                "bands": bands,
            }
        )
        # xds = xr.Dataset(xds_dict)

        return xds_dict

    def _resample(self, arrs, bands, resolution, order=1):
        if resolution == 30:
            return arrs

        elif resolution == 10:
            new_arrs = []
            for i, b in enumerate(bands):
                arr = arrs[i]

                scale = 3
                order = 0 if b in ["QA", "PIXEL-QA"] else order
                arr = self._resample_arr(arr, scale, order)

                new_arrs.append(arr)
        else:
            raise NotImplementedError(
                "Can only resample 10 m or 30 m bands" "resolution."
            )

        return new_arrs


class S3ParallelLoader(ParallelLoader):
    def __init__(
        self,
        access_key_id=None,
        secret_access_key=None,
        region_name="eu-central-1",
        endpoint_url=None,
        rio_gdal_options=None,
        max_workers=20,
        fill_value=0,
        progressbar=False,
    ):
        boto3_session = boto3.Session(
            access_key_id, secret_access_key, region_name=region_name
        )

        if (access_key_id is None) or (secret_access_key is None):
            aws_unsigned = True
        else:
            aws_unsigned = False

        self._session = AWSSession(
            boto3_session, aws_unsigned=aws_unsigned, endpoint_url=endpoint_url
        )

        if rio_gdal_options is None:
            rio_gdal_options = {
                "AWS_REQUEST_PAYER": "requester",
                "GDAL_DISABLE_READDIR_ON_OPEN": "EMPTY_DIR",
                "CPL_VSIL_CURL_ALLOWED_EXTENSIONS": "jp2",
                "VSI_CACHE": False,
            }

        super().__init__(
            rio_gdal_options=rio_gdal_options,
            max_workers=max_workers,
            fill_value=fill_value,
            progressbar=progressbar,
        )

    @retry(
        exceptions=Exception,
        tries=RETRIES,
        delay=DELAY,
        backoff=BACKOFF,
        logger=logger,
    )
    @timeout(TIMEOUT, use_signals=False)
    def _load_array_bounds(self, fname, bounds):
        logger.debug(f"Start loading: {fname}")

        with rasterio.Env(session=self._session, **self._rio_gdal_options):
            with rasterio.open(fname) as src:
                window = rasterio.windows.from_bounds(*bounds, src.transform)
                arr = src.read(
                    window=window, boundless=True, fill_value=self._fill_value
                )

        # arr = np.squeeze(arr)
        arr = arr[0]

        logger.debug(f"End loading: {fname}")

        return arr


class S3LandsatLoader(S3ParallelLoader, LandsatLoader):
    def load(self, *args, **kwargs):
        return super().load(*args, **kwargs)

    def _resample(self, *args, **kwargs):
        return super()._resample(*args, **kwargs)


class AWSParallelLoader(ParallelLoader):
    def __init__(
        self,
        aws_access_key_id=None,
        aws_secret_access_key=None,
        region_name="eu-central-1",
        endpoint_url=None,
        rio_gdal_options=None,
        max_workers=20,
        fill_value=0,
        progressbar=False,
    ):
        boto3_session = boto3.Session(
            aws_access_key_id, aws_secret_access_key, region_name=region_name
        )

        if (aws_access_key_id is None) or (aws_secret_access_key is None):
            aws_unsigned = True
        else:
            aws_unsigned = False

        self._session = AWSSession(
            boto3_session, aws_unsigned=aws_unsigned, endpoint_url=endpoint_url
        )

        if rio_gdal_options is None:
            rio_gdal_options = {
                "AWS_REQUEST_PAYER": "requester",
                "GDAL_DISABLE_READDIR_ON_OPEN": "EMPTY_DIR",
                "CPL_VSIL_CURL_ALLOWED_EXTENSIONS": "jp2",
                "VSI_CACHE": False,
            }

        super().__init__(
            rio_gdal_options=rio_gdal_options,
            max_workers=max_workers,
            fill_value=fill_value,
            progressbar=progressbar,
        )

    def _load_array_bounds(self, fname, bounds):
        with rasterio.Env(session=self._session, **self._rio_gdal_options):
            with rasterio.open(fname) as src:
                window = rasterio.windows.from_bounds(*bounds, src.transform)
                arr = src.read(
                    window=window, boundless=True, fill_value=self._fill_value
                )

        # arr = np.squeeze(arr)
        arr = arr[0]
        return arr


class AWSCOGSLoader(AWSParallelLoader):
    def __init__(
        self,
        aws_access_key_id=None,
        aws_secret_access_key=None,
        region_name="us-west-2",
        rio_gdal_options=None,
        max_workers=100,
        fill_value=0,
    ):
        if rio_gdal_options is None:
            rio_gdal_options = {
                "GDAL_DISABLE_READDIR_ON_OPEN": "EMPTY_DIR",
                "GDAL_HTTP_MERGE_CONSECUTIVE_RANGES": "YES",
                "CPL_VSIL_CURL_ALLOWED_EXTENSIONS": "tif",
                "GDAL_HTTP_MULTIPLEX": "YES",
                "GDAL_HTTP_VERSION": "2",
                "VSI_CACHE": "FALSE",
                "VSI_CACHE_SIZE": 0,
                "GDAL_CACHEMAX": 0,
            }

        super().__init__(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name,
            rio_gdal_options=rio_gdal_options,
            max_workers=max_workers,
            fill_value=fill_value,
        )


class CorruptedL2AProduct(Exception):
    pass


def get_l2a_filenames(filename):
    filename = Path(filename)

    # check if it's a product downloaded from AWS
    aws_subs = ["R10m", "R20m", "R60m"]
    for asub in aws_subs:
        if (filename / asub).is_dir():
            return get_l2a_aws_filenames(filename)

    try:
        xml_manifest = "MTD_MSIL2A.xml"
        metadata = os.path.join(filename, xml_manifest)
        root = ET.parse(metadata).getroot()
        filenames = dict()
        if len(root[0][0][-1]) == 1:
            for i, resolution in enumerate([60, 20, 10]):
                filenames[resolution] = {
                    child.text.split("_")[-2]: os.path.join(
                        filename, child.text + ".jp2"
                    )  # NOQA
                    for child in root[0][0][-1][0][0]
                    if child.text.endswith("{}m".format(resolution))
                }  # NOQA
        else:
            for i, resolution in enumerate([60, 20, 10]):
                filenames[resolution] = {
                    child.text.split("_")[-2]: os.path.join(
                        filename, child.text + ".jp2"
                    )  # NOQA
                    for child in root[0][0][-1][i][0]
                }

        return invert_band_res_keys(filenames)
    except Exception:
        raise CorruptedL2AProduct(
            f"Error with product: {filename}.\n"
            f"Failed to parse metadata file: {metadata}"
        )


def get_l2a_aws_filenames(product_path):
    product_path = Path(product_path)

    r10_files = [product_path / "R10m" / f"B{n:02d}.jp2" for n in [2, 3, 4, 8]]
    r20_files = [
        product_path / "R20m" / f"B{n:02d}.jp2" for n in [5, 6, 7, 11, 12]
    ] + [product_path / "R20m" / "SCL.jp2"]
    r60_files = [product_path / "R60m" / "SCL.jp2"]

    filenames = {
        10: {str(f.name)[:3]: f for f in r10_files},
        20: {str(f.name)[:3]: f for f in r20_files},
        60: {str(f.name)[:3]: f for f in r60_files},
    }

    return invert_band_res_keys(filenames)


def invert_band_res_keys(filenames):
    """
    Invert first and second key in dictionary of jp2 filenames
    """
    filenames2 = dict()
    for res, bands_dict in filenames.items():
        for b, f in bands_dict.items():
            filenames2[b] = filenames2.get(b, dict())
            filenames2[b][res] = f
    return filenames2


def get_jp2_filenames(filenames, band, resolution):
    """
    Returns jp2 file for given band with native resolution closest/lower
    than specified value
    """
    available_res = np.array(list(filenames[band].keys()))
    min_avl = np.min(available_res)
    if resolution <= min_avl:
        target_res = min_avl
    else:
        diff = available_res - resolution
        target_res = (
            resolution if 0 in diff else (np.max(diff[diff < 0]) + resolution)
        )
    return filenames[band][target_res]


def get_aws_filenames(product_key: str) -> dict:
    """
    Returns a dictionary of filenames with the structure
    filenames[band][resolution] where band is one of the
    Sentinel-2 bands 'B01', 'B02', ..., 'B12' and resolution
    is one of 10, 20, 60.

    Parameters
    ----------
    product_key: str
        String pointing to the S3 path of the Sentinel-2 product.
        The function will append the conventional tree structure to
        the jp2 files and produce the filenames from this.
        e.g.
    """
    filenames = dict()
    resolutions = [10, 20, 60]
    for bands, res in zip(L2A_RES_BANDS, resolutions):
        for b in bands:
            band_filenames = filenames.get(b, dict())
            band_filenames[res] = os.path.join(
                product_key, f"R{res}m", f"{b}.jp2"
            )
            filenames[b] = band_filenames

    return filenames


def get_s3_filenames(product_key, band, resolution):
    filenames_dict = get_aws_filenames(product_key)
    jp2_filenames = get_jp2_filenames(filenames_dict, band, resolution)
    return jp2_filenames


class NpEncoder(json.JSONEncoder):
    """
    Encode NumPy arrays to JSON
    """

    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(NpEncoder, self).default(obj)


def load_array_bounds(fname, bounds, fill_value=0):
    with rasterio.open(fname) as src:
        window = rasterio.windows.from_bounds(*bounds, src.transform)
        arr = src.read(window=window, boundless=True, fill_value=fill_value)

    return arr[0]


def _load_array_bounds_latlon(
    fname,
    bounds,
    rio_gdal_options=None,
    boundless=True,
    fill_value=np.nan,
    nodata_value=None,
):
    rio_gdal_options = rio_gdal_options or {}

    with rasterio.Env(**rio_gdal_options):
        with rasterio.open(fname) as src:
            window = rasterio.windows.from_bounds(*bounds, src.transform)

            vals = np.array(window.flatten())
            if (vals % 1 > 0).any():
                # logger.warning("Rounding floating window"
                #                "offsets and shape")
                window = window.round_lengths(op="ceil").round_offsets(
                    op="floor"
                )

            if nodata_value is None:
                nodata_value = src.nodata if src.nodata is not None else np.nan

            if nodata_value is None and boundless is True:
                logger.warning(
                    "Raster has no data value, defaulting boundless"
                    " to False. Specify a nodata_value to read "
                    "boundless."
                )
                boundless = False

            arr = src.read(
                window=window, boundless=boundless, fill_value=nodata_value
            )
            arr = arr.astype(
                np.float32
            )  # needed reprojecting with bilinear resampling  # noqa:e501

            if nodata_value is not None:
                arr[arr == nodata_value] = fill_value

    arr = arr[0]
    return arr


def load_reproject(
    filename,
    bounds,
    epsg,
    resolution=10,
    border_buff=0,
    fill_value=0,
    nodata_value=None,
    rio_gdal_options=None,
    resampling=Resampling.nearest,
):
    """
    Read from latlon layer and reproject to UTM
    """
    bbox = gpd.GeoSeries(Polygon.from_bounds(*bounds), crs=CRS.from_epsg(epsg))

    bounds = (
        bbox.buffer(border_buff * resolution)
        .to_crs(epsg=4326)
        .bounds.values[0]
    )
    utm_bounds = (
        bbox.buffer(border_buff * resolution).bounds.values[0].tolist()
    )

    width = max(1, int((utm_bounds[2] - utm_bounds[0]) / resolution))
    height = max(1, int((utm_bounds[3] - utm_bounds[1]) / resolution))

    gim = _load_array_bounds_latlon(
        filename,
        bounds,
        rio_gdal_options=rio_gdal_options,
        fill_value=fill_value,
        nodata_value=nodata_value,
    )

    src_crs = CRS.from_epsg(4326)
    dst_crs = CRS.from_epsg(bbox.crs.to_epsg())

    src_transform = rasterio.transform.from_bounds(
        *bounds, gim.shape[1], gim.shape[0]
    )
    dst_transform = rasterio.transform.from_bounds(*utm_bounds, width, height)

    dst = np.zeros((height, width), dtype=np.float32)

    reproject(
        gim.astype(np.float32),
        dst,
        src_transform=src_transform,
        dst_transform=dst_transform,
        src_crs=src_crs,
        dst_crs=dst_crs,
        resampling=resampling,
    )

    if border_buff > 0:
        dst = dst[border_buff:-border_buff, border_buff:-border_buff]

    return dst


def load_reproject2(
    filename,
    bounds,
    epsg,
    resolution=10,
    border_buff=0,
    nodata_value=None,
    rio_gdal_options=None,
    resampling=Resampling.nearest,
):
    """
    Read from any crs layer and reproject to given epsg.
    Slower than load_reproject as it needs to open the file header twice
    to check the crs
    """
    with rasterio.open(filename) as src:
        src_crs = src.crs

    bbox = gpd.GeoSeries(Polygon.from_bounds(*bounds), crs=CRS.from_epsg(epsg))

    bounds = (
        bbox.buffer(border_buff * resolution).to_crs(src_crs).bounds.values[0]
    )
    utm_bounds = (
        bbox.buffer(border_buff * resolution).bounds.values[0].tolist()
    )

    width = max(1, int((utm_bounds[2] - utm_bounds[0]) / resolution))
    height = max(1, int((utm_bounds[3] - utm_bounds[1]) / resolution))

    gim = _load_array_bounds_latlon(
        filename,
        bounds,
        rio_gdal_options=rio_gdal_options,
        fill_value=np.nan,
        nodata_value=nodata_value,
    )

    # dst_crs = CRS.from_epsg(bbox.crs.to_epsg())
    dst_crs = bbox.crs

    src_transform = rasterio.transform.from_bounds(
        *bounds, gim.shape[1], gim.shape[0]
    )
    dst_transform = rasterio.transform.from_bounds(*utm_bounds, width, height)

    dst = np.zeros((height, width), dtype=np.float32)

    reproject(
        gim.astype(np.float32),
        dst,
        src_transform=src_transform,
        dst_transform=dst_transform,
        src_crs=src_crs,
        dst_crs=dst_crs,
        resampling=resampling,
    )

    if border_buff > 0:
        dst = dst[border_buff:-border_buff, border_buff:-border_buff]

    return dst


def load_reproject3(
    filename,
    bounds,
    epsg,
    resolution=10,
    nodata_value=None,
    rio_gdal_options=None,
    resampling=Resampling.nearest,
):
    """
    Read from any crs layer and reproject to given epsg.
    Slower than load_reproject as it needs to open the file header twice
    to check the crs
    """
    from satio.grid import fiona_transformer

    with rasterio.open(filename) as src:
        src_crs = src.crs
        src_nodata = src.nodata

    bbox = Polygon.from_bounds(*bounds)

    bb_ll = fiona_transformer(
        f"EPSG:{epsg}", f"EPSG:{src_crs.to_epsg()}", bbox
    )

    if bb_ll.geom_type == "MultiPolygon":
        block_boxes_ll = list(bb_ll)
    elif bb_ll.geom_type == "Polygon":
        block_boxes_ll = [bb_ll]
    else:
        raise TypeError(f"Unsupported geom_type {bb_ll.geom_type}")

    utm_bounds = bounds

    arrs = []

    if nodata_value is None:
        nodata_value = src_nodata

    if nodata_value is None:
        nodata_value = fill_value = np.nan
    else:
        fill_value = nodata_value

    for bb in block_boxes_ll:
        src_bounds = bb.bounds

        width = max(1, int((utm_bounds[2] - utm_bounds[0]) / resolution))
        height = max(1, int((utm_bounds[3] - utm_bounds[1]) / resolution))

        gim = _load_array_bounds_latlon(
            filename,
            src_bounds,
            rio_gdal_options=rio_gdal_options,
            fill_value=fill_value,
            nodata_value=nodata_value,
        )

        dst_crs = CRS.from_epsg(epsg)

        src_transform = rasterio.transform.from_bounds(
            *src_bounds, gim.shape[1], gim.shape[0]
        )
        dst_transform = rasterio.transform.from_bounds(
            *utm_bounds, width, height
        )

        dst = np.zeros((height, width), dtype=np.float32)

        gim = gim.astype(np.float32)
        nan_mask = np.isnan(gim)

        if np.all(nan_mask):
            return dst * np.nan

        if np.any(nan_mask):
            from skimage.restoration import inpaint

            gim = inpaint.inpaint_biharmonic(gim, nan_mask)
            gim = gim.astype(np.float32)

        reproject(
            gim.astype(np.float32),
            dst,
            src_transform=src_transform,
            dst_transform=dst_transform,
            src_crs=src_crs,
            dst_crs=dst_crs,
            src_nodata=nodata_value,
            dst_nodata=nodata_value,
            resampling=resampling,
        )

        arrs.append(dst)

    if len(arrs) > 1:
        arr = np.nanmax(np.array(arrs), axis=0)
    else:
        arr = arrs[0]

    return arr


def _load_raster_bounds(
    fname,
    bounds,
    rio_gdal_options=None,
    boundless=True,
    fill_value=np.nan,
    nodata_value=None,
):
    rio_gdal_options = rio_gdal_options or {}

    with rasterio.Env(**rio_gdal_options):
        with rasterio.open(fname) as src:
            window = rasterio.windows.from_bounds(*bounds, src.transform)

            vals = np.array(window.flatten())
            if (vals % 1 > 0).any():
                # logger.warning("Rounding floating window"
                #                "offsets and shape")
                window = window.round_lengths(op="ceil").round_offsets(
                    op="floor"
                )

            if nodata_value is None:
                nodata_value = src.nodata if src.nodata is not None else np.nan

            if nodata_value is None and boundless is True:
                logger.warning(
                    "Raster has no data value, defaulting boundless"
                    " to False. Specify a nodata_value to read "
                    "boundless."
                )
                boundless = False

            arr = src.read(
                window=window, boundless=boundless, fill_value=nodata_value
            )
            arr = arr.astype(
                np.float32
            )  # needed reprojecting with bilinear resampling  # noqa:e501

            if nodata_value is not None:
                arr[arr == nodata_value] = fill_value

    return arr


def load_reproject4(
    filename,
    bounds,
    epsg,
    resolution=10,
    nodata_value=None,
    rio_gdal_options=None,
    resampling=Resampling.nearest,
):
    """
    Read from any crs layer and reproject to given epsg.
    Slower than load_reproject as it needs to open the file header twice
    to check the crs
    """
    from satio.grid import fiona_transformer

    with rasterio.open(filename) as src:
        src_crs = src.crs
        src_nodata = src.nodata
        nbands = src.count

    bbox = Polygon.from_bounds(*bounds)

    bb_ll = fiona_transformer(
        f"EPSG:{epsg}", f"EPSG:{src_crs.to_epsg()}", bbox
    )

    if bb_ll.geom_type == "MultiPolygon":
        block_boxes_ll = list(bb_ll)
    elif bb_ll.geom_type == "Polygon":
        block_boxes_ll = [bb_ll]
    else:
        raise TypeError(f"Unsupported geom_type {bb_ll.geom_type}")

    utm_bounds = bounds

    arrs = []

    if nodata_value is None:
        nodata_value = src_nodata

    if nodata_value is None:
        nodata_value = fill_value = np.nan
    else:
        fill_value = nodata_value

    for bb in block_boxes_ll:
        src_bounds = bb.bounds

        width = max(
            1, int(round((utm_bounds[2] - utm_bounds[0]) / resolution))
        )
        height = max(
            1, int(round((utm_bounds[3] - utm_bounds[1]) / resolution))
        )

        gim = _load_raster_bounds(
            filename,
            src_bounds,
            rio_gdal_options=rio_gdal_options,
            fill_value=fill_value,
            nodata_value=nodata_value,
        )

        dst_crs = CRS.from_epsg(epsg)

        src_transform = rasterio.transform.from_bounds(
            *src_bounds, gim.shape[2], gim.shape[1]
        )
        dst_transform = rasterio.transform.from_bounds(
            *utm_bounds, width, height
        )

        dst = np.zeros((nbands, height, width), dtype=np.float32)

        gim = gim.astype(np.float32)
        nan_mask = np.isnan(gim)

        if np.all(nan_mask):
            return dst * np.nan

        if np.any(nan_mask):
            from skimage.restoration import inpaint

            gim = inpaint.inpaint_biharmonic(gim, nan_mask)
            gim = gim.astype(np.float32)

        reproject(
            gim.astype(np.float32),
            dst,
            src_transform=src_transform,
            dst_transform=dst_transform,
            src_crs=src_crs,
            dst_crs=dst_crs,
            src_nodata=nodata_value,
            dst_nodata=nodata_value,
            resampling=resampling,
        )

        arrs.append(dst)

    if len(arrs) > 1:
        arr = np.nanmax(np.array(arrs), axis=0)
    else:
        arr = arrs[0]

    return arr


class LatLonReprojectLoader(ParallelLoader):
    def _load_array_bounds_latlon(self, fname, bounds, fill_value=0):
        with rasterio.Env(**self._rio_gdal_options):
            with rasterio.open(fname) as src:
                window = rasterio.windows.from_bounds(*bounds, src.transform)

                vals = np.array(window.flatten())
                if (vals % 1 > 0).any():
                    # logger.warning("Rounding floating window"
                    #                "offsets and shape")
                    window = window.round_lengths(op="ceil").round_offsets(
                        op="ceil"
                    )

                arr = src.read(
                    window=window, boundless=True, fill_value=self._fill_value
                )
        arr = arr[0]
        return arr

    def load_reproject(
        self, filename, bounds, epsg, resolution=10, border_buff=0
    ):
        """
        Read from latlon layer and reproject to UTM
        """
        if epsg == 4326:
            # if requested epsg is latlon just load the data
            return self._load_array_bounds_latlon(filename, bounds)

        bbox = gpd.GeoSeries(
            Polygon.from_bounds(*bounds), crs=CRS.from_epsg(epsg)
        )

        bounds = (
            bbox.buffer(border_buff * resolution)
            .to_crs(epsg=4326)
            .bounds.values[0]
        )
        utm_bounds = (
            bbox.buffer(border_buff * resolution).bounds.values[0].tolist()
        )

        width = max(1, int((utm_bounds[2] - utm_bounds[0]) / resolution))
        height = max(1, int((utm_bounds[3] - utm_bounds[1]) / resolution))

        gim = self._load_array_bounds_latlon(filename, bounds)

        src_crs = CRS.from_epsg(4326)
        dst_crs = CRS.from_epsg(bbox.crs.to_epsg())

        src_transform = rasterio.transform.from_bounds(
            *bounds, gim.shape[1], gim.shape[0]
        )
        dst_transform = rasterio.transform.from_bounds(
            *utm_bounds, width, height
        )

        dst = np.zeros((height, width))

        reproject(
            gim,
            dst,
            src_transform=src_transform,
            dst_transform=dst_transform,
            src_crs=src_crs,
            dst_crs=dst_crs,
        )

        if border_buff > 0:
            dst = dst[border_buff:-border_buff, border_buff:-border_buff]

        return dst

    def load_arrays(
        self, filenames, bounds, epsg, resolution=10, border_buff=0
    ):
        def f_handle(filename):
            return self.load_reproject(
                filename, bounds, epsg, resolution, border_buff
            )

        if self._random_order:
            ids = list(range(len(filenames)))
            ids_random = ids.copy()
            random.shuffle(ids_random)
            ids_map = [ids_random.index(i) for i in ids]
            filenames = [filenames[i] for i in ids_random]

        arrs_list = self._run_parallel(
            f_handle,
            filenames,
            self._max_workers,
            threads=True,
            progressbar=self._progressbar,
        )

        if self._random_order:
            arrs_list = [arrs_list[i] for i in ids_map]

        return arrs_list

    def _load_raw(self, collection, bands, resolution=10):
        bounds = collection.bounds
        epsg = collection.epsg

        filenames = [
            f
            for band in bands
            for f in collection.get_band_filenames(band, resolution)
        ]

        arrs_list_flat = self.load_arrays(filenames, bounds, epsg, resolution)

        arrs_list = self._split_arrs_list(arrs_list_flat, n_bands=len(bands))

        return arrs_list

    def load(self, collection, bands, resolution, resample=None):
        """
        Load data for the given bands. resolution should be 10 or 20.
        If resolution is 10, only 'B02', 'B03', 'B04' and 'B08' will be
        loaded at 10 m resolution, the rest at 20 m. Unless 'resample' is
        set to True. In that case, 20 m bands will be upsampled to 10 m with
        a bilinear filter (except 'SCL' which will be resampled with
        nearest neighbors method).
        """
        if not isinstance(bands, (list, tuple)):
            raise TypeError(
                "'bands' should be a list/tuple of bands. "
                f"Its type is: {type(bands)}"
            )

        arrs_list = self._load_raw(collection, bands, resolution)

        products = collection.products
        timestamps = collection.timestamps
        bands = list(bands)
        bounds = list(collection.bounds)
        epsg = collection.epsg

        xds_dict = {
            band: self._arr_to_xarr(
                arrs_list[i], bounds, timestamps, name=band
            )
            for i, band in enumerate(bands)
        }

        xds_dict.update(
            {
                "epsg": epsg,
                "bounds": bounds,
                "products": products,
                "bands": bands,
            }
        )
        # xds = xr.Dataset(xds_dict)

        return xds_dict


class S3LatLonReprojectLoader(LatLonReprojectLoader):
    def __init__(
        self,
        access_key_id=None,
        secret_access_key=None,
        region_name="eu-central-1",
        endpoint_url=None,
        rio_gdal_options=None,
        max_workers=20,
        fill_value=0,
        progressbar=False,
    ):
        boto3_session = boto3.Session(
            access_key_id, secret_access_key, region_name=region_name
        )

        if (access_key_id is None) or (secret_access_key is None):
            aws_unsigned = True
        else:
            aws_unsigned = False

        self._session = AWSSession(
            boto3_session, aws_unsigned=aws_unsigned, endpoint_url=endpoint_url
        )

        if rio_gdal_options is None:
            rio_gdal_options = {
                "AWS_REQUEST_PAYER": "requester",
                "GDAL_DISABLE_READDIR_ON_OPEN": "EMPTY_DIR",
                "CPL_VSIL_CURL_ALLOWED_EXTENSIONS": "jp2",
                "VSI_CACHE": False,
            }

        super().__init__(
            rio_gdal_options=rio_gdal_options,
            max_workers=max_workers,
            fill_value=fill_value,
            progressbar=progressbar,
        )

    def _load_array_bounds_latlon(self, fname, bounds, fill_value=0):
        with rasterio.Env(session=self._session, **self._rio_gdal_options):
            with rasterio.open(fname) as src:
                window = rasterio.windows.from_bounds(*bounds, src.transform)

                vals = np.array(window.flatten())
                if (vals % 1 > 0).any():
                    # logger.warning("Rounding floating window"
                    #                "offsets and shape")
                    window = window.round_lengths(op="ceil").round_offsets(
                        op="ceil"
                    )

                arr = src.read(
                    window=window, boundless=True, fill_value=self._fill_value
                )
        arr = arr[0]
        return arr


class WarpLoader:
    from satio.timeseries import EOTimeseries

    def __init__(
        self,
        max_workers=40,
        progressbar=False,
        rio_gdal_options=None,
        fill_value=None,
        random_order=True,
        buffer_bounds=None,
        skip_corrupted=False,
        session=None,
        rounding_tolerance=0.00001,
    ):
        self._max_workers = max_workers
        self._progressbar = progressbar
        self._session = session

        if rio_gdal_options is None:
            rio_gdal_options = {"GDAL_CACHEMAX": 0}

        self._rio_gdal_options = rio_gdal_options
        self._fill_value = fill_value
        self._random_order = random_order

        self._buffer_bounds = buffer_bounds
        self._skip_corrupted = skip_corrupted
        self._tolerance = rounding_tolerance

    def load(
        self,
        collection,
        bands,
        resolution,
        src_nodata=None,
        dst_nodata=None,
        resampling=Resampling.nearest,
    ) -> EOTimeseries:
        if not isinstance(bands, (list, tuple)):
            raise TypeError(
                "'bands' should be a list/tuple of bands. "
                f"Its type is: {type(bands)}"
            )

        bands = list(bands)
        dst_bounds = list(collection.bounds)
        dst_epsg = collection.epsg
        # these are the bounds and epsg requested for the final data
        # we need to check the epsgs of source data and get the filenames

        # compute the bounds to load from the files
        src_epsgs = set(collection.df.epsg.values.tolist())
        src_bounds = {
            src_epsg: self._get_src_bounds(
                dst_bounds, dst_epsg, src_epsg, self._buffer_bounds
            )
            for src_epsg in src_epsgs
        }

        # get dictionary with filenames and metadata
        loaded_data = self._get_metadata(collection, bands, resolution)

        # load data and store as a key of the metadata dict
        loaded_data = self._parallel_load(loaded_data, bands, src_bounds)

        # get unique set of loaded boxes (epsg/bounds)
        epsg_bounds = self._epsg_bounds(loaded_data)

        # build a warped EOTimeseries for each box
        warped_ts = []
        for src_epsg, src_bounds in epsg_bounds:
            eo_ts_warped = self._build_eotimeseries(
                loaded_data, src_epsg, src_bounds, nodata_value=src_nodata
            ).warp(
                dst_epsg,
                dst_bounds,
                dst_resolution=resolution,
                dst_nodata=dst_nodata,
                resampling=resampling,
            )

            warped_ts.append(eo_ts_warped)

        if len(warped_ts) > 1:
            ts = warped_ts[0].merge_time(*warped_ts[1:])
        else:
            ts = warped_ts[0]

        ts.attrs["sensor"] = collection.sensor

        return ts

    def _get_src_bounds(
        self, dst_bounds, dst_epsg, src_epsg, buffer_dst_bounds
    ):
        """Compute the bounds that need to be loaded in the native files
        epsg.
        TODO: if the required box is a multipolygon (e.g.
        when try to load a utm block at the antimeridian line from a latlon
        file, then we would need to load two sets of bounds and merge them
        after reprojecting. Special case to address."""
        from satio.grid import buffer_bounds, fiona_transformer

        if src_epsg == dst_epsg:
            # no reprojection needed, returning requested bounds
            return dst_bounds

        if buffer_dst_bounds:
            # only buffer if warping is needed
            dst_bounds = buffer_bounds(dst_bounds, buffer_dst_bounds)

        dst_bbox = Polygon.from_bounds(*dst_bounds)

        # compute bbox in the source projection
        src_bbox = fiona_transformer(
            f"EPSG:{dst_epsg}", f"EPSG:{src_epsg}", dst_bbox
        )

        # if the requested box intersects the antimeridian line
        # src_bbox will be a multi-polygon, so we should get a set of bounds
        # or directly use gdal to warp from the source raster
        if src_bbox.geom_type == "MultiPolygon":
            raise NotImplementedError(
                "Requested data intersects anti-meridian"
                " line. Feature not yet implemented"
            )

        src_bounds = src_bbox.bounds
        return src_bounds

    def _get_metadata(self, collection, bands, resolution):
        """loaded_data is a dictionary containing the the metadata information
        for the data to load and is used to store the loaded arrays with
        its new computed bounds before warping.
        """
        df_files = collection.df.copy()

        for band in bands:
            df_files[band] = collection.get_band_filenames(band, resolution)

        loaded_data = df_files.reset_index(drop=True).T.to_dict()

        return loaded_data

    @retry(
        exceptions=Exception,
        tries=RETRIES,
        delay=DELAY,
        backoff=BACKOFF,
        logger=logger,
    )
    @timeout(TIMEOUT, use_signals=False)
    def _load_array(self, fname, bounds):
        """Load array from given filename and bounds. Bounds are assumed to be
        in raster epsg"""
        logger.debug(f"Start loading: {fname}")

        with rasterio.Env(session=self._session, **self._rio_gdal_options):
            with rasterio.open(fname) as src:
                window = rasterio.windows.from_bounds(*bounds, src.transform)
                new_bounds = bounds  # in case the if condition below is false
                vals = np.array(window.flatten())
                if (vals % 1 > 0).any():
                    # logger.warning("Rounding floating window"
                    #                "offsets and shape")
                    window = round_rasterio_window(window)

                    """When rounding the window, the actual bounds of the
                    loaded data are different from those requested.
                    The new bounds need to be computed and returned, as they
                    are used later for correct warping"""
                    new_bounds = rasterio.windows.bounds(window, src.transform)

                boundless = self._fill_value is not None

                arr = src.read(
                    1,
                    window=window,
                    boundless=boundless,
                    fill_value=self._fill_value,
                )
        logger.debug(f"End loading: {fname}")

        return arr, new_bounds

    def _parallel_load(self, loaded_data, bands, src_bounds):
        """
        Load multiple arrays from filenames (stored in the metadata dict)
        and the required bounds (src_bounds) and bands in parallel.

        Randomize file access order and parellelize loading in multiple threads
        for network file system in order to minimize latency
        """
        from satio.utils import parallelize

        download_tuples = [(k, b) for b in bands for k in loaded_data.keys()]

        if self._random_order:
            random.shuffle(download_tuples)

        def _download(download_tuple):
            """Tuple of products ids and band to download"""
            idx, band = download_tuple
            filename = loaded_data[idx][band]
            epsg = loaded_data[idx]["epsg"]
            bounds = src_bounds[epsg]

            try:
                arr, new_bounds = self._load_array(filename, bounds)
                # round new_bounds to avoid float issues
                new_bounds = self._round_bounds(new_bounds, self._tolerance)

            except Exception as e:
                logger.warning(f"Skipping file. Error loading {filename}: {e}")
                if not self._skip_corrupted:
                    raise e
                arr = None
                new_bounds = None

            data_dict = loaded_data[idx].get("data", {})
            loaded_data[idx]["data"] = data_dict
            loaded_data[idx]["data"][band] = (arr, new_bounds)

        _ = parallelize(
            _download,
            download_tuples,
            self._max_workers,
            progressbar=self._progressbar,
        )

        return loaded_data

    @staticmethod
    def _epsg_bounds(loaded_data):
        """Loop over the loaded data and get the eo box (epsg/bounds) of
        each loaded array. The data bounds may differ from the requested
        bounds since we round the loading windows in `_load_array`
        """
        epsg_bounds = []
        for d in loaded_data.values():
            bands = list(d["data"].keys())
            epsg = d["epsg"]
            bounds = d["data"][bands[0]][1]
            if bounds is None:
                continue
            epsg_bounds.append((epsg, bounds))

        epsg_bounds = set(epsg_bounds)
        return epsg_bounds

    @staticmethod
    def _build_eotimeseries(
        loaded_data, epsg, bounds, nodata_value=None
    ) -> "EOTimeseries":
        """
        For a given box (epsg, bounds) among those computed by the
        `_epsg_bounds` method from the loaded data, generate a EOTimeseries
        """
        from satio.timeseries import EOTimeseries

        bands = list(loaded_data[0]["data"].keys())
        bands_arrs = {band: [] for band in bands}
        timestamps = []

        for d in loaded_data.values():
            _, arr_bounds = d["data"][bands[0]]
            if (epsg != d["epsg"]) | (bounds != arr_bounds):
                continue
            else:
                for band in bands:
                    arr, arr_bounds = d["data"][band]
                    bands_arrs[band].append(arr)
                timestamps.append(d["date"])

        bands_arrs = np.array([np.array(bands_arrs[band]) for band in bands])

        eo_ts = EOTimeseries(
            bands_arrs,
            timestamps,
            bands,
            bounds=bounds,
            epsg=epsg,
            nodata_value=nodata_value,
        )
        return eo_ts

    @staticmethod
    def _round_bounds(bounds, tolerance=0.00001):
        def _round(n, tol, ndigits=5):
            return round(round(n / tol) * tol, ndigits=ndigits)

        new_bounds = tuple(
            map(lambda x: _round(x, tol=tolerance, ndigits=5), bounds)
        )
        return new_bounds


class S3WarpLoader(WarpLoader):
    def __init__(
        self,
        access_key_id=None,
        secret_access_key=None,
        region_name="eu-central-1",
        endpoint_url=None,
        max_workers=40,
        progressbar=False,
        rio_gdal_options=None,
        fill_value=None,
        random_order=True,
        buffer_bounds=None,
        skip_corrupted=False,
    ):
        boto3_session = boto3.Session(
            access_key_id, secret_access_key, region_name=region_name
        )

        if (access_key_id is None) or (secret_access_key is None):
            aws_unsigned = True
        else:
            aws_unsigned = False

        if rio_gdal_options is None:
            rio_gdal_options = {
                "AWS_REQUEST_PAYER": "requester",
                "GDAL_DISABLE_READDIR_ON_OPEN": "EMPTY_DIR",
                "CPL_VSIL_CURL_ALLOWED_EXTENSIONS": "jp2",
                "VSI_CACHE": False,
            }

        super().__init__(
            rio_gdal_options=rio_gdal_options,
            max_workers=max_workers,
            fill_value=fill_value,
            progressbar=progressbar,
            random_order=random_order,
            buffer_bounds=buffer_bounds,
            skip_corrupted=skip_corrupted,
        )

        self._session = AWSSession(
            boto3_session, aws_unsigned=aws_unsigned, endpoint_url=endpoint_url
        )


def round_rasterio_window(w):
    """
    Loading with float window is slow. This helper makes sure that rounding
    of the window extends the window to cover for the full area required
    """
    from rasterio.windows import Window

    w_2 = w.round_lengths(op="ceil").round_offsets(op="floor")

    w_3 = Window(
        w_2.col_off,
        w_2.row_off,
        w.col_off + w.width - w_2.col_off,
        w.row_off + w.height - w_2.row_off,
    ).round_lengths(op="ceil")

    return w_3
