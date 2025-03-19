from unittest import TestCase
import tempfile

import geopandas as gpd
import numpy as np
from numpy.testing import assert_array_equal
import rasterio
from shapely.geometry import Polygon

from classifier.accuracy import get_confidence_map_from_random_forest_model
from classifier.accuracy import collect_classification_and_reference

NOISE_FACTOR = 10

class MockTree:
    def predict(self, data):
        return (data + np.random.rand(*data.shape) * NOISE_FACTOR)[0]

class MockModel:
    estimators_ = [MockTree(), MockTree(), MockTree()]


class ConfidenceMapTestCase(TestCase):
    def setUp(self):
        # arrange
        self.test_function = get_confidence_map_from_random_forest_model
        self.array = np.array([
            [[10, 20, 30], [30, 40, 50]],
            [[50, 60, 70], [70, 80, 90]],
        ])

    def test_confidence_map_ok(self):
        # act
        result = self.test_function(MockModel(), self.array, confidence_level=0.95)
        # assert
        self.assertTrue(all(result.ravel() < 5))
        self.assertEqual(result.shape, self.array.shape[-2:])


class AccuracyAssessment(TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.test_dir_path = self.test_dir.name

        # create the test raster
        self.write_test_raster()

    def tearDown(self):
        # Remove the directory after the test
        self.test_dir.cleanup()

    def write_test_polygons(self, polygons_all, polygons_subset):
        # Create GeoDataFrames
        gdf1 = gpd.GeoDataFrame({'geometry': polygons_all, 'id': range(len(polygons_all))})
        gdf2 = gpd.GeoDataFrame({'geometry': polygons_subset, 'id': range(len(polygons_subset))})

        self.test_polygons_all_path = self.test_dir_path + "/test_polygons_all.gpkg"
        self.test_polygons_subset_path = self.test_dir_path + "/test_polygons_subset.gpkg"
        gdf1.to_file(self.test_polygons_all_path, driver="GPKG")
        gdf2.to_file(self.test_polygons_subset_path, driver="GPKG")

    def write_test_raster(self):
        # Define raster properties
        width = 100
        height = 100
        count = 1
        dtype = np.uint8
        crs = None
        data = np.ones(shape=(height, width), dtype=dtype)

        self.test_raster_path = self.test_dir_path + "fake_raster.tif"
        with rasterio.open(
            self.test_raster_path,
            "w",
            driver="GTiff",
            width=width,
            height=height,
            count=count,
            dtype=dtype,
            crs=crs,
        ) as dst:
            dst.write(data, 1)

    def test_collect_classification_and_reference_all_polygons_overlap(self):
        self.write_test_polygons(
            polygons_all=[
                Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]),
                Polygon([(1, 1), (2, 1), (2, 2), (1, 2)]),
                Polygon([(2, 2), (3, 2), (3, 3), (2, 3)]),
            ],
            polygons_subset=[
                Polygon([(0, 0), (0, 5), (5, 5), (5, 0)]),
                Polygon([(1, 1), (2, 1), (2, 2), (1, 2)]),
                Polygon([(2, 2), (3, 2), (3, 3), (2, 3)]),
            ],
        )

        result_y_pred, result_y_true = collect_classification_and_reference(
            raster=self.test_raster_path,
            rois=self.test_polygons_all_path,
            subset=self.test_polygons_subset_path,
        )

        assert result_y_pred.size == result_y_true.size == 0


    def test_collect_classification_and_reference_some_polygons_overlap(self):
        self.write_test_polygons(
            polygons_all=[
                Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]),
                Polygon([(1, 1), (2, 1), (2, 2), (1, 2)]),
                Polygon([(2, 2), (3, 2), (3, 3), (2, 3)]),
            ],
            polygons_subset=[
                Polygon([(1, 1), (2, 1), (2, 2), (1, 2)]),
                Polygon([(2, 2), (3, 2), (3, 3), (2, 3)]),
            ],
        )

        result_y_pred, result_y_true = collect_classification_and_reference(
            raster=self.test_raster_path,
            rois=self.test_polygons_all_path,
            subset=self.test_polygons_subset_path,
        )

        assert_array_equal(result_y_pred, 1)
        assert_array_equal(result_y_true, 0)


    def test_collect_classification_and_reference_no_polygons_overlap(self):
        self.write_test_polygons(
            polygons_all=[
                Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]),
                Polygon([(1, 1), (2, 1), (2, 2), (1, 2)]),
                Polygon([(2, 2), (3, 2), (3, 3), (2, 3)]),
            ],
            polygons_subset=[
                Polygon([(4, 5), (4, 6), (5, 6), (5, 5)]),
                Polygon([(5, 6), (5, 7), (6, 7), (6, 6)]),
                Polygon([(7, 9), (7, 10), (8, 10), (8, 9)]),
            ],
        )

        result_y_pred, result_y_true = collect_classification_and_reference(
            raster=self.test_raster_path,
            rois=self.test_polygons_all_path,
            subset=self.test_polygons_subset_path,
        )
        assert_array_equal(result_y_pred, np.array([1, 1, 1]))
        assert_array_equal(result_y_true, np.array([0, 1, 2]))
