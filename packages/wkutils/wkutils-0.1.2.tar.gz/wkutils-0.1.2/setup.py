from setuptools import setup, find_packages
import codecs
import os

VERSION = '0.1.2'
DESCRIPTION = 'Useful utilities for python'
LONG_DESCRIPTION = 'A package that contains a bunch of useful utilities I have collected over the years'

# Setting up
setup(
    name="wkutils",
    version=VERSION,
    author="Werner Kruger",
    author_email="<python@wkruger.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=['numpy_financial'],
    keywords=['python', 'utilities', 'financial', 'calculator'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)

