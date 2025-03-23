# hash-drbg
SP800-90A Hash DRBG



| | |
| --- | --- |
| CI/CD | [![CI - Test](https://github.com/sebastien-riou/hash-drbg/actions/workflows/test.yml/badge.svg)](https://github.com/sebastien-riou/hash-drbg/actions/workflows/test.yml) [![CD - Build](https://github.com/sebastien-riou/hash-drbg/actions/workflows/build.yml/badge.svg)](https://github.com/sebastien-riou/hash-drbg/actions/workflows/build.yml) [![Documentation Status](https://readthedocs.org/projects/hdrbg/badge/?version=latest)](https://hdrbg.readthedocs.io/en/latest/?badge=latest)|
| Package | [![PyPI - Version](https://img.shields.io/pypi/v/hdrbg.svg?logo=pypi&label=PyPI&logoColor=gold)](https://pypi.org/project/hdrbg/) [![PyPI - Python Version](https://img.shields.io/pypi/pyversions/hdrbg.svg?logo=python&label=Python&logoColor=gold)](https://pypi.org/project/hdrbg/) |
| Meta | [![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch)  [![linting - Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v0.json)](https://github.com/charliermarsh/ruff) [![code style - Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)  [![License - apache-2.0](https://img.shields.io/badge/license-apache--2.0-blue)](https://spdx.org/licenses/) |


Pure python implementation of NIST SP800-90A Hash DRBG.


## Installation

    python3 -m pip install hdrbg


## Test with `pytest`

    pytest-3

## Test without `pytest`
Tests can run without creating/installing the package:

    python3 -m test.test


you can also run each test separately:

    python3 -m test.test_cavp


    
## Build the package
Build is done using `hatchling`. The script `build` allows to build for different version of python3:

    ./build python3.10


## Create a new version
Version is managed by `hatch-vcs`, you just need to create a tag in github. 

## Launch linters
They use the configuration from `pyproject.toml`

    ./lint
