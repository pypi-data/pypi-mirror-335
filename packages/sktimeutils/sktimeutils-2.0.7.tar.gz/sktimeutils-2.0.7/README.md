# sktimeutils

[![Documentation Status](https://readthedocs.org/projects/showlib/badge/?version=latest)](https://showlib.readthedocs.io/en/latest/?badge=latest)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/usask-arg/showlib/main.svg)](https://results.pre-commit.ci/latest/github/usask-arg/showlib/main)

This package provides Universal Time conversion functions used by the usask-arg group. The
code tries to be friendly for arrays, sequences and scalars. This package currently supports UT time expressed as strings,
modified julian date as floats, Python DateTime and numpy Datetime64.  The code is focussed on Universal Time and has no provision
for time zone handling or conversion conversions etc.  No attempt is made to manage leap-seconds and other earth rotation issues 
in a fully consistent manner.   

## Installation
    
    pip install sktimeutils

also

    conda install setuptools build
    python -m build --wheel

## Usage
Documentation can be found at https://nick.argpages.usask.ca/skoptics/index.html

## Unit Tests
It is useful to run the unit tests as the tests will automatically download leap-second files and earth rotation 
information. Needless to say you must have an internet connection to successfully run the unit tests 

    python -m unittest discover -s sktimeutils.tests

## License
This project is licensed under the MIT license.




