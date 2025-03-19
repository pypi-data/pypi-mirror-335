"""General utilities"""
import contextlib
import dataclasses
import json
import logging
import os
import shutil
import sys
import tempfile
from itertools import product
from pathlib import Path
from typing import Any, Callable, List, Tuple, Optional, Dict, Union
from uuid import uuid4
from zipfile import ZipFile

import joblib
#from matplotlib.patches import Polygon
import numpy as np
import rasterio
from joblib import Parallel, delayed
from tqdm import tqdm
from shapely.geometry import shape, box
from sklearn.base import BaseEstimator

from classifier.settings import RASTER_EXTENSIONS, WORKSPACE
from classifier.utils.config import (
    Configuration, setup_config, PARAMETERS)

UTILS_GENERAL_LOGGER = logging.getLogger(__name__)


def get_available_model_args(model_args: dict, model: BaseEstimator) -> dict:
    """Gets the available parameters of the model
        Args:
            model_args (dict) : arguments to check
            model (BaseEstimator): function to check the kwargs from

        Returns:
            model_algorithm_args(list): model arguments that belong to function

    """
    kwarglist = model.get_params().keys()
    model_algorithm_args = [x for x in model_args.keys() if x in kwarglist]
    return {k: model_args[k] for k in model_algorithm_args}


def progress(count: int, total: int, status: str = '') -> None:
    """A simple progress bar for the command line

    Args:
        count (int): Count between 0 and total
        total (int): Last iteration
        status (str): State

    """
    count += 1
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    p_bar = '=' * filled_len + '-' * (bar_len - filled_len)
    sys.stdout.write(f'[{p_bar}] {percents}% ...{status}\r')
    sys.stdout.flush()


def cli_init(
    output_name: str, rasters: List[str],
    overwrite: bool, config_location: Union[str, Path],
    rois: Optional[str] = None) \
        -> Tuple[Path, List[Path], Path, Configuration]:
    """Initialize everything before starting real work.

    Args:
        output_name (str): name of the output directory in workspace
        rasters (List[str]): Raster paths
        overwrite (bool): overwrite existing folder
        config_location (Path): location of the config file
        rois (str): rois path for input


    Returns:
        output_directory: path to output directory
        rasters (List[Path]): list of separate raster files
        rois (Path): path of rois workspace appended
        config (Configuration): dict containing Config

    """
    # Set Random Seed for reproducible results
    np.random.seed(0)

    if isinstance(config_location, str):
        config_location = WORKSPACE / config_location
    config = read_config(config_location)

    output_directory = create_output_dir(WORKSPACE, output_name, overwrite)
    # pylint: disable = consider-using-with
    config.tmp_dir = tempfile.TemporaryDirectory(dir=output_directory)
    init_logger(output_directory, config.app.log_level)
    params_str = config_as_str(config)
    UTILS_GENERAL_LOGGER.info(
        "\nRunning the Classifier with the following parameters:"
        "\n  %s", params_str)
    if rois is not None:
        rois = WORKSPACE / rois

    raster_paths = get_raster_paths(WORKSPACE, rasters)

    return output_directory, raster_paths, rois, config


def config_as_str(config: Configuration) -> str:
    """ Adds config values to string
    Args:
        config (Configuration) contains config

    Returns:
        params_str (str): parameters formatted in a string
    """
    params_str = ''
    for key, value in dataclasses.asdict(config).items():
        if isinstance(value, dict):
            params_str = params_str + f'{key}:\n'
            for key_2, value_2 in value.items():
                if isinstance(value_2, dict):
                    params_str = params_str + f'    {key_2}:\n'
                    for key_3, value_3 in value_2.items():
                        params_str = params_str + \
                            f'        {key_3}:  {value_3}\n'
                else:
                    params_str = params_str + f'    {key_2}:  {value_2}\n'
        else:
            params_str = params_str + f'{key}:  {value}\n'
    return params_str


def create_output_dir(workspace: Path, name: str, overwrite: bool) -> Path:
    """Create output directory.

    Args:
        workspace (Path): The workspace Path
        name (str): Location of the directory
        overwrite (bool): overwrite existing folder

    Returns:
        Output directory (Path) Path of output directory

    """
    if name is None:
        name = str(uuid4())[:6]
        UTILS_GENERAL_LOGGER.info(
            "No name argument found. Making new folder "
            "called: %s", name)
    output_directory = workspace / name
    if output_directory.exists():
        if overwrite:
            UTILS_GENERAL_LOGGER.warning("Overwriting existing directory!")
            shutil.rmtree(output_directory)
            os.mkdir(output_directory)
        else:
            UTILS_GENERAL_LOGGER.error(
                "Directory with name %s already exists. Either "
                "leave --name out,remove the directory %s, "
                "provide a unique name or turn on --overwrite.", name, name)
            sys.exit()
    else:
        os.mkdir(output_directory)
    return output_directory


def save_dict_as_json(out_file: Path, dict_to_save: dict) -> None:
    """Saves a dict to json

    Args:
        out_file (Path): file to write
        dict_to_save (dict): Dictionary to save

    """
    with open(out_file, 'w', encoding='UTF-8') as config:
        config.write(json.dumps(dict_to_save,
                                sort_keys=True,
                                indent=1,
                                default=str))


def save_config_as_json(**kwargs: Dict[str, Any]) -> None:
    """Save default config values.

    Save default values for classifier parameters in json in current workspace.

    Args:
        kwargs (dict): values to put into the config

    """
    out_file = Path(WORKSPACE) / 'config.json'
    dict_to_save = PARAMETERS
    # update dict with provided parameters
    dict_to_save = update_dict(dict_to_save, **kwargs)
    with open(out_file, 'w', encoding='UTF-8') as config:
        config.write(json.dumps(dict_to_save, indent=4, default=str))


def update_dict(dict_to_update: dict, **kwargs: Dict[str, Any]) -> dict:
    """Update dict with provided values

    Args:
        dict_to_update (dict): dict which values should be updated
        **kwargs (dict): keywords and values to update

    Returns:
        updated_dict (dict): updated dict
    """
    updated_dict = {}
    for key, value in dict_to_update.items():
        if isinstance(value, dict):
            updated_dict[key] = update_dict(value, **kwargs)
        else:
            updated_dict[key] = kwargs.get(key, value)
    return updated_dict


def read_config(config_path: Path) -> Configuration:
    """Read config parameter file and change defaults where necessary.

    Args:
        config_path (pathlib.Path): location of the config file

    Returns:
        config (Configuration): nested dataclass with all config values
    """
    config = setup_config(config_path)

    return config


def init_logger(output_directory: Path, log_level: str) -> None:
    """Set and initialize all logging info.

    Args:
        output_directory (Path): The location of the log file
        log_level (str)

    """
    logging.captureWarnings(True)
    logging.basicConfig(level=logging.DEBUG,
                        filename=output_directory / 'stdout.log')
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # disable matplotlib logger
    logging.getLogger('matplotlib.font_manager').disabled = True

    # # create console handler and set level to info
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    # # create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # # add formatter to ch
    console_handler.setFormatter(formatter)
    # # add Handlers to logger
    logging.getLogger('').addHandler(console_handler)


def write_tifs(
        temp_dir: str, window: rasterio.windows.Window, meta: dict,
        result: np.ndarray) -> None:
    """Writes the tifs of the individual windows

    Args:
        temp_dir: Temp dir location (str)
        window: rasterio window (tuple)
        meta: rasterio meta dictionary for output
        result: Result array

    Returns:
        Nothing

    """
    # Check output dir existence
    os.makedirs(temp_dir, exist_ok=True)
    meta['compress'] = 'deflate'
    with rasterio.open(
            os.path.join(temp_dir, f"c{window.col_off}_{window.row_off}.tif"),
            'w', **meta) as dst:
        dst.write_band(1, result)


def save_model(model_dict: dict, out_dir: Path, config: Configuration) -> None:
    """Save the model as a pickle  and metadata  as a json and zip

    Args:
        model_dict (dict):  Contains the model as well as metadata
        out_dir (Path):      Path where to write model file and meta
        config (Configuration): Configuration parameters

    """
    to_save = model_dict.copy()
    meta_tmp = tempfile.mktemp()
    joblib_tmp = tempfile.mktemp()

    # Take the model out of the dictionairy
    model = to_save.pop('model')

    # Save the model as pickle
    with open(joblib_tmp, 'wb') as model_file:
        joblib.dump(model, model_file, compress=3)

    # Save meta as json
    save_dict_as_json(Path(meta_tmp), to_save)
    to_write = {
        meta_tmp: Path(f"{config.name}_meta.json"),
        joblib_tmp: Path(f"{config.name}.model")
    }

    # Zip to output directory
    zipfile_path = out_dir / 'model.zip'
    write_zipfile(to_write, zipfile_path)


def write_zipfile(files_to_write: dict, zipfile_path: Path) -> None:
    """Writes files to a zipfile

    Args:
        files_to_write (dict): dictionary of path, name of the files to
                               write to the zipfile (e.g.
                               {
                                  '/workspace/weirdname.json':
                                  'nice_name.json'
                               }
        zipfile_path (Path): Path to where the zipfile goes
    """
    with ZipFile(zipfile_path, 'w') as model_zip:
        for files in files_to_write:
            print(files, files_to_write[files])
            model_zip.write(files, files_to_write[files].name)


def get_raster_paths(workspace: Path, rasters: List[str]) -> List[Path]:
    """Get full paths for all rasters.

    Args:
        workspace (Path): The workspace Path
        rasters (List[Path]): List of rasters from the cli

    Returns:
        List[Path]: rasters with their full paths

    """
    paths = []

    for raster in rasters:
        path = workspace / raster
        if path.is_dir():
            paths += [path / r for r in sorted(path.iterdir())]
        else:
            paths.append(path)
    found_rasters = [path for path in paths if path.suffix in RASTER_EXTENSIONS]
    if not found_rasters:
        UTILS_GENERAL_LOGGER.info(
            "Found no rasters.")
        sys.exit(1)
    return found_rasters


def unzip_model_file(model_file: Path) -> Tuple[Path, Path]:
    """Unzips a model file and returns paths to metadata and model pickle

    Args:
        model_file (Path): path to the model zipfile

    Returns:
        meta_file (Path): path to tmp metafile
        pickle_file (Path): path to tmp pickle file
    """
    tmpdir = Path(tempfile.mkdtemp())
    with ZipFile(model_file, 'r') as zipf:
        zipf.extractall(tmpdir)

    model_files = list(tmpdir.iterdir())
    meta_file = tmpdir / [x for x in model_files if x.suffix == '.json'][0]
    pickle_file = tmpdir / [x for x in model_files if x.suffix == '.model'][0]
    return meta_file, pickle_file


def read_model(model_file: Path) -> dict:
    """Function to read the model file and return a pickle

    Args:
        path: The path to the model zipfile

    Returns:
        a dictionary containing a model, and metadata

    """
    # Unzip
    meta_file, joblib_file = unzip_model_file(model_file)
    # Open the metadata and print the modeltypes
    with open(meta_file, encoding='UTF-8') as json_config:
        model_dict = json.load(json_config)

    params_str = '\n'.join(
        [f'{key} :  {value}' for key, value in sorted(model_dict.items())])

    with open(joblib_file, 'rb') as m_file:
        model_dict['model'] = joblib.load(m_file)

    UTILS_GENERAL_LOGGER.info(
        "\nLoaded a saved model, with the following metadata:"
        "\n  %s", params_str)

    return model_dict


def parallel_function(func: Callable,
                      iterable: List[dict],
                      ncpus: int = 1) -> Any:
    """Runs a function in parallel using Joblib

    Args:
        func: Function to run
        iterable (list): List of kwargs for the function
        ncpus (int): number of cpus to use

    Returns:
        list of results
    """
    with tqdm_joblib(tqdm(total=len(iterable))) as _:
        result = Parallel(
            n_jobs=ncpus, max_nbytes=None
        )(delayed(func)(**x) for x in iterable)

    return result


@ contextlib.contextmanager
def tqdm_joblib(tqdm_object: tqdm) -> None:
    """Patch joblib to report a tqdm progress bar for many thread jobs

    Args:
        tqdm_object (tqdm.tqdm): Iterable decorated with progress bar

    Yields:
        tqdm.tqdm: Iterable decorated with progress bar
    """

    # pylint: disable=too-few-public-methods
    class TqdmBatchCompletionCallback(joblib.parallel.BatchCompletionCallBack):
        """ Class to pass completion callback to tqdm"""

        def __call__(self, out: object) -> Any:
            """Updates tqdm and returns joblib call

            Args:
                 out (object): Any object

            Returns:
                object: Any object
            """
            tqdm_object.update(n=self.batch_size)
            return super().__call__(out)

    old_batch_callback = joblib.parallel.BatchCompletionCallBack
    joblib.parallel.BatchCompletionCallBack = TqdmBatchCompletionCallback
    try:
        yield tqdm_object
    finally:
        joblib.parallel.BatchCompletionCallBack = old_batch_callback
        tqdm_object.close()


def rois_in_raster_extent(rasters: List[Path], rois: List[dict]) -> bool:
    """Check if the rois lie in raster extent

    Args:
        rasters (List[Path]): List of raster paths
        rois (List[dict]): List of rois path

    Returns:
        bool: True if all rois lay in raster
    """
    all_rois_in_raster = True
    with rasterio.open(rasters[0]) as src:
        raster_geom = box(*src.bounds)
        for roi in rois:
            roi_geom = shape(roi['geometry'])
            if not raster_geom.contains(roi_geom):
                UTILS_GENERAL_LOGGER.warning(
                    "Roi %s does not lie in the raster", str(roi['id'])
                )
                all_rois_in_raster = False
    return all_rois_in_raster


def dict_product(d: dict) -> dict:  # pylint: disable=invalid-name
    """ Function to build all combinations of multiple lists. But
    returns a dict with the argument name as key to still know which
    value belongs to which key (element)"""
    keys = d.keys()
    for element in product(*d.values()):
        yield dict(zip(keys, element))
