import os
from setuptools import setup, find_packages


setup(
    name='heart_disease_example',
    packages=find_packages(),
    install_requires=['veritable'],
    package_data={'': ['*.json']}
    )
