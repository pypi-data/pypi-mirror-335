"Samples class with child Timeseries class"
# pylint: disable=too-many-positional-arguments
import datetime
import logging
import os
import sys
from pathlib import Path
from typing import Any, List, Optional, Union, Dict

import fiona
import numpy as np
import pandas as pd
import rasterio
from rasterio.windows import Window
from sklearn.ensemble import IsolationForest
from sklearn.impute import SimpleImputer

from classifier.dataprep import class_counts
from classifier.settings import US_ALGORITHMS
from classifier.utils.config import (Configuration,
                                     SubsampleSupervisedConfiguration)
from classifier.utils.general import parallel_function, rois_in_raster_extent
from classifier.utils.raster import (count_bands, get_bandnames, get_meta,
                                     get_raster_date, clip_raster_on_geometry,
                                     verify_and_count_bands)

SAMPLES_LOGGER = logging.getLogger(__name__)


class Samples():
    """
    Class that holds all the samples related data

    Attributes
    ----------
    rasters : List[Path]
        raster paths
    rois : List[dict]
        contains the rois each consisting of one dict respectively
    out_dir : Path
        main output directory for result files and co.
    samples : pd.DataFrame
        contains the sampled data

    """

    def __init__(self,
                 rasters: List[Path],
                 rois: Union[Dict[str, object],
                             Optional[Path]],
                 out_dir: Path) -> None:

        self.rasters: List[Path] = rasters
        self.rois: List[dict] = None

        if rois is not None:
            self.rois = []
            if isinstance(rois, dict):
                # prediction
                self.rois.append(rois)
            else:
                # training
                with fiona.open(rois, "r") as shapefile:
                    # unpack the rois from shapefile in list
                    for roi in shapefile:
                        self.rois.append(roi)
        self.out_dir = out_dir
        self.samples: Optional[pd.DataFrame] = None

        if rasters is not None and rois is not None:
            self.check_geo_input_data(self.rasters, self.rois)

    @staticmethod
    def read_samples(samples_file: Path) -> Any:
        """Read a samples file.

        Args:
            samples_file (Path): CSV or Pickle file containing samples

        Returns:
            sample_df (pd.DataFrame): DF containing samples

        """
        SAMPLES_LOGGER.info("Read samples from file...")
        if samples_file.suffix == '.pkl':
            return pd.read_pickle(samples_file)
        if samples_file.suffix == '.csv':
            return pd.read_csv(samples_file, index_col=0)
        SAMPLES_LOGGER.error(
            "Unknown samples file type")
        return None

    def write_samples(self, file_type: str = 'csv') -> None:
        """Write samples to pickle or csv

        Args:
            file_type (str): File type: csv or pkl

        Returns:
            None

        """
        SAMPLES_LOGGER.info("Save samples to file.")
        if self.samples is not None:
            if file_type == 'csv':
                self.samples.to_csv(
                    os.path.join(self.out_dir, 'samples.csv')
                )
            elif file_type == 'pkl':
                self.samples.to_pickle(
                    os.path.join(self.out_dir, 'samples.pkl')
                )
            else:
                SAMPLES_LOGGER.info(
                    "Unknown file type. Choose csv or pkl")
        else:
            SAMPLES_LOGGER.info(
                "No Samples collected yet.")

    def get_samples(self, only_raster_data: bool = False) -> pd.DataFrame:
        """Returns the samples. If only raster_data true, return only the
        raster values and no class/roi_fid

        Args:
            only_raster_data (bool, optional): Exclude class and roi_fid column
            from returned dataframe

        Returns:
            pd.DataFrame: samples dataframe
        """
        if only_raster_data:
            return self.samples.loc[
                :, ~self.samples.columns.get_level_values(0).isin(
                    ['class', 'roi_fid'])]
        return self.samples

    def get_labels(self) -> pd.Series:
        """Return only the labels

        Returns:
            pd.Series: contains class labels
        """
        if self.samples is not None:
            return self.samples['class']
        return None

    def gather_samples(self,
                       config: Configuration,
                       for_prediction: bool = False) -> None:
        """Gets the samples

        Either from a provided sample file or it will collect the samples
        from provided rasters and rois

        Args:
            config (Configuration): contains config
            for_prediction (bool): Do not read samples from file
                or save samples to file if for_prediction

        Returns:
            None
        """
        # Gather samples
        if config.app.samples is not None and not for_prediction:
            # samples file provided
            self.samples = self.read_samples(
                config.app.samples)
        elif self.rois is not None:
            # gather samples from rasters and rois
            self.samples = self.create_samples(
                self.rasters,
                self.rois,
                config,
                for_prediction)
            if self.out_dir is not None and not for_prediction:
                self.write_samples()
        elif config.app.algorithm in US_ALGORITHMS:
            self.samples = self.create_samples_for_unsupervised(
                self.rasters, config)
        else:
            self.samples = None

    def create_samples(
            self, rasters: List[Path],
            rois: List[dict], config: Configuration,
            for_prediction: bool) -> pd.DataFrame:
        """Create the entire dataset based on rasters and rois

        Args:
            rasters (List[Path]): list of raster file names
            rois (List[Dict]): Contains each roi as a single dict
            config (Configuration): contains config
            for_prediction (bool): changes imputation/samples deleting behaviour

        Returns:
            samples (pd.DataFrame): dataset with samples
        """

        # Gather the samples and return a full df of all samples
        bandnames = get_bandnames(rasters)
        samples = self.gather_samples_from_data(rasters,
                                                rois,
                                                bandnames,
                                                None,
                                                config,
                                                for_prediction
                                                )
        return samples

    def fill_missing_data(
            self, samples: pd.DataFrame, config: Configuration,
            for_prediction: bool = False) -> pd.DataFrame:
        """ Handles the data holes by transforming infinity values to nan and
        then either filling all nan values with the chosen imputation method
        or deleting them.

        Args:
            samples (pd.DataFrame): contains the samples
            config (Configuration): Configuration
            for_prediction (bool): if its for prediction, do not drop NaNs

        Returns:
            samples (pd.DataFrame): dataframe with handled holes
        """

        # Check for numeric values
        samples, contains_nans = self.check_data(samples)

        # Imputation
        if contains_nans and config.app.rasters_are_timeseries:
            # If time series, impute through time
            return self.impute_ts(samples)
        if contains_nans and config.app.imputation:
            return self.impute(samples, config)
        if contains_nans and not for_prediction:
            # delete empty samples
            SAMPLES_LOGGER.warning("""The sampled dataset contains nan's.
            Imputation is set to False so all rows containing NaNs will be
            deleted. If you want to prevent this from happening, please set the
            app_imputation parameter to True and choose a strategy and constant
            if necessary.""")
            return samples.dropna(how='any')
        return samples

    def impute(self, samples: pd.DataFrame,
               config: Configuration) -> pd.DataFrame:
        """Impute a single raster

        Args:
            samples (pd.DataFrame): dataframe with samples
            config (Configuration): Configuration dataclass

        Returns:
            pd.DataFrame: imputed samples dataframe
        """
        if config.app.imputation_strategy == 'interpolate':
            data_filled_df = samples.interpolate(
                method="linear", axis=0, limit_direction="both")
        else:
            # Other imputation methods
            # Check if a feature column is None => will get deleted by
            # sklearn imputer (cant get imputed)
            if samples.isnull().all().any():
                SAMPLES_LOGGER.warning(
                    "%s Features have no values, cant be imputed.",
                    samples.isnull().all().sum())
                return samples
            data_filled = self.impute_values(samples, config)
            data_filled_df = pd.DataFrame(
                data_filled, index=samples.index, columns=samples.columns)
        return data_filled_df

    @staticmethod
    def check_data(dataset: pd.DataFrame) -> Union[pd.DataFrame, bool]:
        """Checks data for invalid values like np.inf and np.nan

        Args:
            dataset (pd.DataFrame): samples dataframe

        Returns:
            Union[pd.DataFrame, bool]: samples dataframe and if it
                contains nan values
        """
        # Replaced infinity values
        dataset = dataset.replace([np.inf, -np.inf], np.nan)

        # Check for nans
        contains_nans = dataset.isnull().values.any()
        return dataset, contains_nans

    def gather_samples_from_data(
            self,
            rasters: List[Path],
            rois: List[dict],
            bands: List[str],
            dates: List[datetime.datetime],
            config: Configuration,
            for_prediction: bool = False) -> pd.DataFrame:
        """Gathers the pixel values for all the rasters and
        combines them in a df

        The DataFrame is a multiColumn dataframe where
        column level 0 is the class

            Args:
                rasters (List[Path]): containg raster paths
                rois (List[dict]): containing the roi geometry dictionaries
                bands (List[str]): Contains band names
                dates (List[datetime.datetime]): Contains dates
                config (Configuration): contains config
                for_prediction (bool): Doesn't delete samples if
                    for prediction

            returns:
                samples_df (pd.DataFrame): DataFrame with of samples
        """

        # Parallel gathering of samples from the rois and rasters
        kwargs = []
        if rois is not None:
            kwargs = [
                {
                    'roi': roi,
                    'rasters': rasters,
                    'config': config,
                    'dates': dates,
                    'bands': bands,
                    'for_prediction': for_prediction
                }
                for roi in rois
            ]
        if for_prediction:
            gathered_samples_list = []
            for roi in kwargs:
                gathered_samples_list.append(
                    self._gather_samples_per_roi(**roi)  # type: ignore
                )
        else:
            gathered_samples_list = parallel_function(
                self._gather_samples_per_roi,
                kwargs,
                ncpus=config.app.threads
            )
        if gathered_samples_list:
            # Concat results from all the rois
            samples_df = pd.concat(gathered_samples_list, axis=0)
        else:
            SAMPLES_LOGGER.error(
                "Couldn't collect any samples from any roi."
                "Check your rois or rasters."
            )
            sys.exit(1)

        # make class column instead of index
        samples_df.reset_index(level='class', inplace=True)

        if not for_prediction:
            # Subsample the data
            if config.supervised.subsample.active:
                samples_df = Samples.subsample(
                    samples_df, config.supervised.subsample
                )

            # Remove outliers (right now only for non timeseries)
            if config.supervised.remove_outliers \
                    and not config.app.rasters_are_timeseries:
                samples_df = self.outlier_removal(
                    samples_df, config)

        # make roi_fid a column instead of index
        samples_df.reset_index(level='roi_fid', inplace=True)

        # Reindex samples id
        samples_df.reset_index(inplace=True, drop=True)

        return samples_df

    def _gather_samples_per_roi(
            self, roi: dict,
            rasters: List[Path],
            config: Configuration,
            dates: List[datetime.datetime],
            bands: List[str],
            for_prediction: bool) -> Union[None, pd.DataFrame]:
        """Gather samples for a roi, for usage in MP function
        Creates a dataframe with rows=sample and columns=bands

            Args:
                roi (dict shapely.geometry): region of interest
                rasters (List[Path]): raster list
                config (dataclass): contains config
                df_index (list): index to use for creation of samples df
                bands (list): bands to use from the tifs
                for_prediction (bool): changes samples imputing/deleting
                    behaviour
        """
        # Gather all the samples for this roi from all rasters
        roi_samples = self._gather_samples_for_roi(
            roi,
            rasters,
        )
        if roi_samples is not None:

            # Samples count for roi
            sample_count = roi_samples.shape[0]

            # Extract roi id (class)
            roi_class = int(roi['properties']['id'])
            roi_classes = sample_count * [roi_class]

            # Extract fid (unique id of each roi)
            roi_fid = int(roi['id'])
            roi_fids = sample_count * [roi_fid]

            # Sample number
            sample_id = np.arange(sample_count)

            # Column Index
            if dates:
                # Save also date if it's a timeseries
                columns = pd.MultiIndex.from_product(
                    [dates, bands],
                    names=['Date', 'Band']
                )
            else:
                columns = bands

            # Row Index
            index = pd.MultiIndex.from_tuples(
                list(zip(roi_classes, roi_fids, sample_id)),
                names=['class', 'roi_fid', 'pixel']
            )

            # Samples DataFrame for roi
            # Shape: rows=samples, columns=dates(if timeseries) * bands
            roi_samples_df = pd.DataFrame(
                roi_samples,
                index=index,
                columns=columns)

            # Handle invalid data
            roi_samples_df = self.fill_missing_data(
                roi_samples_df,
                config,
                for_prediction)

            if roi_samples_df.empty:
                return None

            # Samples which still have data gaps after imputation, are deleted
            # if its for training (not deleted for prediction, will get masked
            # out later)
            if not for_prediction:
                if roi_samples_df.isnull().any(axis=1).any():
                    # Sample seems to have no values for
                    # a given band for any raster timestep
                    SAMPLES_LOGGER.warning(
                        "Deleting samples from roi %s. "
                        "Could not find any values for them. ", roi_fid)
                    roi_samples_df = roi_samples_df.dropna()
            return roi_samples_df
        return None

    @staticmethod
    def _gather_samples_for_roi(roi: dict, rasters: List[Path]) -> np.ndarray:
        """Get sample values from rasters warped to
        the specified warp destination

            Args:
                roi (fiona shape): region of interest
                rasters (List[Path]): list of raster file names

            Returns:
                np.array [nsamples, nfeatures] of samples from within rois.
        """

        try:
            roi_values_list = []
            for files in rasters:
                samples_per_raster = clip_raster_on_geometry(
                    files,
                    roi['geometry']
                )
                roi_values_list.append(samples_per_raster)
            # Concatenate the roi values from all rasters along rows.
            # Then transpose. Shape: rows=samples, columns=bands*timesteps
            roi_values = np.concatenate(roi_values_list, axis=0).T
        except ValueError:
            SAMPLES_LOGGER.debug("ROI %s OUT OF BOUNDS.. Continuing without "
                                 "it", roi['geometry']['coordinates'][0][0])
            roi_values = None
        return roi_values

    @staticmethod
    def impute_values(
            dataset: pd.DataFrame, config: Configuration) -> np.ndarray:
        """Impute values

        Uses the sklearn SimpleImputer to impute missing values.

        Args:
            dataset (pd.DataFrame): DataFrame containing Nans
            config (Configuration): Parameters to use for imputation

        Returns:
            dataset (np.ndarray): DataFrame with Nans imputed
        """

        # sklearn Imputer
        imputer = SimpleImputer(strategy=config.app.imputation_strategy,
                                fill_value=config.app.imputation_constant)
        # imputer expects ndarray
        return imputer.fit_transform(dataset.values)

    @staticmethod
    def outlier_removal(samples: pd.DataFrame,
                        config: Configuration) -> pd.DataFrame:
        """Outlier removal from samples using Isolation Forest

        Args:
            samples (pd.DataFrame): samples with possible outliers
            config (Configuration): Parameters to use for imputation

        Returns:
            samples (pd.DataFrame): samples with filtered outliers
        """
        SAMPLES_LOGGER.info("Now checking for outliers")
        cols = [x for x in samples.columns if x != 'class']
        if_model = IsolationForest(
            contamination='auto', n_jobs=config.app.threads)

        samples['inlier'] = 0
        lulc_classes = samples['class'].unique()

        for lulc_class in lulc_classes:
            samples.loc[samples['class'] == lulc_class, 'inlier'] = \
                if_model.fit_predict(samples[samples['class'] == lulc_class][
                    cols])

        # get the number of removed pixels and give output
        class_counts(samples)
        cols_to_return = [x for x in samples.columns if not x == 'inlier']
        return samples[samples['inlier'] > 0][cols_to_return]

    def create_samples_for_unsupervised(self, rasters: List[Path],
                                        config: Configuration) -> np.ndarray:
        """Create an input array for unsupervised classification

        Function for creating the input array for the training of the
        unsupervised models. A train_size relative to the entire dataset can be
        set to reduce the amount of memory needed

        Args:
            rasters (List[Path]): Input rasters
            config (Configuration): Contains config

        Returns:
            data_array (np.ndarray): A data array to use in model training"""

        SAMPLES_LOGGER.info(
            "Gathering random samples from rasters for "
            "unsupervised classification")
        windows, _ = get_meta(rasters, config.app.window)

        # create_rois_for_us(windows, config)

        subset_windows = np.random.choice(
            np.array(windows)[:, 1],
            size=int(len(windows) * config.unsupervised.trainfraction),
            replace=False)
        n_windows = len(subset_windows)
        if n_windows == 0:
            SAMPLES_LOGGER.error(
                "Not enough subset data."
                "Please increase -us_train_size parameter"
            )
            sys.exit(1)
        SAMPLES_LOGGER.info("\nUsing %i windows for training", n_windows)

        kwargs = [{
            'rasters': rasters,
            'window': window
        } for window in subset_windows]

        gathered_us_data = parallel_function(
            self.get_window_data_for_us_train,
            kwargs,
            ncpus=config.app.threads
        )

        data_array = np.concatenate(gathered_us_data, axis=0)

        dataset = pd.DataFrame(data_array)

        dataset = self.fill_missing_data(dataset, config)
        SAMPLES_LOGGER.info("\nCollected data from windows")
        return dataset

    @staticmethod
    def get_window_data_for_us_train(
            rasters: List[Path],
            window: Window) -> np.ndarray:
        """Gets the pixel values for window and adds it to an MP list

        Args:
            rasters (List[Path]): List of rasters to get data from
            window (rasterio.Window): Window to process

        """
        data_values = []
        # Create a vrt with the window and add the data to the array
        for raster in rasters:
            with rasterio.open(raster, 'r') as src:
                data_values.append(src.read(window=window))
        old_shape = np.shape(data_values)  # (1, channels, x, y)
        data_array = np.reshape(
            data_values,
            (old_shape[0] * old_shape[1],
             old_shape[2] * old_shape[3])).transpose()
        return data_array

    @staticmethod
    def check_geo_input_data(
            rasters: List[Path], rois: List[dict]) -> bool:
        """Check if all the rois are inside the rasters extent

        Args:
            rasters (List[Path]): Raster Paths
            rois (List[dict]): List of roi dict

        Returns:
            bool: True if all rois lie inside the rasters extent
        """

        # only do this for training (more than 1 rois) as windows for
        # prediction sometimes lie partially outside
        if rois is not None and len(rois) > 1:
            rois_lie_inside_rasters = rois_in_raster_extent(
                rasters, rois)
            return rois_lie_inside_rasters
        return True

    @staticmethod
    def subsample(
        samples: pd.DataFrame,
        config_subsampling: SubsampleSupervisedConfiguration,
        ) -> pd.DataFrame:
        """Subsampling

        Args:
            samples (pd.DataFrame): samples
            config (SubsampleSupervisedConfiguration): 
                Parameters to use for subsampling

        Returns:
            samples (pd.DataFrame): subsampled samples 
        """
        group_by = config_subsampling.group_by
        sample_type = config_subsampling.sample_type
        amount = config_subsampling.amount
        replace = config_subsampling.replace

        SAMPLES_LOGGER.info(
            "Do subsampling based on %s with %s: %s, replace: %s",
            group_by, sample_type, amount, replace)

        SAMPLES_LOGGER.info("Total size before subsampling: %s",
                            len(samples))
        samples = samples.groupby(by=group_by).sample(
            **{sample_type: amount, 'replace': replace}, random_state=0)
        SAMPLES_LOGGER.info("Total size after subsampling: %s",
                            len(samples))
        return samples


class TimeSeries(Samples):
    """Class for Timeseries samples, subclass of Sample

    Overwrites some methods of Sample which need to be
    adjusted for time series
    """

    def __init__(self,
                 rasters: List[Path],
                 rois: Union[Dict[str, object],
                             Optional[Path]],
                 out_dir: Path) -> None:
        super().__init__(rasters, rois, out_dir)

        if rasters is not None:
            self.check_geo_input_data_ts(self.rasters)

    @ staticmethod
    def read_samples(samples_file: Path) -> pd.DataFrame:
        """Read a timeseries samples file.

        Args:
            samples(path): file containing samples

        Returns:
            sample_df(pd.DataFrame): Contains samples

        """
        if samples_file.suffix == ".pkl":
            SAMPLES_LOGGER.info("Load Pickle sample dataset\n")
            return pd.read_pickle(samples_file)
        SAMPLES_LOGGER.error(
            "\nFile format of sample file not supported.\n"
            "Supported samples files are Pickle: *.pkl")
        return None

    def write_samples(self, file_type: str = 'pkl') -> None:
        """Write samples to pickle or csv

        Args:
            file_type (str): File type: csv or pkl

        Returns:
            None

        """
        SAMPLES_LOGGER.info("Save Samples as Pickle...")
        if self.samples is not None:
            if file_type == 'pkl':
                self.samples.to_pickle(
                    os.path.join(self.out_dir, 'samples_ts.pkl')
                )
            else:
                SAMPLES_LOGGER.info(
                    "Other save file format currently not supported")
        else:
            SAMPLES_LOGGER.info(
                "No Samples collected yet.")

    def gather_samples(
            self, config: Configuration, for_prediction: bool = False) -> None:
        """Samples for time series from a list of rasters and a polygon file

            Args:
                config (Configuration): contains config
                for_prediction (bool): Do not read samples from file
                or save samples to file if for_prediction

            Returns:
                None
        """
        # Gather samples
        if config.app.samples is not None and not for_prediction:
            # samples file provided
            self.samples = self.read_samples(
                config.app.samples)
        elif self.rois is not None:
            # gather samples from rasters and rois
            self.samples = self.create_samples(
                self.rasters,
                self.rois,
                config,
                for_prediction)
            if self.out_dir is not None and not for_prediction:
                self.write_samples()
        elif config.app.algorithm in US_ALGORITHMS:
            SAMPLES_LOGGER.info("not implemented yet")
            sys.exit(1)
        else:
            self.samples = None

    def create_samples(self,
                       rasters: List[Path],
                       rois: List[dict],
                       config: Configuration,
                       for_prediction: bool) -> pd.DataFrame:
        """Create the entire dataset based on rasters and rois

        Args:
            rasters (List[Path]): list of raster file names
            rois (List[Dict]): contains each roi as a single dict
            config (Configuration): contains config
            for_prediction (bool): changes imputation/samples deleting behaviour

        Returns:
            samples (pd.DataFrame): dataset with samples
        """

        # Extract raster dates from file names
        raster_dates = [get_raster_date(raster) for raster in rasters]
        dates = [datetime.datetime.strptime(
            x, "%Y-%m-%d") for x in raster_dates]

        # Count bands and create new band names
        b_count = count_bands(rasters[0])
        bands = [f'B{str(x).zfill(2)}' for x in np.arange(1, b_count + 1)]

        samples = self.gather_samples_from_data(
            rasters, rois, bands, dates, config, for_prediction)
        return samples

    @ staticmethod
    def impute_ts(samples_df: pd.DataFrame) -> pd.DataFrame:
        """Imputation of timeseries
           Imputes values through time.

            Args:
                samples_df (pd.DataFrame): Dataframe with timeseries samples

            Returns:
                samples_filled_df (pd.DataFrame): Imputed DataFrame
        """

        # Shape after: rows:dates(time)   columns: class, roi_fid, pixel
        samples_df_time_as_index = samples_df.T.unstack()

        # Interpolate through time
        samples_df_filled = samples_df_time_as_index.interpolate(
            method="time", axis=0, limit_direction="both")

        # if there are still NaNs, there were not enough values to interpolate
        if samples_df_filled.isnull().values.any():
            samples_df_filled = samples_df_filled.fillna(
                method="ffill", axis=0).fillna(
                    method="bfill", axis=0)

        # Convert back to old shape
        samples_df_filled = samples_df_filled.T.unstack()

        return samples_df_filled

    @ staticmethod
    def check_geo_input_data_ts(rasters: List[Path]) -> None:
        """Check the rasters and rois input data

        Args:
            rasters (List[Path]): Raster paths
        """

        # check if the timeseries rasters have same amount of bands
        _ = verify_and_count_bands(rasters)
