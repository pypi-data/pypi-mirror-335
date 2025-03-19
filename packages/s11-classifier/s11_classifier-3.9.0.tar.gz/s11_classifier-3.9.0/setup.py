# -*- coding: utf-8 -*-
# (c) Satelligence, see LICENSE.
# pylint: skip-file
import setuptools
from setuptools import setup

version = '3.9.0'

long_description = open('README.md').read()

test_requirements = [
    'pytest'
]

setup(
    name='s11-classifier',
    version=version,
    description="Classifier",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Satelligence",
    author_email='team@satelligence.com',
    url='https://gitlab.com/satelligence/classifier',
    packages=setuptools.find_packages(),
    package_dir={
        'classifier': 'classifier'
    },
    include_package_data=True,
    install_requires=[
        'boto3~=1.37.1',
        'click~=8.1.3',
        'dacite~=1.9.0',
        'dtaidistance~=2.3.10',
        'fiona~=1.10.1',
        'folium~=0.19.0',
        'geojson~=3.2.0',
        'geopandas~=1.0.1',
        'h5py~=3.13.0',
        'marshmallow~=3.26.0',
        'matplotlib~=3.10.0',
        'numpy~=2.2.3',
        'python-dateutil~=2.9.0',
        'rasterio~=1.4.3',
        'rasterstats~=0.20.0',
        'rtree~=1.3.0',
        'scikit_learn~=1.6.1',
        'tqdm~=4.67.0',
        'xarray~=2025.1.2',
        'xgboost~=2.1.4',
    ],
    license="Apache-2.0",
    zip_safe=False,
    python_requires='>=3.5'
)
