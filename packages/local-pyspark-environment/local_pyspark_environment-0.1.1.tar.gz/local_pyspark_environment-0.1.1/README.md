# Local Pyspark Environment

Use it for local testing of your pyspark code

## Environment setup

1. `conda env create -f environment.yml -p .venv`
1. `conda activate $PWD/.venv`
1. `poetry install --no-root`

## Checking code quality

1. `poe black`

