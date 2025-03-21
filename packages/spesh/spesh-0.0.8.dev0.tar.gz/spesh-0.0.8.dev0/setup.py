#!/usr/bin/env python3
import os
from setuptools import setup, find_packages

#-----------problematic------
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

import os.path

def readver(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()

def get_version(rel_path):
    for line in readver(rel_path).splitlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")

setup(
    name="spesh",
    description="SPEctra SHow. A tool for gamma and other spectra, uses ROOT, also for online histograms served via HTTP on port 9009",
    author="jaro",
    author_email="jaromrax@gmail.com",
    license="GPL2",
    version=get_version("spesh/version.py"),
    packages=['spesh'],
    package_data={'spesh': ['data/*']},
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    scripts = ['bin/spesh'],
    install_requires = ['fire', 'console', 'datetime'],
)
