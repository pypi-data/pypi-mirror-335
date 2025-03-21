"""
Stitch together Google Maps images from lat, long coordinates

https://stackoverflow.com/questions/7490491/
capture-embedded-google-map-image-with-python-without-using-a-browser/47776466#47776466

"""

import requests
from io import BytesIO
from math import log, exp, tan, atan, pi, ceil
from PIL import Image
import numpy as np
import geopandas as gpd
from loguru import logger
from shapely.geometry import Polygon
from rasterio.crs import CRS
from rasterio.transform import from_bounds
from rasterio.warp import reproject, calculate_default_transform


EARTH_RADIUS = 6378137
EQUATOR_CIRCUMFERENCE = 2 * pi * EARTH_RADIUS
INITIAL_RESOLUTION = EQUATOR_CIRCUMFERENCE / 256.0
ORIGIN_SHIFT = EQUATOR_CIRCUMFERENCE / 2.0


def latlontopixels(lat, lon, zoom):
    mx = (lon * ORIGIN_SHIFT) / 180.0
    my = log(tan((90 + lat) * pi/360.0))/(pi/180.0)
    my = (my * ORIGIN_SHIFT) / 180.0
    res = INITIAL_RESOLUTION / (2**zoom)
    px = (mx + ORIGIN_SHIFT) / res
    py = (my + ORIGIN_SHIFT) / res
    return px, py


def pixelstolatlon(px, py, zoom):
    res = INITIAL_RESOLUTION / (2**zoom)
    mx = px * res - ORIGIN_SHIFT
    my = py * res - ORIGIN_SHIFT
    lat = (my / ORIGIN_SHIFT) * 180.0
    lat = 180 / pi * (2*atan(exp(lat*pi/180.0)) - pi/2.0)
    lon = (mx / ORIGIN_SHIFT) * 180.0
    return lat, lon


def get_gmaps_image_latlon(bounds: list,
                           google_maps_api_key: str = None,
                           zoom: int = 18,
                           maptype: str = 'satellite') -> np.ndarray:
    """
    Fetch a google maps image of a given box in lat lon coordinates.
    The maximum size is 640x640 so the image is split and downloaded in tiles
    and then stiched together.
    A Google Maps API key is needed.

    Parameters
    ----------
    bounds : iterable
        list or array of bounds in lat lon (xmin, ymin, xmax, ymax)
    google_maps_api_key : str
        Google maps api key needed to downalod the images
    zoom : int
        Zoom level. 18 corresponds to the maximum for land resolution
    maptype : str
        Specify what kind of map is needed. Options can be 'roadmap', 'terrain',
        'satellite', 'hybrid' 

    Returns
    -------
    np.ndarray
        Numpy array containing the RGB image

    References
    ----------
    [1] https://developers.google.com/maps/documentation/maps-static/dev-guide 
    [2] https://stackoverflow.com/questions/7490491/capture-embedded-google-map-image-with-python-without-using-a-browser/47776466#47776466  # NOQA
    [3] https://www.codeproject.com/Articles/14793/How-Google-Map-Works
    """
    if zoom <= 0:
        raise ValueError(f"zoom value must be a positive number.")

    ullon, lrlat, lrlon, ullat = bounds

    # Set some important parameters
    scale = 1
    maxsize = 640

    # convert all these coordinates to pixels
    ulx, uly = latlontopixels(ullat, ullon, zoom)
    lrx, lry = latlontopixels(lrlat, lrlon, zoom)

    # calculate total pixel dimensions of final image
    dx, dy = lrx - ulx, uly - lry

    # calculate rows and columns
    cols, rows = int(ceil(dx/maxsize)), int(ceil(dy/maxsize))

    if (cols > 2) | (rows > 2):
        logger.warning('Requested figure is too big.'
                       f'Retrying with zoom={zoom - 2}')
        return get_gmaps_image_latlon(
            bounds, google_maps_api_key=google_maps_api_key,
            zoom=zoom-2, maptype=maptype)
    # calculate pixel dimensions of each small image
    bottom = 120
    largura = int(ceil(dx/cols))
    altura = int(ceil(dy/rows))
    alturaplus = altura + bottom

    # assemble the image from stitched
    final = Image.new("RGB", (int(dx), int(dy)))
    for x in range(cols):
        for y in range(rows):
            dxn = largura * (0.5 + x)
            dyn = altura * (0.5 + y)
            latn, lonn = pixelstolatlon(ulx + dxn, uly - dyn - bottom/2, zoom)
            position = ','.join((str(latn), str(lonn)))
            logger.debug(f'Downloading tile({x}, {y}), position: {position}')
            urlparams = {'center': position,
                         'zoom': str(zoom),
                         'size': '%dx%d' % (largura, alturaplus),
                         'maptype': maptype,
                         'sensor': 'false',
                         'scale': scale}
            if google_maps_api_key is not None:
                urlparams['key'] = google_maps_api_key

            url = 'http://maps.google.com/maps/api/staticmap'
            try:
                response = requests.get(url, params=urlparams)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(e)
                return None

            im = Image.open(BytesIO(response.content))
            if (x == 0) and (y == 0) and not _is_imagery_valid(np.array(im)):
                logger.warning(f"No valid imagery at this zoom: {zoom}. "
                               f"Retrying with zoom: {zoom - 2}...")
                return get_gmaps_image_latlon(
                    bounds, google_maps_api_key=google_maps_api_key,
                    zoom=zoom-2, maptype=maptype)

            final.paste(im, (int(x*largura), int(y*altura)))

    return np.array(final)


def get_gmaps_image(bounds: list,
                    epsg: int,
                    google_maps_api_key: str = None,
                    zoom: int = 18,
                    maptype: str = 'satellite') -> np.ndarray:
    """
    Fetch a google maps image of a given box in its CRS.
    A Google Maps API key is needed.

    bounds : list
        xmin, ymin, xmax, ymax in the given epsg
    epsg: epsg code
    google_maps_api_key : str
        Google maps api key needed to downalod the images
    zoom : int
        Zoom level. 18 corresponds to the maximum for land resolution
    maptype : str
        Specify what kind of map is needed. Options can be 'roadmap', 'terrain',
        'satellite', 'hybrid' 

    Returns
    -------
    np.ndarray
        Numpy array containing the RGB image

    References
    ----------
    [1] https://developers.google.com/maps/documentation/maps-static/dev-guide 
    [2] https://stackoverflow.com/questions/7490491/capture-embedded-google-map-image-with-python-without-using-a-browser/47776466#47776466  # NOQA
    [3] https://www.codeproject.com/Articles/14793/How-Google-Map-Works
    """
    bbox = gpd.GeoSeries(Polygon.from_bounds(*bounds),
                         crs=CRS.from_epsg(epsg))
    resolution = 10

    # utm pixels to buffer on the border (avoid reprojection artifacts)
    border_buff = 2

    bounds = bbox.buffer(
        border_buff * resolution).to_crs(epsg=4326).bounds.values[0]

    gim = get_gmaps_image_latlon(bounds,
                                 google_maps_api_key=google_maps_api_key,
                                 zoom=zoom, maptype=maptype)
    src_crs = CRS.from_epsg(4326)
    dst_crs = CRS.from_epsg(bbox.crs.to_epsg())

    src_transform = from_bounds(*bounds, gim.shape[1], gim.shape[0])
    dst_transform, width, height = calculate_default_transform(
        src_crs, dst_crs, gim.shape[1], gim.shape[0], *bounds)

    dst = np.zeros((3, height, width))

    reproject(np.transpose(gim, [2, 0, 1]) / 255,
              dst,
              src_transform=src_transform,
              dst_transform=dst_transform,
              src_crs=src_crs,
              dst_crs=dst_crs)

    dst = np.transpose(dst, [1, 2, 0])

    pixelsize = round(border_buff * resolution / dst_transform.a)

    dst_final = dst[pixelsize:-pixelsize, pixelsize:-pixelsize, :]

    return dst_final


def _is_imagery_valid(im):
    """
    Check if downloaded image is not the gray placeholder.

    NB: Only checks that a square of 10x10 at the origin has std == 0.
        Might cause bugs...
    """
    if im[:10, :10].std() == 0:
        return False
    else:
        return True
