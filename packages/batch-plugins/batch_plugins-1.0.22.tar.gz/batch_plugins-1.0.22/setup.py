# Keep setup.py to facilitate local package installation in editable mode

from setuptools import setup, find_packages

setup(name="batch_plugins", packages=find_packages())
