# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': '.'}

packages = \
['isobiscuit_engine']

package_data = \
{'': ['*']}

install_requires = \
['cython>=0.29.37,<0.30.0']

setup_kwargs = {
    'name': 'isobiscuit-engine',
    'version': '0.1.10',
    'description': '',
    'long_description': '# IsoBiscuit Engine\nThis is an isobiscuit engine in cython for performance optimisation',
    'author': 'trollmii',
    'author_email': 'trollmii@outlook.de',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}
from build import *
build(setup_kwargs)

setup(**setup_kwargs)
