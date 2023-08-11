
# Introduction


## setting up environment

```sh
conda create -n ief-env yaml argparse black pandas
```

```sh
python3 src/main.py
```

## Gotchas

Currently `run_model()` is not returning correct values for the `dow-msft` model because the appropriate server CPU types are not available in the aws dataset, so the model is falling back to the most common values in each column. Adding new rows to the aws dataset for the given server types will fix this.


## Linting
Code is formatted using Black.

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)



## TODO
- rethink what params are in `common` and which are specific to individual `series`. Update model accordingly
- add neo4j db and api to model
- work out how to deal with time