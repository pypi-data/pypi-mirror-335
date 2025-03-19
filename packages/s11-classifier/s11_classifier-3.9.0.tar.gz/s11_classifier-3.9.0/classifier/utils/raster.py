"""Raster Utilities"""
# pylint: disable=cyclic-import
import itertools
import logging
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
import rasterio
from rasterio import mask
from rasterio.windows import Window
from shapely.geometry import MultiPolygon, Polygon

from classifier.utils.config import Configuration

UTILS_RASTER_LOGGER = logging.getLogger(__name__)


def stitch_(out_ds: str, temp_dir: str,
            meta: dict, dtype: str = 'Int32') -> None:
    """Stitch all tifs together to a single tif

    Args:
        out_ds (str): output file
        temp_dir (str): The temp directory containing the tifs
        meta (dict): rasterio meta dictionary for output
        dtype (dtype): the raster's dtype

    """
    filelist = [os.path.join(temp_dir, x) for x in os.listdir(temp_dir) if
                x.endswith('tif')]
    input_list = temp_dir+'input_list.txt'
    with open(input_list, 'w', encoding='UTF-8') as tif_list:
        for files in filelist:
            tif_list.write(f'{files}\n')
    cmd_pred = (
        f"""gdalbuildvrt -srcnodata {meta['dst_meta']['nodata']} \
        {out_ds}.vrt \
        -q \
        -input_file_list {input_list}
        """
    )
    subprocess.call(cmd_pred, shell=True)
    cmd_pred = (
        f"""
        gdalwarp -ot {dtype} -q -multi -wo "NUM_THREADS=ALL_CPUS" -co \
        "TILED=YES"  -co "COMPRESS=DEFLATE" -co "BIGTIFF=YES" -overwrite \
        -srcnodata {meta['dst_meta']['nodata']} {out_ds}.vrt {out_ds}.tif
        """
    )
    subprocess.call(cmd_pred, shell=True)
    os.remove(out_ds+'.vrt')


def stitch(out_prefix: Path, meta: dict, config: Configuration) -> None:
    """Stitch the temporary files together

    Args:
        out_prefix (Path)): The output directory
        meta (dict): The rasterio meta dicts from source, destination and
                     dest_proba
        config (Configuration): contains config

    """
    # Find all directories that have chunks.
    dirs = list(x for x in os.listdir(config.tmp_dir.name))
    for directories in dirs:
        if directories.startswith('class'):
            out_file = out_prefix / 'classification'
            dtype = 'Int32'
        elif directories.startswith('probab'):
            out_file = out_prefix / 'probability'
            dtype = 'Float32'
        else:
            out_file = out_prefix / directories
            dtype = 'Float32'
        UTILS_RASTER_LOGGER.info("Now stitching %s", out_file)
        stitch_(out_file.as_posix(),
                os.path.join(config.tmp_dir.name, directories),
                meta,
                dtype)


def get_meta(rasters: List[Path],
             window_size: int = 1024) -> Tuple[List[Tuple[int, Window]],
                                               dict]:
    """ Get the metadata from the input file and create the windows list to
    iterate through

    Args:
        rasters (List[Path]): List of rasters
        window_size (int): The size of the windows that will be processed

    Returns:
        windows (List[int, Window]): List containing number of window and window
        dict: Containing info for rasterio write tiff
    """

    first_raster = rasters[0]
    # Read the metadata of the first and return metadata for dst and dst_proba
    with rasterio.open(first_raster, 'r') as first:
        f_meta = first.meta
        meta = f_meta.copy()
        meta.update(dtype=rasterio.dtypes.int32, nodata=-9999, count=1,
                    driver='GTiff')
        # Create the windows
        col_offs = np.arange(0, first.width, window_size)
        row_offs = np.arange(0, first.height, window_size)
        window_tuples = [x + (window_size, window_size) for x in list(
            itertools.product(col_offs, row_offs))]
        winlist = [rasterio.windows.Window(*x) for x in window_tuples]
        windows = list(zip(range(len(winlist)), winlist))
        meta_proba = meta.copy()
        meta_proba.update(dtype=rasterio.dtypes.float32, nodata=-9999)
    bandcount = []
    for raster in rasters:
        with rasterio.open(raster, 'r') as src_r:
            bandcount.append(src_r.count)
    return windows, {'f_meta': f_meta, 'dst_meta': meta,
                     'dst_proba_meta': meta_proba,
                     'bandcount': np.sum(bandcount)}


def open_single_raster(raster_path: Path, window: Optional[Window] = None)\
        -> Tuple[np.ndarray, dict]:
    """Opens single raster and returns numpy array.

    Array shape: nbands x nrows x ncols.

    Args:
        raster_path(Path): location of the raster file
        window (rasterio.Window): subset window

    Returns:
        raster_array (np.ndarray): Raster data
        meta (dict): dictionary with raster metadata
    """

    with rasterio.open(raster_path, 'r') as raster:
        raster_array = raster.read(window=window)
        meta = raster.meta
        meta.update(
            width=raster_array.shape[2],
            height=raster_array.shape[1],
            transform=raster.window_transform(window))
        return raster_array, meta


def get_raster_date(raster: Path) -> Any:
    """Gets the date of a tif file from the name. The pattern that is expected
    is YYYY-MM-DD.

    If there are multiple dates with that format in the filename, only the
    first one will be used

    Args:
        raster (Path) : Path to raster file
    Returns:
        file_date (str): date of the raster in string format
    """
    file_date = re.findall(r'\d\d\d\d-\d\d-\d\d', raster.as_posix())[0]
    return file_date

def count_bands(raster: Path) -> int:
    """Returns number of bands of a raster

    Args:
        raster (Path): path to raster file

    Returns:
        (int): Number of bands of a raster


    """
    with rasterio.open(raster, 'r') as src:
        return int(src.count)


def verify_and_count_bands(rasters: List[Path]) -> int:
    """Counts the number of bands for all the rasters and makes sure they all
    have the same number bands. Then it returns the number of bands that the
    rasters have

        Args:
            rasters(List[Path]): list of raster files

        Returns:
            b_count (int): number of bands in each raster

    """
    n_bands_list = [count_bands(raster) for raster in rasters]
    count = set(n_bands_list)
    if len(count) > 1:
        UTILS_RASTER_LOGGER.error("Number of bands per raster is not equal. "
                                  "Quitting...")
        sys.exit()
    return count.pop()


def get_bandnames(rasters: List[Path]) -> List[str]:
    """Get the filenames and add a number for the bands

    Args:
        rasters (List[Path]): The list of input rasters

    Returns:
        bandnames (List[str]): List of rasternames and bandsuffixes
    """
    bandnames = []
    for files in rasters:
        rastername = files.stem
        with rasterio.open(files) as src:
            nr_bands = src.count
            bandnames.extend([f'{rastername}_{x}' for x in
                              np.arange(1, nr_bands+1)])
    return bandnames


def clip_raster_on_geometry(
        raster_file: Path,
        geometry: Union[Polygon, MultiPolygon]
) -> np.ndarray:
    """Clip a raster using a geometry and an optional window

        Args:
            raster_file (Path): path to gdal supported raster file
            geometry (Polygon or Multipolygon): Geometry to use for clipping
            window (rasterio.Window): window to use for opening the raster
    """
    with rasterio.open(raster_file) as src:
        selection, _, window = mask.raster_geometry_mask(
            src,
            [geometry],
            crop=True)
        raster_subset = src.read(window=window)
        # For each raster extract all band values.
        # Shape: rows=bands, columns=samples

        # rasterio convention: outside shape=True, inside=False.
        # We invert.
        return raster_subset[:, ~selection]


def ndarray_to_df(
        array: np.ndarray,
        nodata: int | float = -9999
) -> pd.DataFrame:
    """Convert numpy array to pandas dataframe with each column a flattened band

    Args:
        array (np.ndarray): input data array

    Returns:
        pd.DataFrame: dataframe with each band flattened per column
    """
    nr_bands = array.shape[0] if len(array.shape) == 3 else 1
    dataframe = pd.DataFrame()
    for i in np.arange(nr_bands):
        if nr_bands == 1:
            band = array
        else:
            band = array[i, :, :]
        band[np.isnan(band)] = nodata
        band[np.isinf(band)] = nodata
        dataframe[i] = band.flatten()
    return dataframe
