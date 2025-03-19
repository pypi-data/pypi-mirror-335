"Fixture for setting up the tests, yield CliRunner() and tearing them down"
from collections import OrderedDict
import shutil
import os
from pathlib import Path
import fiona
import numpy as np
import pandas as pd
import pytest
import rasterio

from click.testing import CliRunner
from classifier.settings import WORKSPACE

from classifier.utils.general import read_config


@pytest.fixture
def runner(test_arg):
    """Setup, yield CliRunner() and teardown"""
    # setup
    is_timeseries_test = test_arg[0]
    is_supervised_test = test_arg[1]
    rois_outside_test = test_arg[2]

    # Rasters
    nowhere = 0.0
    pixel_size = 2.0

    transform = rasterio.Affine(
        pixel_size,
        nowhere,
        nowhere,
        nowhere,
        -pixel_size,
        nowhere
    )

    raster_folder = WORKSPACE / "integration_test_rasters"
    raster_folder.mkdir()

    if is_timeseries_test:
        raster_names = ['test_raster_008570_2020-07-01T000000Z_mean.tif',
                        'test_raster_008570_2020-08-01T000000Z_mean.tif',
                        'test_raster_008570_2020-09-01T000000Z_mean.tif']
    else:
        raster_names = ['test_raster_008570_2020-07-01T000000Z_mean.tif']
    raster_paths = [raster_folder / raster_name
                    for raster_name in raster_names]

    raster_values = [
        np.array([
            np.full((10, 10), [1, 1, 1, 1, 1, 100, 100, 100, 100, 100]),
            np.full((10, 10), [2, 2, 2, 2, 2, 101, 101, 101, 101, 101])
        ]),
        np.array([
            np.full((10, 10), [2, 2, 2, 2, 2, 102, 102, 102, 102, 102]),
            np.full((10, 10), [4, 4, 4, 4, 4, 103, 103, 103, 103, 103])
        ]),
        np.array([
            np.full((10, 10), [1, 1, 1, 1, 1, 103, 103, 103, 103, 103]),
            np.full((10, 10), [3, 3, 3, 3, 3, 105, 105, 105, 105, 105])
        ]),
    ]

    for raster_path, data in zip(raster_paths, raster_values):
        with rasterio.open(
            raster_path,
            'w',
            driver='GTiff',
            height=data.shape[1],
            width=data.shape[2],
            count=data.shape[0],
            dtype='float32',
            crs='+proj=latlong',
            nodata=np.nan,
            transform=transform
        ) as dst:
            dst.write(data)

    if is_supervised_test:
        # Train polygons
        x_min, y_min, x_max, y_max = 0, -20, 10, 0
        window_polygon_1 = [[(x_min, y_min),
                             (x_min, y_max),
                             (x_max, y_max),
                             (x_max, y_min)]]

        if rois_outside_test:
            # partially outside
            x_min, y_min, x_max, y_max = 10, -20, 20, 0
            window_polygon_2 = [[(x_min, y_min),
                                 (x_min, y_max),
                                 (x_max, y_max),
                                 (x_max, y_min)]]
            # completely outside
            x_min, y_min, x_max, y_max = 30, -40, 40, -20
            window_polygon_3 = [[(x_min, y_min),
                                 (x_min, y_max),
                                 (x_max, y_max),
                                 (x_max, y_min)]]

        else:
            x_min, y_min, x_max, y_max = 10, -20, 20, 0
            window_polygon_2 = [[(x_min, y_min),
                                 (x_min, y_max),
                                 (x_max, y_max),
                                 (x_max, y_min)]]

        polygon1 = {
            "properties": {
                "id": 0,
                "fid": 1
            },
            "geometry": {
                "coordinates": window_polygon_1,
                "type": "Polygon"
            }
        }
        polygon2 = {
            "type": "Feature",
                    "properties": {
                        "id": 1,
                        "fid": 2
                    },
            "geometry": {
                        "coordinates": window_polygon_2,
                        "type": "Polygon"
                    }
        }

        if rois_outside_test:
            polygon3 = {
                "type": "Feature",
                "properties": {
                        "id": 1,
                        "fid": 3
                },
                "geometry": {
                    "coordinates": window_polygon_3,
                    "type": "Polygon"
                }
            }
            train_polygons = [polygon1, polygon2, polygon3]
        else:
            train_polygons = [polygon1, polygon2]

        schema = {
            "geometry": "Polygon",
            "properties": OrderedDict([("id", "int"), ("fid", "int")])
        }
        rois_path = WORKSPACE / 'integration_test_rois.gpkg'
        with fiona.open(rois_path,
                        "w",
                        driver="GPKG",
                        crs="+proj=latlong",
                        schema=schema) as src:
            src.writerecords(train_polygons)

    yield CliRunner()

    # teardown
    shutil.rmtree(WORKSPACE / "integration_test_rasters")
    if is_supervised_test:
        os.remove(WORKSPACE / 'integration_test_rois.gpkg')
    # Delete classification result
    shutil.rmtree(WORKSPACE / "test_result")


@pytest.fixture
def setup_config():
    return read_config(Path(""))


@pytest.fixture
def setup_samples_df():
    data = np.array([[1.51, 4.57, 1],
                     [1.46, 4.61, 1],
                     [1.52, 4.53, 1],
                     [4.01, 2.03, 2],
                     [4.01, 2.01, 2],
                     [4.01, 2.02, 2],
                     ])
    columns = ("test_raster_008570_2020-07-01T000000Z_mean.tif_1",
               "test_raster_008570_2020-07-01T000000Z_mean.tif_2", "class")
    samples_test = pd.DataFrame(data, columns=columns)
    return samples_test


@pytest.fixture
def setup_samples_df_with_outliers():
    data = np.array([[1.51, 4.57, 1],
                     [1.46, 4.61, 1],
                     [6.04, 4.54, 1],  # outlier
                     [1.52, 4.53, 1],
                     [4.01, 2.03, 2],
                     [4.01, 2.01, 2],
                     [4.01, 2.02, 2],
                     [4.01, 5.02, 2],  # outlier
                     ])
    columns = ("test_raster_008570_2020-07-01T000000Z_mean.tif_1",
               "test_raster_008570_2020-07-01T000000Z_mean.tif_2", "class")
    samples_test = pd.DataFrame(data, columns=columns)
    return samples_test


@pytest.fixture
def setup_samples_df_with_nans():
    data = np.array([[1., 4., 2., np.nan, 3., np.nan],
                     [np.nan, 4., 2., 6., 3., 8.],
                     [1., 4., 2., 6., 3., np.nan],
                     [1., 4., np.nan, 6., 3., 8.],
                     ])

    roi_classes = [0, 0, 1, 1]
    roi_fids = [1, 1, 2, 2]
    pixel_ids = [0, 1, 2, 3]
    dates = pd.to_datetime(['2020-07-01', '2020-08-01', '2020-09-01'])
    bands = ['B01', 'B02']

    index = pd.MultiIndex.from_tuples(
        list(zip(roi_classes, roi_fids, pixel_ids)),
        names=['class', 'roi_fid', 'pixel_id']
    )
    columns = pd.MultiIndex.from_product(
        [dates, bands],
        names=['Date', 'Band']
    )
    samples_test = pd.DataFrame(data, index=index, columns=columns)
    return samples_test


@pytest.fixture
def setup_samples_df_with_nans_ref():
    data = np.array([[1., 4., 2., 4., 3., 4.],
                     [2., 4., 2., 6., 3., 8.],
                     [1., 4., 2., 6., 3., 6.],
                     [1., 4., 2., 6., 3., 8.],
                     ])

    roi_classes = [0, 0, 1, 1]
    roi_fids = [1, 1, 2, 2]
    pixel_ids = [0, 1, 2, 3]
    dates = pd.to_datetime(['2020-07-01', '2020-08-01', '2020-09-01'])
    bands = ['B01', 'B02']

    index = pd.MultiIndex.from_tuples(
        list(zip(roi_classes, roi_fids, pixel_ids)),
        names=['class', 'roi_fid', 'pixel_id']
    )
    columns = pd.MultiIndex.from_product(
        [dates, bands],
        names=['Date', 'Band']
    )
    samples_test = pd.DataFrame(data, index=index, columns=columns)
    return samples_test

@pytest.fixture
def setup_samples_df_with_rois_fid():
    data = np.array([[1., 4.],
                    [2., 3.],
                    [1., 7.],
                    [1., 8.],
                    ])
        
    roi_classes = [0, 0, 1, 1]
    roi_fids = [1, 1, 2, 2]
    pixel_ids = [0, 1, 0, 1]
    bands = ['B01', 'B02']

    index = pd.MultiIndex.from_tuples(
        list(zip(roi_classes, roi_fids, pixel_ids)),
        names=['class', 'roi_fid', 'pixel_id']
    )
    columns = ['band0', 'band1']
    samples_test = pd.DataFrame(data, index=index, columns=columns)
    return samples_test

@pytest.fixture
def setup_samples_df_with_rois_fid_subsampled():
    data = np.array([[2., 3.],
                    [1., 7.],
                    ])
        
    roi_classes = [0, 1]
    roi_fids = [1, 2]
    pixel_ids = [1, 0]
    bands = ['B01', 'B02']

    index = pd.MultiIndex.from_tuples(
        list(zip(roi_classes, roi_fids, pixel_ids)),
        names=['class', 'roi_fid', 'pixel_id']
    )
    columns = ['band0', 'band1']
    samples_test = pd.DataFrame(data, index=index, columns=columns)
    return samples_test
