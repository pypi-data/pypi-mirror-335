"Training module for classifier"
import logging
import dataclasses
from pathlib import Path
from typing import Any, List, Tuple, Dict

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

from classifier import __version__ as classifier_version
from classifier.models import random_optimise
from classifier.utils.general import dict_product
from classifier.settings import ALGORITHM_DICT
from classifier.samples import Samples
from classifier.utils.config import Configuration
from classifier.utils.general import get_available_model_args

TRAIN_LOGGER = logging.getLogger(__name__)


def train_kmeans(train_array: np.ndarray, config: Configuration) -> dict:
    """Train the kmeans model

        Args:
            train_array (array): A data array with columns (bands) and rows (
            pixels)
            config (Configuration): contains config

        Returns:
            (dict): A dictionary conaining the algorithm name, the trained model
            and an empty label key to match the dicts from the supervised
            classifications
    """
    algorithm = ALGORITHM_DICT[config.app.algorithm]
    n_classes = config.unsupervised.nclasses

    TRAIN_LOGGER.info(
        "Now Training Model. This might take some time...")

    kmeans = algorithm(n_clusters=n_classes)
    kmeans.fit(train_array)
    return {
        'app_algorithm': config.app.algorithm,
        'model': kmeans,
        'labels': None
    }


def train_dataset(samples: Samples, out_dir: Path,
                  config: Configuration) -> Tuple[dict, np.ndarray]:
    """Train the model using a dataset

    Args:
        samples (Samples): Dataset containing features in the columns
            with one column named "class" which contains class labels or numbers
        out_dir (Path): Path where to write dataset file
        config (Configuration): contains config

    Returns:
        model_dict (dict): A dictionary containing the name, model and label
                        encoder.
        test (np.ndarray): A test dataset which was not used during training
    """
    # Split the dataset,
    model, xcols, test, labels = init_model_and_train(
        samples.get_samples(),
        out_dir,
        config,
    )

    model_dict = {'app_algorithm': config.app.algorithm,
                  'model': model,
                  'labels': labels,
                  'names': xcols,
                  'version': classifier_version}
    return model_dict, test


def init_model(algorithm: str, algorithm_args: dict) -> Any:
    """ Set the model parameters

    Args:
        algorithm (str): internal name of the algorithm (model)
        algorithm_args (dict): Algorithm arguments

    Returns:
        model (Any): parametrized model
    """
    model = ALGORITHM_DICT[algorithm]
    if 'optimization_parameters' in algorithm_args:
        del algorithm_args['optimization_parameters']
    available_args = get_available_model_args(algorithm_args, model())

    ignored_args = set(algorithm_args.keys()) - set(available_args.keys())
    if ignored_args:
        TRAIN_LOGGER.info(
            "Ignored args in model init: %s", ignored_args)
    return model(**available_args)


def get_algorithm_args(
        config: Configuration, dataset: pd.DataFrame, out_dir: Path) -> dict:
    """Fills the algorithm arg dict for the chosen algorithm

    Args:
        config (Configuration): Contains Configuration including algorithm
            name and some parameters
        dataset (pd.Dataframe): Dataset
        out_dir (Path): output directory

    Returns:
        algorithm_args (dict): Contains specific model keyword and arguments
            for the model initialization
    """
    algorithm_name = config.app.algorithm
    algorithm_args = {}

    if algorithm_name == 'randomforest':
        # Random forest
        algorithm_args = dataclasses.asdict(config.randomforest)
    elif algorithm_name == 'xgboost' and len(dataset['class'].unique()) < 3:
        algorithm_args = dataclasses.asdict(config.randomforest)
        algorithm_args['objective'] = 'binary:logistic'
    elif config.app.rasters_are_timeseries:
        # Get raster count and band count
        raster_count = len(dataset.columns.get_level_values(0).unique())-2
        band_count = len(dataset.columns.get_level_values(1).unique())-1
        fit_params = {'raster_count': raster_count, 'band_count': band_count}

        if algorithm_name == "knn_dtw":
            # KNN
            algorithm_args['fit_params'] = fit_params
            metric_params = {
                'window': config.dtw.window,
                'max_dist': config.dtw.max_dist,
                'use_pruning': config.dtw.use_pruning,
                'penalty': config.dtw.penalty}

            # Dtw function (metric function needs both)
            algorithm_args['metric_params'] = {**fit_params,
                                               **metric_params
                                               }
            algorithm_args['n_neighbors'] = config.dtw.n_neighbors
            algorithm_args['number_of_patterns_per_class'] = \
                config.dtw.number_of_patterns_per_class
            algorithm_args['out_dir'] = out_dir
            algorithm_args['patterns_path'] = config.dtw.patterns
            algorithm_args['patterns_save'] = config.dtw.patterns_save
    algorithm_args['n_jobs'] = config.app.threads
    return algorithm_args


def optimize_model(
        model: Any,
        x_train: pd.DataFrame,
        y_train: pd.DataFrame,
        out_dir: Path,
        config: Configuration) -> Any:
    """_summary_

    Args:
        model (sklearn.model): A sklearn model
        x_train (pd.DataFrame): Train data (in case of dtw also with
            class and roi_fid column)
        y_train (pd.DataFrame): class
        out_dir (Path): output path
        config (Configuration): Configuration

    Returns:
        optimized_model (Sklearn.Model): Model with the optimized
            parameters
    """
    optimize_iters = config.supervised.optimization.optimize_number

    if config.app.algorithm == 'knn_dtw':
        # Get the user provided optimization parameters
        # # from the config
        params_from_config = dataclasses.asdict(
            config.dtw)['optimization_parameters']

        # Get the transform parameters for the reshape
        fit_params = model['transformer'].get_params()[
            'fit_params']

        # These two parameters are only influencing the performance
        use_pruning = config.dtw.use_pruning
        max_dist = config.dtw.max_dist

        # The optimization parameter combinations have to
        # be put in a list by hand
        # as sklearn struggles with metric_params unpacking
        optimization_parameters = []

        # Build all combinations of the provided optimization
        # parameters
        for comb in dict_product(params_from_config):
            # Only add combination if there are more or
            # equal patterns to neighbors
            if comb['n_neighbors'] <= comb['number_of_patterns_per_class']:
                # Add to optimization parameters
                optimization_parameters.append(
                    {
                        'n_neighbors': [comb['n_neighbors']],
                        'number_of_patterns_per_class':
                        [comb['number_of_patterns_per_class']],
                        'metric_params': [
                            {**fit_params,
                             'window': comb['window'],
                             'penalty': comb['penalty'],
                             'use_pruning': use_pruning,
                             'max_dist': max_dist
                             }],
                        'fit_params': [fit_params]
                    }
                )
    else:
        optimization_parameters = dataclasses.asdict(
            config.randomforest)['optimization_parameters']
    optimized_params = random_optimise(
        model,
        optimization_parameters,
        x_train,
        y_train,
        out_dir,
        optimize_iters
    )

    if config.app.algorithm == 'knn_dtw':
        optimized_params['out_dir'] = out_dir
    if config.dtw.patterns:
        optimized_params['pattern_path'] = config.dtw.patterns
    if config.dtw.patterns_save:
        optimized_params['patterns_save'] = config.dtw.patterns_save

    model.set_params(**optimized_params)
    return model


def init_model_and_train(
        dataset: pd.DataFrame,
        out_dir: Path,
        config: Configuration
    ) -> Tuple[Any, List[str], pd.DataFrame, Dict[str, str]]:
    """Set the model parameters and train it

    Args:
        dataset (Array) : The dataset for input in the model (array)
        out_dir (Path): The output directory
        config (Configuration): Contains config

    Returns:
        model (Any): Trained sklearn model
        xcols (List[str]): Names of bands
        test (pd.DataFrame): Test dataset
        labels (Dict[str, str]): labels mapped to ascending integers
    """
    optimize = config.supervised.optimization.optimize
    test_size = config.accuracy.testfraction
    algorithm_args = {}

    train, test = train_test_split(dataset, test_size=test_size)
    xcols = [x for x in train.columns
             if 'class' not in x and 'roi_fid' not in x]
    if config.app.algorithm == 'knn_dtw':
        # keep class and roi_fid column for knn_dtw training
        x_train = train
    else:
        x_train = train[xcols]
    y_train = train['class']

    # encode the labels
    label_encoder = LabelEncoder()
    y_train_encoded = label_encoder.fit_transform(y_train)
    labels_encoded = zip(label_encoder.transform(label_encoder.classes_), label_encoder.classes_)
    labels = {str(k): str(v) for k, v in labels_encoded}

    # Get the model/algorithm arguments
    algorithm_args = get_algorithm_args(config, dataset, out_dir)

    # Create the model with the given params
    model = init_model(config.app.algorithm, algorithm_args)

    # Optimize model
    if optimize:
        model = optimize_model(
            model, x_train, y_train_encoded, out_dir, config)

    # y_train_encoded = sample_labels_encoder.transform(y_train)
    TRAIN_LOGGER.info("Train model ...")
    # Use array repr (x_train.values) to make sure feature names are not used.
    # Except when we use KNN DTW, because that needs the band names.
    if not config.app.algorithm == 'knn_dtw':
        x_train = x_train.values

    model.fit(x_train, y_train_encoded)
    TRAIN_LOGGER.info("Model trained.")
    return model, xcols, test, labels
