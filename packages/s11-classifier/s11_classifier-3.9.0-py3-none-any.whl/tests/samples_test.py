"Test for samples module"
import numpy as np
import pandas as pd
from classifier.samples import Samples, TimeSeries
from classifier.utils.config import setup_config, SubsampleSupervisedConfiguration


def test_impute_timeseries_AsExpected(
        setup_samples_df_with_nans_ref, setup_samples_df_with_nans):
    ref_samples = setup_samples_df_with_nans_ref
    timeseries = TimeSeries(None, None, None)

    timeseries_imputed = timeseries.impute_ts(setup_samples_df_with_nans)
    assert np.array_equal(
        ref_samples.to_numpy(),
        timeseries_imputed.to_numpy())


def test_outlier_removal_RemovedAsExpected(
        setup_samples_df, setup_samples_df_with_outliers):
    config = setup_config()
    
    ref_samples = setup_samples_df
    samples_outlier_removed = Samples.outlier_removal(
        setup_samples_df_with_outliers, config)
    np.array_equal(ref_samples.values, samples_outlier_removed.values)
    
    
def test_subsample_AsExpected(
        setup_samples_df_with_rois_fid, setup_samples_df_with_rois_fid_subsampled):
    samples = setup_samples_df_with_rois_fid
    
    config = SubsampleSupervisedConfiguration(
        active=True,
        group_by='roi_fid',
        sample_type='n',
        amount=1,
        replace=False
    )

    samples_subsampled = Samples.subsample(samples, config)
    pd.testing.assert_frame_equal(samples_subsampled, setup_samples_df_with_rois_fid_subsampled)