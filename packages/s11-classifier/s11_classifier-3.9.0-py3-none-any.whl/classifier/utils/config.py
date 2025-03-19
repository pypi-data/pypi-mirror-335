""" Setup and load the configurations """
import json
import logging
import pathlib
import sys
from dataclasses import dataclass
from typing import List, Optional, Any, Dict, Mapping, Union

import dacite
from marshmallow import Schema, ValidationError, fields, validate

UTILS_CONFIG_LOGGER = logging.getLogger(__name__)

LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
IMPUTATION_STRATEGIES = ["mean", "median",
                         "most_frequent", "constant", "interpolate"]
OPTIMIZE_RANDOMFOREST_MAX_FEATURES = ["sqrt", "log2"]
ALGORITHMS = [
    "randomforest", "xgboost", "singleclass", "us_kmeans",
    "us_kmeans_minibatch", "knn_dtw"
]

PARAMETERS = {
    "app": {
        "algorithm": "randomforest",
        "window": 1024,
        "model": None,
        "model_save": False,  # Save a model file which can be re-used
        "samples": None,
        "log_level": "INFO",
        "threads": -1,
        "imputation": True,
        "imputation_strategy": "mean",
        "imputation_constant": -9999,
        "rasters_are_timeseries": False
    },
    "supervised": {
        "probability": True,
        "all_probabilities": False,
        "remove_outliers": True,  # Remove outliers from the training data
        "optimization": {
            "optimize": False,  # Optimize the model parameters
            "optimize_number": 10,  # Number of iterations for optimization
        },
        "subsample": {
            "active": False,
            "group_by": "class",
            "sample_type": "n",
            "amount": 100,
            "replace": False,
        },
    },
    "unsupervised": {
        "nclasses": 2,  # Number of classes for unsupervised
        "trainfraction": 1.0  # Fraction of raster used for training
    },
    "accuracy": {
        "perform_assesment": True,  # Perform accuracy assessment
        "testfraction": 0.25,  # Fraction of data to use for training
    },
    "dtw": {
        "patterns": None,
        "patterns_save": False,
        "number_of_patterns_per_class": 1,
        "n_neighbors": 1,
        "window": None,
        "max_dist": None,
        "use_pruning": False,
        "penalty": None,
        "optimization_parameters": {
            "n_neighbors": [1],
            "number_of_patterns_per_class": [1],
            "window": [None],
            "penalty": [None]
        }
    },
    "randomforest": {
        "n_estimators": 100,
        "criterion": "gini",
        "max_depth": None,
        "min_samples_split": 2,
        "min_samples_leaf": 1,
        "min_weight_fraction_leaf": 0.,
        "max_features": "sqrt",
        "max_leaf_nodes": None,
        "min_impurity_decrease": 0.,
        "bootstrap": True,
        "oob_score": False,
        "random_state": None,
        "verbose": 0,
        "class_weight": None,
        "ccp_alpha": 0.,
        "max_samples": None,
        "optimization_parameters": {
            "max_features": ['sqrt', 'log2'],
            "max_leaf_nodes": [3, 5, 7],
            "max_depth": [None, 1, 3, 10, 20000],
            "n_estimators": [10, 50, 100],
            "min_samples_split": [2],
            "min_samples_leaf": [1],
            "min_weight_fraction_leaf": [0.0],
            "min_impurity_decrease": [0.0],
            "oob_score": [False],
            "class_weight": [None],
            "ccp_alpha": [0.0],
            "max_samples": [None]
        }
    }
}


class PathField(fields.Field):
    """ Field that serializes to a string and deserializes to a pathlib.Path."""

    def _deserialize(
            self, value: Any, attr: Optional[str],
            data: Optional[Mapping[str, Any]],
            **kwargs: dict) -> pathlib.Path:
        if not isinstance(value, str):
            raise ValidationError(
                "Please provide the path as a string (with quotation marks)")
        return pathlib.Path(value)

    def _serialize(self, value: Any, attr: str, obj: Any, **kwargs: dict)\
            -> str:
        if value is None:
            return ""
        return str(value)


class IntFloatField(fields.Field):
    """ Field that accepts int or float and saves it then
    as either int or float."""

    def __init__(self, val_types: Dict[str, fields.Field],
                 allow_none: bool = False,):
        self.valid_types = val_types
        super().__init__(allow_none=allow_none)

    def _deserialize(self, value: Any, attr: Optional[str],
                     data: Optional[Mapping[str, Any]],
                     **kwargs: dict):
        if isinstance(value, int):
            return self.valid_types['Int'].deserialize(
                value, attr, data, **kwargs)
        if isinstance(value, float):
            return self.valid_types['Float'].deserialize(
                value, attr, data, **kwargs)
        raise ValidationError(
            "Given Value is not Int, Float or None")


def validate_path(path: Any) -> None:
    """Validates if file path exists"""
    path = pathlib.Path(path)
    if not path.exists():
        raise ValidationError('Not a valid path')


def validate_filepath_model(value: Any) -> None:
    """Validates if model path ends on .zip"""
    path = pathlib.Path(value)
    if path.suffix != '.zip':
        raise ValidationError(
            'Model path should include a model.zip at the end')


def validate_filepath_samples(value: Any) -> None:
    """Validates if samples path ends on .csv or .pkl"""
    path = pathlib.Path(value)
    if path.suffix not in ['.csv', '.pkl']:
        raise ValidationError('Not a valid path')


def validate_app_threads(n_threads: int) -> None:
    """Validates number of app threads"""
    if n_threads < -1 or n_threads == 0:
        raise ValidationError(
            "App threads can't be smaller than -1. or equal 0."
            "Choose either -1(flexible number of threads) "
            "or > 0 (fixed number of threads).")


@ dataclass
class AppConfiguration:
    """Dataclass which stores app config"""

    algorithm: str
    # randomforest, xgboost, singleclass,kmeans
    window: int  # Any int, preferably within 2^x
    model: Optional[pathlib.Path]  # Model File location
    model_save: bool  # Save a model file which can be re-used
    samples: Optional[pathlib.Path]  # Samples file location (csv)
    log_level: str  # Logging level
    threads: int  # of threads
    imputation: bool  # Use simple imputation for missing values
    imputation_strategy: str  # Strategy for imputation. mean,
    imputation_constant: int  # constant for imputation
    # if constant was chosen as imputation method
    rasters_are_timeseries: bool  # Rasters are timeseries


class AppConfigurationSchema(Schema):
    """Schema for the App configuration dataclass.
    Will raise ValidationErrors when invalid data are passed in"""

    algorithm = fields.Str(validate=validate.OneOf(ALGORITHMS))
    window = fields.Int(
        validate=validate.Range(min=1, error="Value must be greater than 0"))
    model = PathField(validate=[validate_path, validate_filepath_model],
                      allow_none=True)
    model_save = fields.Bool()
    samples = PathField(
        validate=[validate_path, validate_filepath_samples], allow_none=True)
    threads = fields.Int(validate=validate_app_threads)
    log_level = fields.Str(validate=validate.OneOf(LOG_LEVELS))
    imputation = fields.Bool()
    imputation_strategy = fields.Str(
        validate=validate.OneOf(IMPUTATION_STRATEGIES))
    imputation_constant = fields.Int()
    rasters_are_timeseries = fields.Bool()


@ dataclass
class OptimizeSupervisedConfiguration():
    """Dataclass which stores the optimization parameters for
    the supervised classification"""

    optimize: bool  # Optimize the model parameters
    optimize_number: int  # Number of iterations for optimization


class OptimizeSupervisedConfigurationSchema(Schema):
    """Schema for the optimization part of the supervised classification
    configuration dataclass.
    Will raise ValidationErrors when invalid data are passed in"""

    optimize = fields.Bool()
    optimize_number = fields.Int(
        validate=validate.Range(
            min=1,
            error="Value must be greater than 0. Better value is > 5.")
    )

@ dataclass
class SubsampleSupervisedConfiguration():
    """Dataclass which stores the subsample parameters for
    the supervised classification"""

    active: bool  # Do sampling
    group_by: str  # Groupby class or roi_fid
    sample_type: str # n or frac
    amount: Union[int, float] # int for n and float for frac
    replace: bool # reuse values when sampling


class SubsampleSupervisedConfigurationSchema(Schema):
    """Schema for the subsample part of the supervised classification
    configuration dataclass.
    Will raise ValidationErrors when invalid data are passed in"""
    active = fields.Bool()
    group_by = fields.Str(validate=validate.OneOf(['class', 'roi_fid']))
    sample_type = fields.Str(validate=validate.OneOf(['n', 'frac']))
    amount = IntFloatField(
        {'Int':
            fields.Int(
                validate=validate.Range(
                    min=1,
                    error="Value must be >= 1."),
            ),
         'Float':
            fields.Float(
                validate=validate.Range(
                    min=0.01, max=1))
         }
    )
    replace = fields.Bool()

@ dataclass
class SupervisedConfiguration:
    """Dataclass which stores supervised classification config"""

    probability: bool  # output probability map
    all_probabilities: bool
    remove_outliers: bool  # Remove outliers from the training data
    optimization: OptimizeSupervisedConfiguration
    subsample: SubsampleSupervisedConfiguration


class SupervisedConfigurationSchema(Schema):
    """Schema for the supervised classification configuration dataclass.
    Will raise ValidationErrors when invalid data are passed in"""

    probability = fields.Bool()
    all_probabilities = fields.Bool()
    remove_outliers = fields.Bool()  # Remove outliers from the training data
    optimization = fields.Nested(OptimizeSupervisedConfigurationSchema)
    subsample = fields.Nested(SubsampleSupervisedConfigurationSchema)


@ dataclass
class UnsupervisedConfiguration:
    """Dataclass which stores unsupervised classification config"""

    nclasses: int  # Number of classes for unsupervised
    trainfraction: float  # Fraction of raster used for training


class UnsupervisedConfigurationSchema(Schema):
    """Schema for the unsupervised classification configuration dataclass.
    Will raise ValidationErrors when invalid data are passed in"""

    nclasses = fields.Int(validate=validate.Range(
        min=2, error="Value must be > 1 . This results in at least 2 classes.")
    )  # Number of classes for unsupervised
    trainfraction = fields.Float(validate=validate.Range(
        min=0.01,
        max=1.0,
        error="Fraction of data used for training should be at least 0.01 "
        "and <= 1.0(use all data for training)")
    )  # Fraction of raster used for training


@ dataclass
class OptimizeRandomForestConfiguration:
    """Dataclass which stores algorithm config"""

    n_estimators: List[int]
    max_depth: List[Optional[int]]
    max_features: List[Union[str, int, float]]
    max_leaf_nodes: List[Optional[int]]


class OptimizeRandomForestConfigurationSchema(Schema):
    """Schema for the algorithm configuration dataclass.
    Will raise ValidationErrors when invalid data are passed in"""
    n_estimators = fields.List(
        fields.Int(
            validate=validate.Range(
                min=1,
                error="Value must be >= 1. Rather use 50 or 100.")
        ))
    max_depth = fields.List(
        fields.Int(
            validate=validate.Range(
                min=1,
                error="Value must be >= 1 or NONE."),
            allow_none=True
        ))
    max_features = fields.List(
        fields.Str(
            validate=validate.OneOf(["auto", "sqrt", "log2"]))
    )
    max_leaf_nodes = fields.List(
        fields.Int(
            validate=validate.Range(
                min=1,
                error="Value must be >= 1 or NONE."),
            allow_none=True
        )
    )


@ dataclass
class RandomForestConfiguration:
    """Dataclass which stores algorithm config"""

    n_estimators: int
    criterion: str
    max_depth: Optional[int]
    min_samples_split: Union[int, float]
    min_samples_leaf: Union[int, float]
    min_weight_fraction_leaf: float
    max_features: Union[str, int, float]
    max_leaf_nodes: Optional[int]
    min_impurity_decrease: float
    bootstrap: bool
    oob_score: bool
    random_state: Optional[int]
    verbose: int
    class_weight: Optional[Union[str, dict, List[dict]]]
    ccp_alpha: float
    max_samples: Optional[Union[int, float]]
    optimization_parameters: dict


class RandomForestConfigurationSchema(Schema):
    """Schema for the algorithm configuration dataclass.
    Will raise ValidationErrors when invalid data are passed in"""
    n_estimators = fields.Int(validate=validate.Range(
        min=1, error="Value must be >= 1. Rather use 50 or 100.")
    )
    criterion = fields.Str(validate=validate.OneOf(["gini", "entropy"]))
    max_depth = fields.Int(validate=validate.Range(
        min=1, error="Value must be >= 1 or NONE."), allow_none=True
    )
    min_samples_split = IntFloatField(
        {'Int': fields.Int(
            validate=validate.Range(
                min=1,
                error="Consider min_samples_split as the minimum number")),
         'Float': fields.Float(
             validate=validate.Range(min=0.01, max=1))
         }
    )
    min_samples_leaf = IntFloatField(
        {'Int':
            fields.Int(
                validate=validate.Range(
                    min=1,
                    error="Value must be >= 1."),
            ),
         'Float':
            fields.Float(
                validate=validate.Range(
                    min=0.01, max=1))
         }
    )
    min_weight_fraction_leaf = fields.Float(validate=validate.Range(
        min=0, error="Value must be >= 0")
    )
    max_features = fields.Str(validate=validate.OneOf(["sqrt", "log2"]))
    max_leaf_nodes = fields.Int(validate=validate.Range(
        min=1, error="Value must be >= 1 or NONE."), allow_none=True
    )
    min_impurity_decrease = fields.Float(validate=validate.Range(
        min=0, error="Value must be >=0")
    )
    bootstrap = fields.Bool()
    oob_score = fields.Bool()
    random_state = fields.Int(validate=validate.Range(
        min=1, error="Value must be > 0 or NONE."), allow_none=True
    )
    verbose = fields.Int(validate=validate.Range(
        min=0, error="Value must be >= 0 or NONE."), allow_none=True
    )
    class_weight = fields.Str(validate=validate.OneOf(
        ["balanced", "balanced_subsample"]), allow_none=True)
    ccp_alpha = fields.Float(validate=validate.Range(
        min=0, error="Value must be >=0"), allow_none=True
    )
    max_samples = IntFloatField(
        {'Int':
            fields.Int(
                validate=validate.Range(
                    min=1, error="Value must be >= 1 or NONE.")
            ),
         'Float':
            fields.Float(
                validate=validate.Range(
                    min=0.01, max=1)
            ),
         },
        allow_none=True
    )
    optimization_parameters = fields.Dict(
        keys=fields.Str(),
        values=fields.List(fields.Raw(allow_none=True), allow_none=False),
        allow_none=True)


@ dataclass
class AccuracyConfiguration:
    """Dataclass which stores accuracy config"""

    perform_assesment: bool  # Perform accuracy assessment
    testfraction: float  # Fraction of data to use for training


class AccuracyConfigurationSchema(Schema):
    """Schema for the accuracy configuration dataclass.
    Will raise ValidationErrors when invalid data are passed in"""

    perform_assesment = fields.Bool()  # Perform accuracy assessment
    testfraction = fields.Float(validate=validate.Range(
        min=0,
        max=1.0,
        error="Fraction of data used for testing should be > 0 when "
        "perform_assessment is True and < 1.0")
    )  # Fraction of data to use for training


@ dataclass
class DtwConfiguration:
    """Dataclass which stores dtw config"""

    patterns: Optional[pathlib.Path]
    patterns_save: bool
    number_of_patterns_per_class: int
    n_neighbors: int
    window: Optional[int]
    max_dist: Optional[float]
    use_pruning: Optional[bool]
    penalty: Optional[float]
    optimization_parameters: dict


class DtwConfigurationSchema(Schema):
    """Schema for the dtw configuration dataclass.
    Will raise ValidationErrors when invalid data are passed in"""
    patterns = PathField(
        validate=[validate_path, validate_filepath_samples], allow_none=True)
    patterns_save = fields.Bool()  # Remove outliers from the training data
    number_of_patterns_per_class = fields.Int(
        validate=validate.Range(min=1,
                                error="""Must create at least 1 pattern
                                per class"""))
    n_neighbors = fields.Int(
        validate=validate.Range(min=1,
                                error="Neighbors must be at least >=1"))
    window = fields.Int(
        validate=validate.Range(min=1,
                                error="Window must be at least >=1 or None"),
        allow_none=True
    )
    max_dist = fields.Float(
        validate=validate.Range(min=0.001,
                                error="Max_dist must be at least >0 or None"),
        allow_none=True
    )
    use_pruning = fields.Bool(allow_none=True)
    penalty = fields.Float(
        validate=validate.Range(min=0.001,
                                error="Penalty must be at least >0 or None"),
        allow_none=True
    )
    optimization_parameters = fields.Dict(
        keys=fields.Str(),
        values=fields.List(fields.Raw(allow_none=True)),
        allow_none=True)


class ConfigurationSchema(Schema):
    """ConfigurationSchema for nested json.
    Each section in the json will get validated with a different schema"""

    app = fields.Nested(AppConfigurationSchema)
    supervised = fields.Nested(SupervisedConfigurationSchema)
    unsupervised = fields.Nested(UnsupervisedConfigurationSchema)
    accuracy = fields.Nested(AccuracyConfigurationSchema)
    dtw = fields.Nested(DtwConfigurationSchema)
    randomforest = fields.Nested(RandomForestConfigurationSchema)


@ dataclass
class Configuration:
    """Main Configuration dataclass.
    Has sub dataclasses for the different parts"""
    app: AppConfiguration
    supervised: SupervisedConfiguration
    unsupervised: UnsupervisedConfiguration
    accuracy: AccuracyConfiguration
    dtw: DtwConfiguration
    randomforest: RandomForestConfiguration
    # name and tmp_dir are defined on runtime
    name: str
    tmp_dir: Any


def update_config_dict(config_dict_to_update: dict, updates: dict) -> dict:
    """Updates the nested default config dict with the user
    provided nested config dict

    Args:
        config_dict_to_update (dict): nested default config dict
        updates (dict): nested dict with updates

    Returns:
        dict: updated nested dict
    """
    updated_dict = {}
    for key, value in config_dict_to_update.items():
        if key in updates:
            if key == 'optimization_parameters':
                # only use user provided model parameters for optimization
                updated_dict[key] = updates[key]
                continue
            # key is in the updates
            if isinstance(value, dict):
                # call function recursively with sub dict to find the key
                # to be updated
                updated_dict[key] = update_config_dict(value, updates[key])
            else:
                # update the key
                updated_dict[key] = updates[key]
        else:
            # set the default value for the key, if it is not in the
            # update keys
            updated_dict[key] = config_dict_to_update[key]
    return updated_dict


def setup_config(config_path: Optional[pathlib.Path] = None) -> Configuration:
    """Setup method for the Configuration Dataclass.
    Uses marshmallow schemas to load the json and validate
    types and values. Dacite creates dataclass from that.

    Args:
        config_path (pathlib.Path): path to json config file

    Returns:
        config (Configuration): dataclass containing configs
    """
    if config_path and config_path.is_file():
        # loads json from path
        with open(config_path, encoding='UTF-8') as file:
            config_dict = json.load(file)
            updated_config_dict = update_config_dict(PARAMETERS, config_dict)
            config_json = json.dumps(updated_config_dict)
    else:
        print("No local config file found. Using default config")
        # Use default config dictionary
        config_json = json.dumps(PARAMETERS)
    config = json_to_config(config_json)
    return config


def json_to_config(config_json: str) -> Configuration:
    """Converts the json object to a dataclass with type and value validation

    Args:
        config_json (str): JSON formatted string

    Returns:
        [dataclass]: dataclass containing configs
    """
    # validates the type and range of the config Values
    try:
        result = ConfigurationSchema().load(json.loads(config_json))
    except ValidationError as error:
        UTILS_CONFIG_LOGGER.error(error)
        sys.exit(1)

    # add name and tmp dir
    result['name'] = ''
    result['tmp_dir'] = None

    # creates the Configuration dataclass instance from the checked data
    return dacite.from_dict(data_class=Configuration,
                            data=result
                            # config=dacite.Config(type_hooks=converters),
                            )
