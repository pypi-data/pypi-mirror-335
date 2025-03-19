"""An sk-learn classifier for landcover classification"""

import logging
import sys
import time
from pathlib import Path
from typing import List, Optional

from classifier.accuracy import (plot_feature_importances,
                                 write_confusion_matrix)
from classifier.predict import prediction
from classifier.settings import US_ALGORITHMS
from classifier.train import train_dataset, train_kmeans
from classifier.utils.config import Configuration
from classifier.utils.general import parallel_function, read_model, save_model
from classifier.utils.raster import get_meta, stitch
from classifier.samples import Samples, TimeSeries
from classifier.utils.vector import get_rois_extent


START = time.time()
CLASSIFIER_LOGGER = logging.getLogger(__name__)


def train(samples: Samples, out_dir: Path, config: Configuration,
          rois_extent: Optional[List[float]] = None) -> dict:
    """Train a model using samples and rasters

    Args:
        samples (Samples): Samples dataframe containing pixel
            values and class values
        rasters (List[Path]): A list of raster files
        out_dir (Path): Path where to write the dataset file
        config (Configuration): contains config
        rois_extent (List[float]): The extent of the training data

    Returns:
        model_dict (dict): Containing the name, model and label
                           encoder.
    """
    CLASSIFIER_LOGGER.info("\n####-----Training----#####\n")
    #windows, _ = get_meta(rasters, config.app.window)
    if config.app.algorithm in US_ALGORITHMS:
        # Do unsupervised
        array = samples.get_samples()
        model_dict = train_kmeans(array,
                                  config)
    else:  # All supervised methods
        model_dict, test = train_dataset(
            samples,
            out_dir,
            config
        )
        if config.app.algorithm in ['randomforest', 'xgboost'] \
                and config.accuracy.perform_assesment:
            # Do the accuracy analysis
            write_confusion_matrix(model_dict, test, out_dir)
            plot_feature_importances(model_dict, out_dir)
    # save the model as a python pickle
    if not rois_extent is None:
        model_dict['rois_bounds'] = rois_extent
    if config.app.model_save:
        save_model(model_dict, out_dir, config)
    CLASSIFIER_LOGGER.info("\nFinished Training\n")
    return model_dict


def predict(
        model_dict: dict, rasters: List[Path],
        out_dir: Path, config: Configuration) -> None:
    """Prediction function using a trained model and raster files

    Args:
        model_dict (dict): Containing the name, model and label
                        encoder.
        rasters (List[Path]): A list of raster files
        out_dir (Path): Path where to write the dataset file
        config (Configuration): contains config
    """
    threads = config.app.threads
    CLASSIFIER_LOGGER.info("\n####-----Prediction----#####\n")
    windows, meta = get_meta(rasters, config.app.window)

    # Set model n_jobs to 1 for prediction
    if 'n_jobs' in model_dict['model'].get_params():
        model_dict['model'] = \
            model_dict['model'].set_params(**{'n_jobs': 1})

    iterable = [
        {
            'window': window[1],
            'rasters': rasters,
            'model_dict': model_dict,
            'meta': meta,
            'config': config
        }
        for window in windows
    ]
    if threads > 1 or threads == -1:
        parallel_function(prediction,
                          iterable,
                          threads)
    else:
        for wins in iterable:
            prediction(**wins)

    # ##--------------------STITCHING-----------------------------------###

    CLASSIFIER_LOGGER.info("\n####-----Stitching----#####\n")

    # Run the gdalwarp command in the command line
    stitch(out_dir, meta, config)
    CLASSIFIER_LOGGER.info("Cleaning up..")
    config.tmp_dir.cleanup()
    CLASSIFIER_LOGGER.info(
        "Total run time was %i seconds", (int(time.time() - START)))


def check_input_choices(
        config: Configuration, rois: Optional[Path] = None) -> None:
    """Checks if the chosen options and provided data match

    Args:
        rasters (List[Path]): A list of raster files
        config (Configuration): contains config
        rois (Path): The path to a rois file

    Returns:
        None
    """

    # If rois and samples are None, only unsupervised is possible
    if rois is None and config.app.samples is None:
        if config.app.algorithm not in US_ALGORITHMS:
            CLASSIFIER_LOGGER.error(
                "You have chosen a supervised classification method but didn't "
                "provide rois or samples. Either provide one of these or run "
                "an unsupervised classification.")
            sys.exit(1)

    if rois is not None and config.app.samples is not None:
        CLASSIFIER_LOGGER.error(
            "You provided rois and samples but not both can be used. "
            "Only provide one of them.")
        sys.exit(1)

    if rois is not None or config.app.samples is not None:
        if config.app.algorithm in US_ALGORITHMS:
            CLASSIFIER_LOGGER.error(
                "You have chosen an unsupervised classification "
                "method but provided samples or rois. Please choose "
                "a supervised method to use them or don't provide them for "
                "an unsupervised classification.")
            sys.exit(1)


def classify_(
        rasters: List[Path], config: Configuration,
        out_dir: Path, rois: Optional[Path] = None) -> None:
    """Entry point function for pixel-based classification

        Args:
            rasters (List[Path]): A list of raster files
            config (Configuration): contains config
            out_dir (Path): Path where to write the dataset file
            rois (Path): The path to a rois file

    """

    CLASSIFIER_LOGGER.info("Starting Classification...")
    if config.app.model is not None:
        CLASSIFIER_LOGGER.info(
            "You provided a model. Remember that this model has to "
            "be already trained and provided rois/samples will "
            "not be used. Only predictions are done."
        )
        # Model provided, only do prediction
        model_dict = read_model(config.app.model)
    else:
        CLASSIFIER_LOGGER.info(
            "No model provided. Train a new one."
        )

        check_input_choices(config, rois)

        # gather samples
        samples = Samples(rasters, rois, out_dir)
        samples.gather_samples(config)

        rois_extent = []
        if rois is not None:
            rois_extent = get_rois_extent(rois)

        # train
        model_dict = train(samples, out_dir,
                           config, rois_extent)

    predict(model_dict, rasters, out_dir, config)


def classify_timeseries(rasters: List[Path],
                        config: Configuration,
                        out_dir: Path,
                        rois: Path) -> None:
    """Main function to classifiy timeseries.

    For now, only from start to finish is supported. ie, supplying a model
    or samples does not work.

        Args:
            rasters (List[Path]): List of raster paths
            config (Configuration): contains config
            out_dir (Path): Path to output directory
            rois (Path): Path to rois file

    """
    CLASSIFIER_LOGGER.info("Timeseries Classification")

    if config.app.algorithm == 'unsupervised':
        CLASSIFIER_LOGGER.error(
            "Unsupervised classification not supported yet")
        sys.exit()

    if config.app.model is not None:
        # Model provided, only do prediction
        model_dict = read_model(config.app.model)
    else:
        # No Model provided
        # gather samples
        timeseries = TimeSeries(rasters, rois, out_dir)
        timeseries.gather_samples(config)

        model_dict = train(timeseries,
                           out_dir,
                           config,
                           rois_extent=None)

    predict(model_dict, rasters, out_dir, config)


if __name__ == "__main__":
    pass
