import os
from pathlib import Path

from loguru import logger
import rasterio
from rio_cogeo.profiles import cog_profiles
from rio_cogeo.cogeo import cog_translate

from satio.utils import random_string
from satio.utils.buildvrt import build_vrt


def cog_translate_wrapper(src_path,
                          dst_path,
                          profile="deflate",
                          profile_options=None,
                          in_memory=True,
                          colormap=None,
                          band_names=None,
                          **options):

    if profile_options is None:
        profile_options = {}

    """Convert image to COG."""
    # Format creation option (see gdalwarp `-co` option)
    output_profile = cog_profiles.get(profile)
    output_profile.update(dict(BIGTIFF="IF_SAFER",
                               interleave="band",
                               blockxsize=1024,
                               blockysize=1024))

    output_profile.update(profile_options)

    # Dataset Open option (see gdalwarp `-oo` option)
    config = dict(
        GDAL_NUM_THREADS="ALL_CPUS",
        GDAL_TIFF_INTERNAL_MASK=True,
        GDAL_TIFF_OVR_BLOCKSIZE="128",
    )

    cog_translate(
        src_path,
        dst_path,
        output_profile,
        config=config,
        in_memory=in_memory,
        quiet=True,
        **options,
    )

    if colormap is not None:
        with rasterio.open(dst_path, 'r+') as src:
            src.write_colormap(1, colormap)

    if band_names is not None:
        with rasterio.open(dst_path, 'r+') as src:
            src.update_tags(bands=band_names)
            for i, b in enumerate(band_names):
                src.update_tags(i + 1, band_name=b)

    return True


def cog_from_folder(folder,
                    cog_filename,
                    create_folder=True,
                    colormap=None,
                    in_memory=True,
                    band_names=None,
                    **options):

    cog_filename = Path(cog_filename)
    vrt_fname = None

    if cog_filename.is_file():
        os.remove(cog_filename)

    if create_folder:
        cog_filename.parent.mkdir(parents=True, exist_ok=True)

    try:
        vrt_fname = f'_tmpvrt_{random_string()}.vrt'
        logger.info(f"Generating {cog_filename} from {folder}")
        build_vrt(vrt_fname, folder)
        cog_translate_wrapper(vrt_fname,
                              cog_filename,
                              in_memory=in_memory,
                              colormap=colormap,
                              band_names=band_names,
                              **options)

    except Exception as e:
        logger.error(f"Error on creating COG from folder {folder}:\n{e}")
    finally:
        if Path(vrt_fname).is_file():
            os.remove(vrt_fname)
