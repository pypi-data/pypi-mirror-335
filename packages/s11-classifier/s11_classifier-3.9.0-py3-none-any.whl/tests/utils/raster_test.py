from unittest import TestCase

import numpy as np
import pandas as pd

from classifier.utils.raster import ndarray_to_df


class NdarrayToDfTestCase(TestCase):
    def setUp(self):
        self.test_function = ndarray_to_df

    def test_convert_ndarray_to_df_ok(self):
        # arrange
        array = np.array([[[1,2], [3,4]], [[5,6], [7,8]]])
        # act
        result = self.test_function(array)
        # assert
        expected_result = pd.DataFrame([[1,5], [2,6], [3,7], [4,8]])
        self.assertTrue(result.equals(expected_result))

    def test_convert_ndarray_to_df_with_nan_ok(self):
        # arrange
        array = np.array([[[1,2], [3,4]], [[5,6], [7,np.nan]]])
        expected_result = pd.DataFrame([[1,5], [2,6], [3,7], [4,-9999]], dtype=float)
        # act
        result = self.test_function(array)
        # assert
        self.assertTrue(result.equals(expected_result))
