# coding: utf-8
from setuptools import setup, find_packages  # noqa: H301
NAME = "cohesity-sdk"
VERSION = "1.4.0"
PYTHON_REQUIRES = ">= 3.8"
REQUIRES = [
    "urllib3 >= 1.25.3, < 3.0.0",
    "python-dateutil >= 2.8.2",
    "pydantic >= 2",
    "typing-extensions >= 4.7.1",
]

setup(
    name=NAME,
    version=VERSION,
    description="This SDK provides operations for interfacing with the Cohesity Cluster.",
    author="Cohesity Inc.",
    author_email="support@cohesity.com",
    url="https://github.com/cohesity/cohesity_sdk",
    install_requires=REQUIRES,
    packages=find_packages(exclude=["test", "tests"]),
    include_package_data=True,
    long_description_content_type='text/markdown',
    long_description="""\
    Cohesity API provides a RESTful interface to access the various data management operations on Cohesity cluster and Helios.
    """,  # noqa: E501
    package_data={"cohesity_sdk.helios": ["py.typed"]},
)