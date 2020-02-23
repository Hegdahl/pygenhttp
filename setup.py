'''
Installation script.
pip install <this directory>
will use this script to install pygenhttp.
'''
from setuptools import setup, find_packages
from pygenhttp import __version__

setup(
    name="pygenhttp",
    version=__version__,
    packages=find_packages(),
)
