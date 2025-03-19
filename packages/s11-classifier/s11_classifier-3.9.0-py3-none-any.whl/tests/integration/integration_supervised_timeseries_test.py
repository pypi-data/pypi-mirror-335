"Supervised timeseries integration test for classifier"
import numpy as np
import pytest
import rasterio
from classifier.cli import classification
from classifier.settings import WORKSPACE
from classifier.utils.general import save_config_as_json


@pytest.mark.parametrize('test_arg',
                         [[True, True, False]])
def test_supervised_timeseries_randomforest(runner):
    """
    Test for running a supervised randomforest classification
    on a timeseries
    """
    save_config_as_json(threads=1, algorithm="randomforest",
                        remove_outliers=False,
                        rasters_are_timeseries=True)

    rois_path = WORKSPACE / 'integration_test_rois.gpkg'
    runner.invoke(classification, [
        "--name", 'test_result', '--overwrite', True,
        '--rois', rois_path, "integration_test_rasters"])
    directory = WORKSPACE / 'test_result' / 'classification.tif'
    with rasterio.open(directory, 'r') as dst:
        result = dst.read(1)
        assert np.all(result[:, 0:4] == 0)
        assert np.all(result[:, 5:10] == 1)


@pytest.mark.parametrize('test_arg',
                         [[True, True, False]])
def test_supervised_timeseries_xgboost(runner):
    """
    Test for running a supervised xgboost classification
    on a timeseries
    """
    save_config_as_json(threads=1, algorithm="xgboost",
                        remove_outliers=False, rasters_are_timeseries=True)

    rois_path = WORKSPACE / 'integration_test_rois.gpkg'
    runner.invoke(classification, [
        "--name", 'test_result', '--overwrite', True,
        '--rois', rois_path, "integration_test_rasters"])
    directory = WORKSPACE / 'test_result' / 'classification.tif'
    with rasterio.open(directory, 'r') as dst:
        result = dst.read(1)
        assert np.all(result[:, 0:4] == 0)
        assert np.all(result[:, 5:10] == 1)


@pytest.mark.parametrize('test_arg',
                         [[True, True, False]])
def test_supervised_timeseries_knndtw(runner):
    """
    Test for running a supervised knn classification
    on a timeseries
    """
    save_config_as_json(threads=1, algorithm="knn_dtw",
                        remove_outliers=False, rasters_are_timeseries=True)

    rois_path = WORKSPACE / 'integration_test_rois.gpkg'

    runner.invoke(classification, [
        "--name", 'test_result', '--overwrite', True,
        '--rois', rois_path, "integration_test_rasters"], catch_exceptions=False)
    directory = WORKSPACE / 'test_result' / 'classification.tif'
    with rasterio.open(directory, 'r') as dst:
        result = dst.read(1)
        assert np.all(result[:, 0:4] == 0)
        assert np.all(result[:, 5:10] == 1)
