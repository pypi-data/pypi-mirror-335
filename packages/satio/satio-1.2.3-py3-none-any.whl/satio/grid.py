from typing import List
from concurrent.futures import ThreadPoolExecutor

import os
import numpy as np
import pandas as pd
import geopandas as gpd
import shapely
from shapely.geometry import Polygon
from shapely.geometry import mapping, shape
from fiona.transform import transform_geom
from pyproj.crs import CRS
import rasterio
import rasterio.mask
from rasterio.windows import from_bounds  # NOQA

import satio
from satio.layers import load_s2tile_windows
from satio.utils import parallelize


class BBoxGrid:
    """
    Divides a rectangular box in a grid of bboxes of given size in pixels
    """

    def __init__(self,
                 bounds,
                 bbox_size=256,
                 resolution=10,
                 epsg=None,
                 **kwargs):
        """
        bounds = (xmin, ymin, xmax, ymax)
        """
        bounds = self._round_bounds(bounds, resolution)
        left, bottom, right, top = bounds
        self.origin_x = left
        self.origin_y = top
        self.width = right - left
        self.height = top - bottom
        self.epsg = epsg

        # make it compatible with previous scripts, where 'resolution'
        # parameter was called 'pixelsize'
        resolution = kwargs.get('pixelsize', resolution)
        self.bbox_size = bbox_size
        self.bbox_size_m = bbox_size * resolution

        self.nrows = self._get_nrows()
        self.ncols = self._get_ncols()

        self.n_bboxes = self.nrows * self.ncols

    @staticmethod
    def _round_bounds(bounds, resolution):
        """
        Buffer bounds of 'resolution' meters and then round to the closest
        multiple of resolution. This will split in bboxes that are multiple of
        the desired pixels resolution.
        """
        bounds = np.array(bounds)
        bounds = bounds + np.array([-resolution, -resolution,
                                    resolution, resolution])
        bounds = bounds // resolution * resolution
        return bounds.tolist()

    def _get_nrows(self):
        return np.ceil(self.height / self.bbox_size_m).astype(int)

    def _get_ncols(self):
        return np.ceil(self.width / self.bbox_size_m).astype(int)

    def _get_bbox_row_col(self, box_id):
        return list(zip(*np.unravel_index([box_id], (self.nrows, self.ncols),
                                          order='C')))[0]

    def _get_bbox_bounds(self, row, col):
        left, top = (self.origin_x + col * self.bbox_size_m,
                     self.origin_y - row * self.bbox_size_m)
        right, bottom = left + self.bbox_size_m, top - self.bbox_size_m
        return left, bottom, right, top

    def __len__(self):
        return self.n_bboxes

    @property
    def shape(self):
        return self.nrows, self.ncols

    def __getitem__(self, bbox_id):

        if isinstance(bbox_id, slice):
            start = bbox_id.start if bbox_id.start else 0
            stop = bbox_id.stop if bbox_id.stop else len(self)
            step = bbox_id.step if bbox_id.step else 1

            if start < 0:
                start += len(self)

            if stop < 0:
                stop += len(self)

            return [self._get_bbox(i) for i in range(start, stop, step)]
        else:
            return self._get_bbox(bbox_id)

    def _get_bbox(self, bbox_id):
        if bbox_id < 0:
            bbox_id = len(self) + bbox_id

        if (bbox_id < 0) or (bbox_id >= (self.nrows * self.ncols)):
            raise IndexError("box_id should be between 0 and {}"
                             .format(len(self) - 1))

        row, col = self._get_bbox_row_col(bbox_id)
        left, bottom, right, top = self._get_bbox_bounds(row, col)
        return BBox((left, bottom, right, top), bbox_id)

    def __repr__(self):
        return "<BboxGrid: bbox_size={}, n_boxes={}>".format(self.bbox_size,
                                                             len(self))

    def as_gdf(self, aoi_shp=None):
        """
        Returns GeoDataFrame of bboxes in grid. If aoi_shp: Polygon is given,
        the GeoDataFrame will contain only the intersecting bboxes
        """
        if aoi_shp:
            return gpd.GeoDataFrame({'id': b.id, 'geometry': b}
                                    for b in self if b.intersects(aoi_shp))
        else:
            return gpd.GeoDataFrame({'id': b.id, 'geometry': b} for b in self)


class BBoxGridShp(BBoxGrid):
    """Use pure shapely boxes instead of custom BBox"""

    def _get_bbox(self, bbox_id):
        if bbox_id < 0:
            bbox_id = len(self) + bbox_id

        if (bbox_id < 0) or (bbox_id >= (self.nrows * self.ncols)):
            raise IndexError("box_id should be between 0 and {}"
                             .format(len(self) - 1))

        row, col = self._get_bbox_row_col(bbox_id)
        left, bottom, right, top = self._get_bbox_bounds(row, col)
        return shapely.geometry.box(left, bottom, right, top)

    def as_gdf(self, aoi_shp=None):
        """
        Returns GeoDataFrame of bboxes in grid. If aoi_shp: Polygon is given,
        the GeoDataFrame will contain only the intersecting bboxes
        """
        if aoi_shp:
            return gpd.GeoDataFrame({'id': i, 'geometry': b}
                                    for i, b in enumerate(self)
                                    if b.intersects(aoi_shp))
        else:
            return gpd.GeoDataFrame({'id': i, 'geometry': b}
                                    for i, b in enumerate(self))


class BBox(Polygon):
    """Sub-class of Polygon describing a BBox with a given id"""

    def __init__(self, bounds, bbox_id=None):
        self.left, self.bottom, self.right, self.top = bounds
        super().__init__([(self.left, self.top), (self.right, self.top),
                          (self.right, self.bottom), (self.left, self.bottom),
                          (self.left, self.top)])

        self.id = bbox_id

        self.width = self.right - self.left
        self.height = self.top - self.bottom

    def intersect(self, geo_df, buffer=0):
        """
        Returns list of overlapping sentinel 2 tiles given
        with s2grid GeoDataFrame
        """

        def inter_f(x): return x.geometry.buffer(buffer).intersects(self)
        flag = geo_df.apply(inter_f, axis=1)
        return geo_df[flag]

    def plot(self, *args, **kwargs):
        kwargs['facecolor'] = kwargs.get('facecolor', 'none')
        gpd.GeoDataFrame([{'id': 0,
                           'geometry': self}]).plot(*args, **kwargs)


def tile_to_epsg(tile):
    row = tile[2]
    zone = tile[:2]

    if row in 'CDEFGHJKLM':
        hemisphere = 'S'
    elif row in 'NPQRSTUVWX':
        hemisphere = 'N'
    else:
        raise ValueError(f"Unrecognized UTM zone '{zone}'.")

    utm = zone + hemisphere
    return utm_to_epsg(utm)


def utm_to_epsg(utm):
    utm = utm.upper()
    sud = 1 if utm[-1] == 'S' else 0
    zone = int(utm[:-1])
    epsg = 32600 + sud * 100 + zone
    return epsg


def get_tile_blocks(tile, s2grid=None, resolution=10):

    if s2grid is None:
        s2grid = satio.layers.load('s2grid')

    width = heigth = {10: 10980,
                      20: 5490,
                      60: 1830,
                      1098: 100}[resolution]

    epsg = tile_to_epsg(tile)
    if 'bounds' in s2grid.columns:
        tile_bounds = s2grid.loc[s2grid.tile == tile, 'bounds'].iloc[0]
    else:
        tile_bounds = s2grid[s2grid.tile == tile].to_crs(
            epsg=epsg).bounds.values[0].round().tolist()
    tile_transform = rasterio.transform.from_bounds(
        *tile_bounds, width, heigth)

    windows_tuples = load_s2tile_windows(resolution)

    polygons = []
    for t in windows_tuples:
        w = t[1]
        xmin, ymax = tile_transform * (w.col_off, w.row_off)
        xmax, ymin = tile_transform * \
            (w.col_off + w.width, w.row_off + w.height)

        polygons.append(Polygon.from_bounds(xmin, ymin, xmax, ymax))

    return gpd.GeoSeries(polygons, crs=CRS.from_epsg(epsg))


def get_blocks_gdf(tiles, s2grid=None, resolution=10):
    if s2grid is None:
        s2grid = satio.layers.load('s2grid')

    tiles_blocks = []
    for t in tiles:
        tblocks = get_tile_blocks(t, s2grid, resolution=resolution)
        tblocks_ll = tblocks.to_crs(epsg=4326)
        tiles_blocks += [{'tile': t,
                          'bounds': tuple(np.round(
                              np.array(b.bounds) / resolution).astype(int)
                              * resolution),
                          'geometry': tblocks_ll.iloc[i],
                          'area': b.area,
                          'epsg': tile_to_epsg(t),
                          'block_id': i}
                         for i, b in enumerate(tblocks)]
    df = gpd.GeoDataFrame(tiles_blocks, crs=CRS.from_epsg(4326))

    return df


def get_blocks_gdf_antimeridian(tiles, s2grid=None, resolution=10):
    if s2grid is None:
        s2grid = satio.layers.load('s2grid')

    tiles_blocks = []
    for t in tiles:
        tblocks = get_tile_blocks(t, s2grid, resolution=resolution)
        tblocks_ll = fiona_transform(tblocks.to_frame('geometry'),
                                     dst_epsg=4326)

        tiles_blocks += [{'tile': t,
                          'bounds': tuple(np.round(
                              np.array(b.bounds) / resolution).astype(int)
                              * resolution),
                          'geometry': tblocks_ll.iloc[i].geometry,
                          'area': b.area,
                          'epsg': tile_to_epsg(t),
                          'block_id': i}
                         for i, b in enumerate(tblocks)]
    df = gpd.GeoDataFrame(tiles_blocks, crs=CRS.from_epsg(4326))

    return df


def filter_land_blocks(blocks,
                       landsea,
                       s2grid,
                       landsea_buffer=0.03,
                       max_workers=4):

    s2tiles = s2grid[s2grid.tile.isin(blocks.tile.unique())]

    landsea_tiles = landsea.intersection(s2tiles.unary_union)
    landsea_geom = landsea_tiles.iloc[0].buffer(landsea_buffer)

    def f(row):
        if row.geometry.intersects(landsea_geom):
            return row.Index
        else:
            return None

    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        valid_ids = list(ex.map(f, blocks.itertuples()))

    valid_ids = [r for r in valid_ids if r is not None]

    blocks = blocks.loc[valid_ids]

    return blocks


def filter_regions_blocks(blocks,
                          regions,
                          s2grid,
                          regions_buffer=0.03,
                          max_workers=4):

    s2tiles = s2grid[s2grid.tile.isin(blocks.tile.unique())]

    regions_tiles = regions.intersection(s2tiles.unary_union)
    regions_geom = regions_tiles.unary_union.buffer(regions_buffer)

    def f(row):
        if row.geometry.intersects(regions_geom):
            return row.Index
        else:
            return None

    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        valid_ids = list(ex.map(f, blocks.itertuples()))

    valid_ids = [r for r in valid_ids if r is not None]

    blocks = blocks.loc[valid_ids]

    return blocks


def split_rectangle(geom):
    """
    Split rectangle in 4 rectangles
    """
    xmin, ymin, xmax, ymax = geom.bounds

    xmid = xmin + (xmax - xmin) / 2
    ymid = ymin + (ymax - ymin) / 2

    return [Polygon.from_bounds(xmin, ymin, xmid, ymid),
            Polygon.from_bounds(xmin, ymid, xmid, ymax),
            Polygon.from_bounds(xmid, ymin, xmax, ymid),
            Polygon.from_bounds(xmid, ymid, xmax, ymax)]


def get_tlocs_areas(tlocs, base_geoms=None, max_locs=300, final_geoms=[]):
    """
    Generate a grid of boxes by recursively splitting rectangles in 4 until
    every rectangle contains at most `max_locs` training points from `tlocs`
    """
    if base_geoms is None:
        base_geoms = [Polygon.from_bounds(-180, -90, 180, 90)]

    for g in base_geoms:
        n_locs = tlocs[tlocs.intersects(g)].shape[0]
        if n_locs <= max_locs:
            final_geoms.append(g)
        else:
            final_geoms = get_tlocs_areas(tlocs,
                                          base_geoms=split_rectangle(g),
                                          final_geoms=final_geoms)

    tlocs_areas = gpd.GeoSeries(final_geoms, crs=tlocs.crs)

    return tlocs_areas


def buffer_bounds(bounds, buffer):
    bounds = np.array(bounds)
    bounds += np.array([-buffer, -buffer, buffer, buffer])
    return bounds.tolist()


def clip_to_global_bbox(df):
    bbox = gpd.GeoSeries([Polygon([(-180, 90), (180, 90),
                                   (180, -90), (-180, -90)])])
    dfbbox = gpd.GeoDataFrame({'geometry': bbox,
                               'gbbox': 0}, crs=CRS.from_epsg(4326))
    dfint = gpd.tools.overlay(df, dfbbox)
    return dfint


def fiona_transform(df, dst_crs=None, dst_epsg=None):
    if dst_epsg is not None:
        dst_crs = CRS.from_epsg(dst_epsg)

    if not isinstance(dst_crs, str):
        dst_crs = dst_crs.to_string()

    src_crs = df.crs.to_string()

    def f(x): return fiona_transformer(src_crs, dst_crs, x)

    tdf = df.set_geometry(df.geometry.apply(f))
    tdf.crs = CRS.from_string(dst_crs)
    return tdf


def fiona_transformer(src_crs, dst_crs, geom):
    fi_geom = transform_geom(src_crs=src_crs,
                             dst_crs=dst_crs,
                             geom=mapping(geom),
                             antimeridian_cutting=True)
    return shape(fi_geom)


def get_latlon_grid(deg_resolution: int = 1,
                    sjoin_layers: List[gpd.GeoDataFrame] = None):
    """
    Genearte a gloabl lat lon grid with conventional cell names.

    If a list of `sjoin_layers` is provided they will be intersected to
    reduce the grid. (For example providing the landsea layer it will output
    a grid of cells only covering landmass)
    """
    sjoin_layers = sjoin_layers or []

    xdeg = ydeg = deg_resolution

    x = np.arange(-180, 180, xdeg)
    y = np.arange(-90, 90, ydeg)

    grid_origins = [(x0, y0) for y0 in y for x0 in x]
    polygons = [Polygon.from_bounds(x0, y0, x0 + xdeg, y0 + ydeg)
                for x0, y0 in grid_origins]

    ll_tile = []
    for x0, y0 in grid_origins:
        a = 'E' if x0 >= 0 else 'W'
        b = 'N' if y0 >= 0 else 'S'
        ll_tile.append(f'{b}{abs(y0):02d}{a}{abs(x0):03d}')

    grid = gpd.GeoDataFrame(ll_tile, columns=['ll_tile'],
                            geometry=polygons, crs=4326)

    for layer in sjoin_layers:
        grid = gpd.sjoin(grid, layer)
        grid = grid.drop_duplicates('ll_tile')

    return grid


class BlocksBuilder:

    def __init__(self,
                 tiles,
                 s2grid=None,
                 land_masses=None,
                 LISA_blocks=None,
                 mastertiles=None):

        self.tiles = tiles
        self.s2grid = (s2grid if s2grid is not None
                       else satio.layers.load('s2grid'))
        self.land_masses = (land_masses if land_masses is not None
                            else gpd.read_file('/data/worldcover/auxdata/shapefiles/land/land-sea-detailed.geojson'))

        if LISA_blocks is not None:
            self.LISA_blocks = LISA_blocks
        else:
            self.LISA_blocks = gpd.read_file('/data/worldcover/auxdata/shapefiles/latlon_grid_1deg_all_land.geojson')
            self.LISA_blocks.drop(columns=['index_right'], inplace=True)
        self.mastertiles = (mastertiles if mastertiles is not None
                            else gpd.read_file('/data/worldcover/auxdata/water_GEE/LC100_product_TilingGrid_v2.shp'))

    def get_blocks_gdf(self,
                       epsg_filter=True,
                       tile_filter=True,
                       water_filter=True,
                       ice_filter=True,
                       overpass_filter=True,
                       max_workers=1,
                       progressbar=True):

        def f(tile): return self._get_tile_blocks_gdf(tile,
                                                      epsg_filter,
                                                      tile_filter,
                                                      water_filter,
                                                      ice_filter,
                                                      overpass_filter)
        gdfs_list = parallelize(f,
                                self.tiles,
                                max_workers=max_workers,
                                progressbar=progressbar)

        return pd.concat(gdfs_list, ignore_index=True)

    def _get_tile_blocks_gdf(self,
                             tile,
                             epsg_filter,
                             tile_filter,
                             water_filter,
                             ice_filter,
                             overpass_filter):

        tbr = TileBlocksBuilder(tile, self.s2grid, self.land_masses, self.LISA_blocks, self.mastertiles)

        return tbr.get_blocks_gdf(epsg_filter=epsg_filter,
                                  tile_filter=tile_filter,
                                  water_filter=water_filter,
                                  ice_filter=ice_filter,
                                  overpass_filter=overpass_filter)


class TileBlocksBuilder:

    def __init__(self, tile, s2grid=None, land_masses=None, LISA_blocks=None, mastertiles=None):
        self.tile = tile
        self.epsg = tile_to_epsg(tile)

        self.s2grid = (s2grid if s2grid is not None
                       else satio.layers.load('s2grid'))
        self.land_masses = (land_masses if land_masses is not None
                            else gpd.read_file('/data/worldcover/auxdata/shapefiles/land/land-sea-detailed.geojson'))
        if LISA_blocks is not None:
            self.LISA_blocks = LISA_blocks
        else:
            self.LISA_blocks = gpd.read_file('/data/worldcover/auxdata/shapefiles/latlon_grid_1deg_all_land.geojson')
            self.LISA_blocks.drop(columns=['index_right'], inplace=True)
        self.mastertiles = (mastertiles if mastertiles is not None
                            else gpd.read_file('/data/worldcover/auxdata/water_GEE/LC100_product_TilingGrid_v2.shp'))
        self.blocks = get_blocks_gdf([tile], s2grid)

        self._epsgs = self.s2grid.epsg.unique()
        self._s2tile = s2grid[s2grid.tile == tile]

    def _filter_overlap_epsg(self, blocks):
        """
        Remove blocks in overlab between neighboring epsgs.
        The convention is to remove blocks that are withing tiles
        on the right epsg.
        """
        if self.epsg + 1 not in self._epsgs:
            # if there is no epsg on the right do nothing
            return blocks

        s2grid = self.s2grid
        if self.epsg + 2 not in self._epsgs:
            # also check 2 steps (necessary in the north)
            r_s2grid = s2grid[s2grid.epsg == self.epsg + 1]
        else:
            r_s2grid = (s2grid[s2grid.epsg == self.epsg + 1]).append(s2grid[s2grid.epsg == self.epsg + 2])
        ov_tiles = r_s2grid[r_s2grid.intersects(self._s2tile.iloc[0].geometry)]

        if ov_tiles.shape[0] == 0:
            return blocks
        else:
            new_blocks = blocks[~blocks.within(ov_tiles.unary_union)]
            return new_blocks

    def _filter_water(self, blocks):
        """
        Remove blocks that are completely covered with water
        """
        # First using a detailed land-sea mask
        land_masses = self.land_masses
        df = gpd.sjoin(blocks, land_masses)
        new_blocks_1 = blocks[blocks['block_id'].isin(df['block_id'].unique())]

        # Next using the DEM
        DEM_folder = '/data/worldcover/auxdata/dem/COP-DEM_GLO-30-DTED/S2grid_20m'
        DEM_file = f'{DEM_folder}/dem_{self.tile}.tif'
        blocks['COP_DEM'] = 0
        if os.path.isfile(DEM_file):
            for num, block in blocks.iterrows():
                with rasterio.open(DEM_file) as src:
                    dem = src.read(1, window=from_bounds(
                        block.bounds[0], block.bounds[1], block.bounds[2], block.bounds[3], src.transform))
                    dem[dem == -32767] = 0
                if np.max(dem) > 0:
                    blocks.loc[num, 'COP_DEM'] = 1
        blocks = blocks[blocks.COP_DEM == 1]
        new_blocks_2 = blocks.drop(columns=['COP_DEM'])

        # take the union of both
        new_blocks = pd.concat([new_blocks_1, new_blocks_2]).drop_duplicates().reset_index(drop=True)

        # next an extra check for inland waters that are not yet removed
        mastertiles = self.mastertiles
        df = gpd.sjoin(new_blocks, mastertiles)

        # check for each block the number of overpasses
        new_blocks['inland_water'] = 0
        for num, block in new_blocks.iterrows():
            masterTiles = df[df['block_id'] == block.block_id]['tile_id'].unique()
            water_array = np.zeros(len(masterTiles), dtype=np.ubyte)
            for idx, masterTile in enumerate(masterTiles):
                filename = f'/data/worldcover/auxdata/water_GEE/updated_fractions/{masterTile}_20m_2019-01-01_to_2020-01-01_water_fraction.tif'
                if os.path.isfile(filename):
                    with rasterio.open(filename) as src:
                        if (int(masterTile[1:4]) == 180):
                            shape = shapely.affinity.translate(block.geometry, xoff=360)
                        else:
                            shape = block.geometry
                        try:
                            out_image, out_transform = rasterio.mask.mask(src, [shape], crop=True, nodata=255)
                            if (np.all((out_image >= 80))) & (~np.all((out_image == 255))):
                                water_array[idx] = 1
                        except ValueError:
                            water_array[idx] = 2
                            print('There is no overlap with this shape, skipping it')
            if (np.all(water_array >= 1)) & (np.size(water_array) > 0) & (~np.all(water_array == 2)):
                new_blocks.loc[num, 'inland_water'] = 1
        return new_blocks

    def _filter_ice(self, blocks):
        """
        Mark blocks that are fully ice, so they can be skipped
        """
        LISA_blocks = self.LISA_blocks
        df = gpd.sjoin(blocks, LISA_blocks)

        # check for each block if they consists of 100% ice
        blocks['ICE'] = 0
        for num, block in blocks.iterrows():
            tiles = df[df['block_id'] == block.block_id]['ll_tile'].unique()
            ice_array = np.zeros(len(tiles), dtype=np.ubyte)
            for idx, tile in enumerate(tiles):
                filename = f'/data/worldcover/auxdata/ice_GEE/updated_fractions_LISA/{tile}_20m_2019-01-01_to_2020-01-01_LISA_snow_fraction.tif'
                if os.path.isfile(filename):
                    with rasterio.open(filename) as src:
                        if (int(tile[4:7]) == 180):
                            shape = shapely.affinity.translate(block.geometry, xoff=360)
                        else:
                            shape = block.geometry
                        try:
                            out_image, out_transform = rasterio.mask.mask(src, [shape], nodata=255, crop=True)
                            if (np.all((out_image > 90))) & (~np.all((out_image == 255))):
                                ice_array[idx] = 1
                        except ValueError:
                            print('There is no overlap with this shape, skipping it')

            if (np.all(ice_array == 1)) & (np.size(ice_array) > 0):
                blocks.loc[num, 'ICE'] = 1
        return blocks

    def _filter_overpasses(self, blocks):
        """
        Mark blocks that have no overpasses
        """
        mastertiles = self.mastertiles
        df = gpd.sjoin(blocks, mastertiles)

        # check for each block the number of overpasses
        blocks['Overpass'] = np.nan
        for num, block in blocks.iterrows():
            masterTiles = df[df['block_id'] == block.block_id]['tile_id'].unique()
            overpass_array = np.zeros(len(masterTiles), dtype=np.uint)*np.nan
            size_array = np.zeros(len(masterTiles), dtype=np.int)*np.nan
            for idx, masterTile in enumerate(masterTiles):
                filename = f'/data/worldcover/auxdata/overpasses_GEE/2019/{masterTile}_20m_2019-01-01_to_2020-01-01_overpass_amount.tif'
                if os.path.isfile(filename):
                    with rasterio.open(filename) as src:
                        if (int(masterTile[1:4]) == 180):
                            shape = shapely.affinity.translate(block.geometry, xoff=360)
                        else:
                            shape = block.geometry
                        try:
                            out_image, out_transform = rasterio.mask.mask(src, [shape], crop=True)
                            overpass_array[idx] = np.median(out_image)
                            size_array[idx] = out_image.shape[1] * out_image.shape[2]
                        except ValueError:
                            print('There is no overlap with this shape, skipping it')
            blocks.loc[num, 'Overpass'] = np.sum(overpass_array * size_array) / np.sum(size_array)
        return blocks

    def _filter_overlap_tiles(self, blocks):
        """
        Remove blocks that fall in the overlab between neighboring tiles

        Only blocks from the last right column and lower row are being removed
        if within a neighboring tile
        """
        s2grid = self.s2grid
        s2tile = self._s2tile.iloc[0]

        neigh_tiles = s2grid[s2grid.intersects(s2tile.geometry) &
                             (s2grid.epsg == s2tile.epsg) &
                             (s2grid.tile != s2tile.tile)]

        # only the last row and last col
        block_ids = np.arange(121).reshape(11, 11)
        block_ids = block_ids[:, -1].tolist() + block_ids[-1, :-1].tolist()

        flag = (blocks.block_id.isin(block_ids) &
                blocks.within(neigh_tiles.unary_union))

        new_blocks = blocks[~flag]

        return new_blocks

    def get_blocks_gdf(self,
                       epsg_filter=True,
                       tile_filter=True,
                       water_filter=True,
                       ice_filter=True,
                       overpass_filter=True):

        new_blocks = self.blocks.copy()

        if epsg_filter:
            new_blocks = self._filter_overlap_epsg(new_blocks)

        if tile_filter:
            new_blocks = self._filter_overlap_tiles(new_blocks)

        if (water_filter) & (len(new_blocks) > 0):
            new_blocks = self._filter_water(new_blocks)

        if (ice_filter) & (len(new_blocks) > 0):
            new_blocks = self._filter_ice(new_blocks)

        if (overpass_filter) & (len(new_blocks) > 0):
            new_blocks = self._filter_overpasses(new_blocks)

        return new_blocks


class S2TileBlocks:
    """Generate blocks GeoDataframes for S2 tiles at custom block size"""

    def __init__(self,
                 block_size,
                 tile_size=10980,
                 resolution=10,
                 s2grid=None):

        self.block_size = block_size
        self._tile_size = tile_size
        self._resolution = resolution

        self._s2grid = (satio.layers.load('s2grid') if s2grid is None
                        else s2grid)
        self._blocks_sizes = self._blocks_sizes()

    def _last_block_side(self):
        return (self._tile_size - (self.block_size *
                                   (self._tile_size // self.block_size)))

    def _blocks_sizes(self):
        tile_size = self._tile_size
        block_size = self.block_size

        n_blocks = tile_size // block_size
        extra_block_size = self._last_block_side()

        blocks_sizes = [block_size for n in range(n_blocks)]
        if extra_block_size:
            blocks_sizes.append(extra_block_size)
        return blocks_sizes

    def _tile_blocks_bounds(self, tile):

        s2grid = self._s2grid
        blocks_sizes = self._blocks_sizes

        bounds = s2grid[s2grid.tile == tile].iloc[0]['bounds']

        xmin = bounds[0]
        ymax = bounds[3]

        blocks_bounds = []

        bxmin = int(xmin)
        bymax = int(ymax)

        for dy in blocks_sizes:
            for dx in blocks_sizes:
                bxmax = bxmin + dx * self._resolution

                bymin = bymax - dy * self._resolution

                bounds = (bxmin, bymin, bxmax, bymax)
                blocks_bounds.append(bounds)

                bxmin = bxmax

            bxmin = int(xmin)
            bymax = bymin

        return blocks_bounds

    def _tile_blocks(self, tile):
        from shapely.geometry import Polygon
        blocks_bounds = self._tile_blocks_bounds(tile)

        epsg = tile_to_epsg(tile)
        gs = gpd.GeoSeries([Polygon.from_bounds(*bs)
                            for bs in blocks_bounds],
                           crs=f"EPSG:{epsg}")
        return gs

    def blocks(self, *tiles):

        s2grid = self._s2grid
        resolution = self._resolution

        tiles_blocks = []

        for t in tiles:
            tblocks = self._tile_blocks(t)
            tblocks_ll = tblocks.to_crs(epsg=4326)
            tiles_blocks += [{'tile': t,
                              'bounds': tuple(np.round(
                                  np.array(b.bounds) / resolution).astype(int)
                                  * resolution),
                              'geometry': tblocks_ll.iloc[i],
                              'area': b.area,
                              'epsg': tile_to_epsg(t),
                              'block_id': i}
                             for i, b in enumerate(tblocks)]
        df = gpd.GeoDataFrame(tiles_blocks, crs="EPSG:4326")

        return df

    def __getitem__(self, tile):
        return self.blocks(tile)


def epsg_point_bounds(p, epsg, dst_epsg,
                      box_pixels_shape_xy,
                      resolution=20):
    """Returns bounds and epsg for a box around the closest pixel corner
    to the given point.
    e.g. starting from a lat lon point, get an epsg box around it"""

    src_epsg = f'EPSG:{epsg}'
    dst_epsg = f'EPSG:{dst_epsg}'

    putm = fiona_transformer(src_epsg, dst_epsg, p)

    box_x = box_pixels_shape_xy[0] * resolution
    box_y = box_pixels_shape_xy[1] * resolution

    # tloc origin
    ox = round((putm.x - box_x/2) / resolution)*resolution
    oy = round((putm.y + box_y/2) / resolution)*resolution

    bounds = ox, oy - box_y, ox + box_x, oy

    return bounds
