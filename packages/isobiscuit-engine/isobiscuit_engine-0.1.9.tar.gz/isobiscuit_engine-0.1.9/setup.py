# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': '.'}

packages = \
['isobiscuit_engine']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'isobiscuit-engine',
    'version': '0.1.9',
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
}
from build import *
build(setup_kwargs)

setup(**setup_kwargs)
