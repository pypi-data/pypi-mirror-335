"""Settings file for Classifier"""
from pathlib import Path
from sklearn.cluster import KMeans, MiniBatchKMeans
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from xgboost import XGBClassifier

from classifier.models import KnnDtw

WORKSPACE = Path('/workspace/')

RASTER_EXTENSIONS = frozenset(['.tif', '.vrt', '.jp2'])

US_ALGORITHMS = ['us_kmeans', 'us_kmeans_minibatch']

# ##----THE ALGORITHMS---###
ALGORITHMS = [
    "randomforest", "xgboost", "singleclass", "us_kmeans",
    "us_kmeans_minibatch", "knn_dtw"
]
CLASSIFIERS = [RandomForestClassifier, XGBClassifier, IsolationForest, KMeans,
               MiniBatchKMeans, KnnDtw]
ALGORITHM_DICT = dict(zip(ALGORITHMS, CLASSIFIERS))
