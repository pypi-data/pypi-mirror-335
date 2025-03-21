from setuptools import setup
from setuptools import find_packages


VERSION = '0.1.2'

setup(
    name='dc.commonlibrary',  # package name
    version=VERSION,  # package version
    description='common library',  # package description
    packages=find_packages(),
    zip_safe=False,
)