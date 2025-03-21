import os
import glob
from pathlib import Path
import argparse

from loguru import logger


def rename_filenames(folder, ext1, ext2):
    filenames = get_filenames(folder, ext=ext1)
    for f in filenames:
        os.rename(f, f.replace(ext1, ext2))


def get_filenames(folder, ext='.tif'):
    return sorted(glob.glob(os.path.join(folder, f'*{ext}')))


def build_vrt(dst_filename,
              folder,
              nodata_value=None,
              **kwargs):

    folder = os.path.abspath(folder)
    filenames = get_filenames(folder)
    if not len(filenames):
        raise ValueError(f"No files in {folder}")

    build_vrt_files(dst_filename,
                    filenames,
                    nodata_value=nodata_value,
                    **kwargs)


def build_vrt_files(dst_filename,
                    filenames,
                    nodata_value=None,
                    **kwargs):

    dst_filename = os.path.abspath(dst_filename)
    if os.path.isfile(dst_filename):
        os.remove(dst_filename)

    dst_folder = os.path.dirname(dst_filename)
    os.makedirs(dst_folder, exist_ok=True)

    if not len(filenames):
        raise ValueError(f"No files in provided...")

    dst_filename = str(dst_filename)
    filenames = [str(f) for f in filenames]

    # late import to avoid gdal import conflicts...
    try:
        from osgeo import gdal
    except ImportError:
        import gdal

    my_vrt = gdal.BuildVRT(dst_filename,
                           filenames,
                           VRTNodata=nodata_value,
                           **kwargs)
    my_vrt = None  # NOQA


def parse_args():
    parser = argparse.ArgumentParser(description="Build a vrt from a folder")
    parser.add_argument('folder', help="Folder of geotifs files")
    parser.add_argument('vrtname', help="Destination VRT filename")
    return parser.parse_args()


if __name__ == '__main__':

    args = parse_args()

    logger.info("Creating {}...".format(args.vrtname))
    dst_file = os.path.abspath(args.vrtname)
    build_vrt(dst_file, args.folder)
    logger.info("Done")
