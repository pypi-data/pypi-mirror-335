from unittest import TestCase
import tempfile

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import Polygon

from classifier.utils.vector import create_spatial_index, true_intersect


class TestCreateSpatialIndex(TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.test_dir_path = self.test_dir.name

    def tearDown(self):
        # Remove the directory after the test
        self.test_dir.cleanup()
        
    def write_test_polygons(self, polygons):
        # Create GeoDataFrames
        gdf = gpd.GeoDataFrame({'geometry': polygons, 'id': range(len(polygons))})
        self.test_polygons_path = self.test_dir_path + "/test_polygons_all.gpkg"
        gdf.to_file(self.test_polygons_path, driver="GPKG")

    def test_empty_input(self):
        self.write_test_polygons([])
        # Call the function with the empty path
        index = create_spatial_index(self.test_polygons_path)

        # Assert that the index is empty
        self.assertEqual(len(list(index.intersection((-180, -90, 180, 90)))), 0)

    def test_non_empty_input(self):
        # Create a temporary file with sample polygons
        polygons = [
            Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]),
            Polygon([(2, 2), (3, 2), (3, 3), (2, 3)])
        ]
        self.write_test_polygons(polygons)

        # Call the function with the temporary file
        index = create_spatial_index(self.test_polygons_path)

        # Assert that the index contains both polygons
        self.assertEqual(len(list(index.intersection((0, 0, 3, 3)))), 2)


class TestTrueIntersect(TestCase):
    def test_no_overlap(self):
        # Create two polygons with no overlap
        geom_1 = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])
        geom_2 = Polygon([(2, 2), (3, 2), (3, 3), (2, 3)])

        result = true_intersect(geom_1, geom_2)

        self.assertFalse(result)
        
    def test_partial_overlap(self):
        # Create two polygons with partial overlap
        geom_1 = Polygon([(0, 0), (2, 0), (2, 2), (0, 2)])
        geom_2 = Polygon([(1, 1), (3, 1), (3, 3), (1, 3)])

        result = true_intersect(geom_1, geom_2)

        self.assertTrue(result)

    def test_full_overlap(self):
        # Create two polygons with full overlap
        geom_1 = Polygon([(0, 0), (2, 0), (2, 2), (0, 2), (0, 0)])
        geom_2 = Polygon([(1, 1), (3, 1), (3, 3), (1, 3), (1, 1)])

        result = true_intersect(geom_1, geom_2)

        self.assertTrue(result)