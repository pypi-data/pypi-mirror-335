"The command line interface and entry point for classifier"
# pylint: disable=too-many-positional-arguments
import logging
import pathlib
import sys
from typing import Union, Optional

import click

from classifier.accuracy import assess_accuracy
from classifier.classify import classify_, classify_timeseries
from classifier.settings import WORKSPACE
from classifier.utils.general import cli_init, save_config_as_json

CLI_LOGGER = logging.getLogger(__name__)


@click.group()
def cli() -> None:
    """---Classifier---
     Classification of rasters using ground truth"""


@cli.command()
@click.argument(
    'rasters',
    nargs=-1,
    type=click.Path(),
)
@click.option('--rois',
              default=None,
              type=click.Path(),
              help="""OGR supported polygon file""")
@click.option('--name',
              type=click.STRING,
              help="""Name of the output folder""")
@click.option('--overwrite',
              default=False,
              type=click.BOOL,
              help="""Overwrite Existing output folder"""
              )
@click.option('--config_location',
              default=WORKSPACE / 'config.json',
              type=click.Path(),
              help="""Use a custom location for configuration file""")
def classification(
        name: str, rasters: list, rois: Optional[str], overwrite: bool,
        config_location: Union[str, pathlib.Path]) -> None:
    """Do a traditional (un)supervised classification

    Raster input paths can be added like arguments without a prefix.
    Multiple raster paths can be added

    For additional options, create a config file in your workspace. Also see
    https://satelligence.gitlab.io/classifier/usage/configfile.html.

    """
    out_dir, rasters, rois, config = \
        cli_init(
            name,
            rasters,
            overwrite,
            config_location,
            rois
        )
    config.name = name
    if config.app.rasters_are_timeseries:
        classify_timeseries(rasters, config, out_dir, rois)
    else:
        if config.app.algorithm == "knn_dtw":
            CLI_LOGGER.error("K-Nearest Neighbour with Dynamic Time Warping "
                             "can only be used with timeseries. Set "
                             "rasters_are_timeseries=True")
            sys.exit(1)
        classify_(rasters, config, out_dir, rois)


@ cli.command()
@ click.option('--name',
               type=click.STRING,
               help="""Name of the output folder""")
@ click.option('--raster',
               default=None,
               type=click.Path(),
               help="""Raster file with classification result""")
@ click.option('--rois',
               default=None,
               type=click.Path(),
               help="""OGR supported polygon file""")
@ click.option('--subset',
               default=None,
               type=click.Path(),
               help="""OGR supported polygon file""")
@ click.option('--overwrite',
               default=False,
               type=click.BOOL,
               help="""Overwrite Existing output folder""")
@ click.option('--config_location',
               default=WORKSPACE / 'config.json',
               type=click.Path(),
               help="""Use a custom location for configuration file""")
def accuracy_assessment(name: str,
                        raster: pathlib.Path,
                        rois: str,
                        subset: str,
                        overwrite: bool,
                        config_location: Union[str, pathlib.Path]) -> None:
    """Accuracy assessment.
    """
    out_dir, rasters, rois_path, config = cli_init(
        name,
        [str(raster)],
        overwrite,
        config_location,
        rois
    )
    if subset is not None:
        subset = WORKSPACE / subset
    assess_accuracy(rasters[0], rois_path, out_dir, config, subset)


@ cli.command()
def make_config() -> None:
    """Make a config file with default values in your workspace directory
    and exit"""
    save_config_as_json()


if __name__ == '__main__':
    cli()
