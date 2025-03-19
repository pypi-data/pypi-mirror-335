"""Vector utilities"""
import logging
from pathlib import Path
from typing import Optional, Any

import geopandas as gpd
import numpy as np
import fiona
import rasterio
from geopandas import GeoDataFrame
from rasterio import Affine
from rasterio.features import shapes
from rasterio.windows import Window
from rtree.index import Index
from shapely.geometry.base import BaseGeometry
from shapely.geometry import MultiPolygon, Polygon, shape

UTILS_VECTOR_LOGGER = logging.getLogger(__name__)


def vectorize_array(
        array_to_vectorize: np.ndarray,
        transform: Optional[Affine] = None) -> GeoDataFrame:
    """Vectorize a tif file and return geodataframe.

    Args
        array_to_vectorize (array): Array to vectorize_and_classify
        transform (Affine): Affine transformation

    Returns:
        GeoDataFrame: geodataframe with polygons

    """
    polygonized = shapes(array_to_vectorize,
                         connectivity=8,
                         transform=transform)
    shapelist, valuelist = zip(*polygonized)
    shapelist = [Polygon(x['coordinates'][0]) for x in shapelist]
    new_poly_dict = {'geometry': shapelist, 'segment_id': valuelist}

    return gpd.GeoDataFrame.from_dict(new_poly_dict)


def get_subset_of_polygons(
        window: Window, transform: dict, polygons: GeoDataFrame,
        col_name: str = 'max') -> list:
    """Get a subset of a geodataframe from a rasterio window

    Uses a rasterio window to make an intersection on the whole polygon
    dataframe.

    Args:
        window (rasterio.Window): window of interest
        transform (dict):   transform of the window
        polygons (GeoDataFrame): polygons to classify
        col_name (str): Name of the column to subset

    Returns:
        list of [geometry, value] pairs that can be consumed by GeoPandas

    """
    left, bottom, right, top = rasterio.windows.bounds(window,
                                                       transform)

    window_polygon = Polygon([[left, bottom],
                              [left, top],
                              [right, top],
                              [right, bottom]])

    window_df = gpd.GeoDataFrame({'geometry': [window_polygon],
                                  'name': [1]})
    window_df.crs = {'init': 'epsg:4326'}

    subset_polygons = gpd.overlay(window_df,
                                  polygons,
                                  how='intersection')

    return list(zip(list(subset_polygons['geometry'].values),
                    list(subset_polygons[col_name].values)))


def gdf_polygon_to_multipolygon(gdf: GeoDataFrame) -> GeoDataFrame:
    """Converts all geometries to multipolyon, so there are no issues when
    saving these to a file and adds a crs (epsg:4326) to the gdf

    Args:
        gdf (GeoDataFrame): Containing polygons

    Returns:
        gdf (GeoDataFrame): GDF with all polygons converted to multipolygons

    """
    geometry = [MultiPolygon([feature]) if isinstance(feature, Polygon)
                else feature for feature in gdf["geometry"]]
    return geometry


def get_rois_extent(rois: Path) -> Any:
    """

    Args:
        rois (Path): path to a rois file

    Returns:
        bounds of rois (list): ulx, uly, llx, lly coordinates

    """
    with fiona.open(rois, "r") as shapefile:
        return shapefile.bounds


def create_spatial_index(rois: Path) -> Index:
    """Create an RTree spatial index filled with the bboxes of the polygons

    Args:
        rois (Path): rois path

    Returns:
        Index: rtree index
    """
    rtree_index = Index()
    with fiona.open(rois) as polygons:
        for fid, feature in polygons.items():
            geometry = shape(feature['geometry'])
            rtree_index.insert(fid, geometry.bounds)
    return rtree_index


def true_intersect(geom_1: BaseGeometry, geom_2: BaseGeometry) -> bool:
    """Check for a true intersection (not only touch, but overlap)

    Args:
        geom_1 (BaseGeometry): geometry 1
        geom_2 (BaseGeometry): geometry 2

    Returns:
        bool: true if true intersection
    """
    return bool(geom_1.relate_pattern(
        geom_2, 'T********'
    ))
