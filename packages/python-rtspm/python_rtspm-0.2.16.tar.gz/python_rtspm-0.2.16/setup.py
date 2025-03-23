# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['rtspm']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.19.2', 'scipy>=1.5.4']

setup_kwargs = {
    'name': 'python-rtspm',
    'version': '0.2.16',
    'description': 'Python adaptation of SPM functions for real-time fMRI analysis',
    'long_description': '# python-rtspm\n\n[![PyPI version](https://img.shields.io/pypi/v/python-rtspm.svg)](https://pypi.python.org/pypi/python-rtspm)\n[![Supported Python versions](https://img.shields.io/pypi/pyversions/python-rtspm.svg)](https://pypi.org/project/python-rtspm/#files)\n[![Build and Publish](https://github.com/OpenNFT/python-rtspm/workflows/Build%20and%20Publish/badge.svg)](https://github.com/OpenNFT/python-rtspm/actions/workflows/build-publish.yaml)\n[![License](https://img.shields.io/pypi/l/python-rtspm.svg)](https://choosealicense.com/licenses/gpl-3.0)\n\nPython adaptation of SPM functions for real-time fMRI analysis\n\n## Installing\n\nPython 3.11 or above is supported.\n\n```\npip install python-rtspm\n```\n',
    'author': 'OpenNFT Team',
    'author_email': 'opennft@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.11,<4.0',
}
from buildext import *
build(setup_kwargs)

setup(**setup_kwargs)
