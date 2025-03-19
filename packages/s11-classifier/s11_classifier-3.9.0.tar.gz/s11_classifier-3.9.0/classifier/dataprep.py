"""All the necessary functions for preparing the data for the classification
model can be found here.."""
import logging
import pandas as pd


# Set Logging levels on Rasterio and Fiona to not get too many logging msg
RASTERIO_LOGGER = logging.getLogger('rasterio')
RASTERIO_LOGGER.setLevel(logging.CRITICAL)
FIONA_LOGGER = logging.getLogger('fiona')
FIONA_LOGGER.setLevel(logging.CRITICAL)
DATAPREP_LOGGER = logging.getLogger(__name__)


def check_training_extent() -> None:
    """Check whether the extent of the rois falls outside of the extent of the
        rasters"""
    raise NotImplementedError


def class_counts(samples: pd.DataFrame) -> None:
    """Prints the number of pixels removed after outlier removal

    Args:
        samples (pd.DataFrame): Gathered samples with 'inlier' column

    """
    count_dict = samples.groupby(
        ['class', 'inlier']).size().unstack().to_dict(orient='index')

    # print the header of the table
    to_print = (
        f"\t\t{'Class':<4}"
        f"\t{'#Remaining':<10}"
        f"\t{'Removed':<10}"
        f"{'Remaining fraction':<10}"
    )
    DATAPREP_LOGGER.info("%s", to_print)

    for class_label, pixel_count in list(count_dict.items()):
        remaining = pixel_count[1]
        removed = pixel_count[-1]
        # PRint the row of the table
        to_print = (
            f"\t\t{class_label:<4}"
            f"\t{remaining:<10}"
            f"\t{removed:<10}"
            f"\t{(remaining/(remaining+removed)):<10.2f}"
        )
        DATAPREP_LOGGER.info("%s", to_print)
