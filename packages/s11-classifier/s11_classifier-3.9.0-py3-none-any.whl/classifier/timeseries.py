"""All timeseries functionality can be found here"""
# pylint: disable=too-many-positional-arguments
import logging
import warnings
from pathlib import Path
from typing import Optional, Any, List, Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from dtaidistance import dtw, dtw_ndim

# pylint: disable=R0917

warnings.simplefilter(action='ignore', category=pd.errors.PerformanceWarning)

TIMESERIES_MODULE_LOGGER = logging.getLogger(__name__)


def dtw_metric(ts1: np.ndarray, ts2: np.ndarray, raster_count: int,
               band_count: int, window: Optional[int] = None,
               max_dist: Optional[float] = None, use_pruning: bool = False,
               penalty: Optional[float] = None) -> Any:
    """Metric function for KNearest-Neighbor classification.
       Uses Dynamic-time-warping (DTW) algorithm as distance function.

        Args:
            ts1 (np.ndarray): timeseries reference
            ts2 (np.ndarray): timeseries sample
            raster_count (int): Number of rasters
            band_count (int): Number of bands
            window (int): window constraint
            max_dist (float): max dist to stop dist computation
            use_pruning (bool): set euclidean dist as max_dist
            penalty (float): penalty to add for compression/expansion

        Returns:
            dtw_dist (float): dtw distance
    """

    if band_count == 1:
        return dtw.distance_fast(
            ts1, ts2,
            window=window,
            max_dist=max_dist,
            use_pruning=use_pruning,
            penalty=penalty
        )
    # nD-case
    ts1 = ts1.reshape(raster_count, band_count)
    ts2 = ts2.reshape(raster_count, band_count)

    # (Dependent) Dynamic Time Warping using multidimensional sequences.
    # For independent DTW (DTW_I) distance, rewrite to
    # use the 1-dimensional version in a loop
    # dtw_ndim.distance(ts1, ts2, use_c=True, max_dist=2.5, window=5)
    # 1d version in loop MUCH SLOWER
    # dtw_i = 0
    # for dim in range(band_count):
    #     dtw_i += dtw.distance(ts1[:, dim], ts2[:, dim])
    return dtw_ndim.distance_fast(
        ts1.astype(np.double), ts2.astype(np.double),
        window=window,
        max_dist=max_dist,
        use_pruning=use_pruning,
        penalty=penalty
    )


def get_characteristic_timeseries_per_class(
        train_dataset: pd.DataFrame,
        patterns_per_class_nr: int) -> List[pd.DataFrame]:
    """ Builds the mean of the band values for each timestep and class.
    If optimize, it uses 5 subsets instead of all the data to build the
    mean values for each of the subsets. Can then be used to find the best
    subset.

    Args:
        train_dataset (pd.DataFrame): _description_
        patterns_per_class_nr (int): _description_

    Returns:
        pd.DataFrame: _description_
    """

    all_mean_values_per_class = []
    train_dataset = train_dataset.sort_index(level=[0, 1])

    for i in range(patterns_per_class_nr):
        # build median per roi
        train_dataset = train_dataset.astype(
            {"roi_fid": int})

        # When multiple patterns per class are created, use
        # subsets of the roi in each run to have variations
        if patterns_per_class_nr > 1:
            mean_per_roi = train_dataset.groupby(
                ['roi_fid']).mean().sample(frac=1/3)
        else:
            mean_per_roi = train_dataset.groupby(
                ['roi_fid']).mean()

        # build median of all same class rois
        mean_per_roi['class'] = mean_per_roi['class'].astype(
            int).astype(str)

        mean_values_per_class = mean_per_roi.groupby(['class']).mean()

        # Dates column becomes index
        mean_values_per_class = mean_values_per_class.stack(0)

        # Set column names to band_names
        # Convert dates to datetime
        mean_values_per_class = mean_values_per_class.reset_index(level=-1)
        mean_values_per_class['Date'] = pd.to_datetime(
            mean_values_per_class['Date'])
        mean_values_per_class = mean_values_per_class.set_index(
            mean_values_per_class['Date'], append=True)
        mean_values_per_class.drop(['Date'], axis=1, inplace=True)

        # extra index "Pattern Set" to
        # distinguish the subset results
        mean_values_per_class["Pattern Set"] = i
        mean_values_per_class = mean_values_per_class.set_index(
            mean_values_per_class['Pattern Set'], append=True)
        mean_values_per_class = mean_values_per_class.drop(
            ['Pattern Set'], axis=1)
        mean_values_per_class = mean_values_per_class.swaplevel(0, 2)

        all_mean_values_per_class.append(mean_values_per_class)
    all_mean_values_per_class = pd.concat(all_mean_values_per_class, axis=0)
    return all_mean_values_per_class


def get_dataset_dates_as_days(
        all_mean_values_per_class: pd.DataFrame) -> Union[
            np.ndarray, List[int]]:
    """Get Dates from dataframe and convert to days, starting at 0.

    Args:
        all_mean_values_per_class (pd.DataFrame):
            Contains a Dataframe with band and dates as column index

    Returns:
        x_days (np.ndarray): contains dates converted to days starting
            at 0.
        date_index (list): contains dates as strings
    """
    date_index = all_mean_values_per_class.index.get_level_values(
        1).unique().tolist()
    # convert to datetime
    dates_datetime = [date.to_pydatetime() for date in date_index]
    # build diff of dates
    date_differences = [
        (dates_datetime[i + 1] - dates_datetime[i]).days
        for i in range(0, len(dates_datetime) - 1)]
    date_differences_added = [0]
    for i, date_diff in enumerate(date_differences):
        date_differences_added.append(
            date_differences_added[i] + date_diff)
    x_days = np.array(date_differences_added)
    return x_days, date_index


def create_training_patterns(
        patterns: pd.DataFrame,
        band_names: List[str],
        class_names: list,
        patterns_per_class: int,
        out_dir: Optional[Path] = None) -> pd.DataFrame:
    """ This function uses values for each class to create training
    patterns. It either uses just the mean values which are already
    given to the function or it uses a GAM (Generalized Adversial Model)
    on the average values for each class. The GAM then creates a smooth
    course of the values (like a linear regression)

    Args:
        patterns (List[pd.DataFrame]): Patterns
        band_names (List[str]): Band Names
        class_names (list): Class Names (here id)
        patterns_per_class (int): Number of patterns per class
        out_dir (Path): Output path

    Returns:
        List[pd.DataFrame]: Contains of the found characteristic timeseries
        found for each class and band
    """
    # Figure for plotting the patterns
    _, axes = plt.subplots(
        len(class_names) * patterns_per_class, len(band_names),
        figsize=(len(band_names) * 15, len(class_names) * 10))
    # pylint: disable=invalid-name

    # Convert the dataset dates to days (starting at 0)
    x_days, date_index = get_dataset_dates_as_days(patterns)

    # Add extra dim for gam gridsearch function
    x_days = np.expand_dims(x_days, axis=1)
    predict_dates = x_days.tolist()

    all_patterns_all_subsets = []

    # Iterate through the multiple run dataframes
    # (multiple patterns per class)
    for subset_pattern_id, subset_pattern_df in patterns.groupby(
            level=0, axis=0):

        subset_pattern_df.index = subset_pattern_df.index.droplevel([0, 1])
        all_patterns_per_subset = []

        class_ids = subset_pattern_df.index.unique()

        # Iterates through alle classes and bands and creates characteristic
        # timeseries for each.
        for class_id_i, class_id in enumerate(class_ids):
            all_patterns_per_class_per_band = []

            # Index for plot
            i = (subset_pattern_id*len(class_ids))+int(class_id_i)

            for j, band_name in enumerate(band_names):
                # Extract values for given class and band
                y_values = subset_pattern_df[band_name][class_id]

                axes[i, j].plot(x_days, y_values, 'r')
                axes[i, j].set_title(
                    f"Class id: {class_id}, Band name: {band_name}")
                axes[i, j].scatter(x_days, y_values,
                                   facecolor='gray', edgecolors='none')

                all_patterns_per_class_per_band.append(y_values)
            values_reshaped = np.array(
                all_patterns_per_class_per_band).flatten('F')

            # Create a dataframe with the results.
            # Columns are the dates and bands
            # 1 Row are the values for 1 class

            # Column names
            columns = []
            for date in date_index:
                for band_name in band_names:
                    columns.append(f"{date} {band_name}")
            # cut it off for only predict dates range
            columns = columns[:len(predict_dates)*len(band_names)]

            # Create Dataframe
            df_values = pd.DataFrame(values_reshaped, columns).T
            df_values['class'] = int(class_id)
            all_patterns_per_subset.append(df_values)

        all_patterns_per_subset = pd.concat(all_patterns_per_subset, axis=0)
        all_patterns_all_subsets.append(all_patterns_per_subset)
    all_patterns_all_subsets = pd.concat(all_patterns_all_subsets, axis=0)
    if out_dir is not None:
        plt.savefig(out_dir / "training_patterns.png", dpi=300)
    return all_patterns_all_subsets


def get_characteristic_timeseries(
        dataset: pd.DataFrame,
        number_of_patterns_per_class: int,
        out_dir: Path) -> pd.DataFrame:
    """ Extract timeseries from every roi and then use timeseries clustering
        to combine them to class characteristic timeseries

        Args:
            dataset (pd.DataFrame): sampled pixels
            number_of_patterns_per_class (int): Number of characteristic
                timeseries per class to create
            out_dir (Path): The output directory

        Returns:
            train (pd.DataFrame):
                columns: dates*bands
                rows: time series values for one class

                Contains the found characteristic time series values
                for each class. This can directly be fed to sklearn.
    """

    class_ids = np.unique(dataset['class'])
    band_names = [column_name for column_name in
                  np.unique(dataset.columns.get_level_values('Band')) if
                  column_name != '']

    # Build the average values for each timestep for each class
    all_patterns_per_class = get_characteristic_timeseries_per_class(
        dataset, number_of_patterns_per_class)

    # Uses the mean values per class to create training patterns per class.
    training_patterns = create_training_patterns(
        all_patterns_per_class,
        band_names,
        class_ids,
        number_of_patterns_per_class,
        out_dir
    )
    return training_patterns
