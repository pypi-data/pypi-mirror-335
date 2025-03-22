# Pyspark Databricks Environment

Set of basic environment-specific functions

## Environment setup

1. `conda env create -f environment.yml -p .venv`
1. `conda activate $PWD/.venv`
1. `poetry install --no-root`

## Checking code quality

1. `poe black`
