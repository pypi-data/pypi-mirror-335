"Accuracy assessment and plotting for classifier"
import itertools
import logging
import time
from pathlib import Path
from typing import List, Optional, Tuple

import fiona
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from shapely.geometry import shape
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import cohen_kappa_score, confusion_matrix
from sklearn.metrics import classification_report
from tqdm import tqdm

from classifier.utils.raster import clip_raster_on_geometry, ndarray_to_df
from classifier.utils.config import Configuration
from classifier.utils.vector import create_spatial_index, true_intersect

ACCURACY_LOGGER = logging.getLogger(__name__)


def write_confusion_matrix(
        model_dict: dict, test_set: pd.DataFrame, out_dir: Path,
        plot: bool = True, csv: bool = True) -> None:
    """ Uses a sklearn confusion matrix (np 2d array) to write to a csv file
    that also contains overall metrics. Also plots the confusion matrix for
    easier viewing.

        Args:
            model_dict (dict):dictionary with the name, model and label encoder
            test_set (pd.DataFrame): test dataset not used during training
            out_dir (Path): output folder
            plot (bool): Whether or not to plot the figure
            csv (bool): Whether or not to write csv file

        returns:
            nothing
    """
    # Convert dict and dataframe to arrays
    x_test = test_set[[x for x in test_set.columns
                       if 'class' not in x and 'roi_fid' not in x]].values
    y_test = np.ravel(
        test_set[[x for x in test_set.columns if 'class' in x]].values)
    preds = model_dict['model'].predict(x_test)
    labels = {int(k): int(v) for k, v in model_dict['labels'].items()}
    preds_decoded = np.vectorize(lambda x: labels[x])(preds)
    compute_confusion_matrix(y_test, preds_decoded, out_dir, plot, csv)


def compute_confusion_matrix(
        y_test: np.ndarray, preds: np.ndarray, out_dir: Path, plot: bool = True,
        csv: bool = True) -> None:
    """ Uses a sklearn confusion matrix (np 2d array) to write to a csv file
    that also contains overall metrics. Also plots the confusion matrix for
    easier viewing.

        Args:
            y_test (np.array): Ground truth (correct) target values
            preds (np.array): Estimated targets as returned by a classifier
            out_dir (Path): output folder
            plot (bool): Whether or not to plot the figure
            csv (bool):  Whether or not to write the csv
    """

    # Write and plot confusion Matrix
    cm_labels = sorted(list(set(np.unique(y_test)) | set(np.unique(
        preds))))
    kappa = cohen_kappa_score(y_test, preds, labels=cm_labels)
    conf_matrix = confusion_matrix(y_test, preds, labels=cm_labels)

    # Metrics: overall mean accuracy and kappa
    ACCURACY_LOGGER.info("\n####-----Accuracy Assessment-----#####\n")
    metrics_list = []
    metrics_list.append(
        f'Overall Accuracy {np.trace(conf_matrix)/np.nansum(conf_matrix)}'
    )
    metrics_list.append(f'Kappa {kappa:.4f}')
    for metric in metrics_list:
        ACCURACY_LOGGER.info(metric)

    if csv:
        df_cm = pd.DataFrame(
            data=conf_matrix, index=cm_labels, columns=cm_labels)
        # Total of the rows
        df_cm['Total'] = df_cm.sum(axis=1)
        # Accuracy
        df_cm['Accuracy'] = np.diag(df_cm[cm_labels]) / df_cm['Total']
        # Appending the numbers to the df
        total_row = df_cm.sum(axis=0).rename('Total')
        reliability = pd.Series(
            np.diag(conf_matrix) / np.sum(conf_matrix, axis=0),
            index=cm_labels).rename('Reliability')
        df_cm_all = pd.concat(
            [df_cm, pd.DataFrame(total_row).T,
             pd.DataFrame(reliability).T],
            axis=0)
        df_cm_all.to_csv(
            out_dir / 'confusion_matrix.csv', sep=';', float_format='%.4f')

    if plot:
        # Plotting if necessary
        try:
            # Plot normalized confusion matrix
            plt.figure()
            plot_confusion_matrix(conf_matrix,
                                  classes=cm_labels,
                                  normalize=True
                                  )
            plt.tight_layout()
            plt.savefig(out_dir / 'confusion_matrix_plot.png', dpi=150)
        except AttributeError:  # Not all models have FIs, so skip
            pass


def plot_confusion_matrix(conf_matrix: np.ndarray, classes: List[str],
                          normalize: bool = False,
                          cmap: matplotlib.colors.Colormap = plt.cm.Blues) \
        -> None:
    """This function prints and plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.

    Args:
        conf_matrix (np.ndarray): confusion matrix
        classes (list): Class names
        normalize (bool, optional): Wether to normalize the conf matrix
        cmap (colormap, optional): colormap
    """
    if normalize:
        conf_matrix = conf_matrix.astype('float') /\
            conf_matrix.sum(axis=1)[:, np.newaxis]
    plt.imshow(conf_matrix, interpolation='nearest', cmap=cmap)
    plt.title("Confusion Matrix")
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=90, fontsize=6)
    plt.yticks(tick_marks, classes, fontsize=8)

    fmt = '.2f' if normalize else 'd'
    thresh = conf_matrix.max() / 2.
    for i, j in itertools.product(range(conf_matrix.shape[0]),
                                  range(conf_matrix.shape[1])):
        plt.text(j, i, format(conf_matrix[i, j], fmt),
                 horizontalalignment="center",
                 color="white" if conf_matrix[i, j] > thresh else "black",
                 fontsize=4)

    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')


def plot_feature_importances(model_dict: dict, out_dir: Path) -> None:
    """Plot the feature importances of the forest

    Args:
        model_dict (dict): dict containing the model, metadata and feature names
        out_dir (Path): output folder
    """
    importances = model_dict['model'].feature_importances_
    feat_importances = pd.Series(importances, index=model_dict['names'])

    # only features which have higher importance than 0.01 are plotted
    feat_importances_big = feat_importances[feat_importances > 0.01]

    fig, axis = plt.subplots()
    axis.set_title("Feature importances >0.01 \n(band numbers)")
    axis.set_xlabel("Mean decrease in impurity")

    # Get STD whenever possible
    if model_dict['app_algorithm'] in [
            'randomforest', 'randomforest_ts_metrics']:
        std = pd.Series(
            np.std([tree.feature_importances_ for tree in model_dict[
                'model'].estimators_], axis=0), index=model_dict['names'])
        std = std[feat_importances > 0.01]
        feat_importances_big.sort_values(ascending=False).plot(
            ax=axis, color=['red'], kind='barh', xerr=std)
    else:
        feat_importances_big.sort_values(ascending=False).plot(
            ax=axis, color=['red'], kind='barh')
    fig.tight_layout()
    outfile = out_dir / 'feature_importance.png'
    plt.savefig(outfile, dpi=300)


def collect_classification_and_reference(
        raster: Path,
        rois: Path,
        subset: Path | None = None,
    ) -> Tuple[np.ndarray, np.ndarray]:
    """Collect the classification result and reference class for given rois.
    Ignore rois if it intersects with rois in subset (used for classification). 

    Args:
        raster (Path): raster path
        rois (Path): all rois
        subset (Path | None, optional): rois used for classification. Defaults to None.

    Returns:
        Tuple[np.ndarray, np.ndarray]: class prediction, class reference
    """
    ACCURACY_LOGGER.info("Collect predicted and reference class")
    # Is subset is given, exclude its polygons from accuracy assessment
    if subset:
        rtree_index = create_spatial_index(subset)
    all_y_pred = []
    all_y_true = []
    counter = 0
    with fiona.open(rois, "r") as shapefile:
        for roi in tqdm(shapefile):
            roi_geom = shape(roi['geometry'])
            if subset:
                with fiona.open(subset) as subset_polygons:
                    fids = list(rtree_index.intersection(roi_geom.bounds))
                    # only skip when theres a true intersection
                    if any(
                        true_intersect(
                            roi_geom, shape(subset_polygons[int(fid)]['geometry']))
                        for fid in fids
                    ):
                        counter += 1
                        continue
            roi_samples = clip_raster_on_geometry(raster, roi_geom).flatten()
            if roi_samples is not None and roi_samples.size != 0:
                y_pred = roi_samples.astype(int)
                y_true = int(roi['properties']['id'])

                all_y_pred += list(y_pred)
                all_y_true += len(y_pred) * [y_true]

        all_y_pred = np.array(all_y_pred)
        all_y_true = np.array(all_y_true)

        ACCURACY_LOGGER.info(
            "Using %i groundtruth polygons, excluding %i already used in classifier",
            len(shapefile),
            counter)
    return all_y_pred, all_y_true


def assess_accuracy(
        raster: Path,
        rois: Path,
        out_dir: Path,
        config: Configuration,
        subset: Optional[Path] = None,
    ) -> None:
    """"Accuracy assessment

    Args:
        raster (Path): Path of classication raster
        rois (Path): Path of rois
        out_dir (Path): Path of output
        config (Configuration): Configuration
        subset (Path, optional): Path of subset used for classication
    """
    start = time.time()
    y_pred, y_true = collect_classification_and_reference(
        raster,
        rois,
        subset,
    )

    report = pd.DataFrame(
        classification_report(
            y_true=y_true,
            y_pred=y_pred,
            output_dict=True
            )
    ).T
    report.to_csv(
        out_dir / 'classification_report.csv',
        sep=';',
        float_format='%.4f',
    )

    # write confusion matrix
    compute_confusion_matrix(
        y_test=y_true, preds=y_pred, out_dir=out_dir, plot=True, csv=True)
    config.tmp_dir.cleanup()
    ACCURACY_LOGGER.info(
        "Total run time was %i seconds", (int(time.time() - start)))


def get_confidence_map_from_random_forest_model(
        model: RandomForestRegressor,
        array: np.ndarray,
        confidence_level=0.9,
) -> np.ndarray:
    """Get confidence map from random forest model

    Args:
        model (RandomForestRegressor): the model
        array (np.ndarray): the data array to calculate confidence on.
        confidence_level (float, optional): confidence level [0-1]. \
            Defaults to 0.9.

    Returns:
        np.ndarray: confidence map
    """
    data = ndarray_to_df(array)
    stack = None
    for tree in model.estimators_:
        prediction = tree.predict(data)
        stack = np.vstack(
            [stack, prediction]
        ) if stack is not None else prediction

    quantile_edge = (1 - confidence_level) / 2
    quantile_low = np.quantile(stack, quantile_edge, axis=0)
    quantile_high = np.quantile(stack, 1 - quantile_edge, axis=0)
    return ((quantile_high - quantile_low) / 2).reshape(array.shape[-2:])
