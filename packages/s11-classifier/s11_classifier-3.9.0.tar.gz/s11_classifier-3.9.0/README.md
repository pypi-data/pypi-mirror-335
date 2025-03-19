# Classifier

A scalable land cover classification tool for humans

Go to [the documentation](https://satelligence.gitlab.io/classifier) for more
 info on how to install and run Classifier!

## Note on performance

For now, the multithreading of XGboost is not properly implemented. If you have
a lot of input files the XGBoost method is MUCH slower than e.g. scikit-learn's
random forest. With single input files (so not a lot of IO operations), the
difference in performance is small.

## issues and bugs

Issues are tracked on the [issue list of this
repo](https://gitlab.com/satelligence/classifier/issues).

## Development

Please follow the [Satelligence development guidelines](https://gitlab.com/satelligence/workflow/blob/master/dev_workflow.md)
when adding features or fixing bugs.

(Fork) Clone this repo:

```sh
git clone git@gitlab.com:satelligence/classifier.git
```

Make sure you are running the latest docker image.

Run docker with a binding to the source files:

```sh
docker run  -v $(pwd):/app -t -i classifier
```