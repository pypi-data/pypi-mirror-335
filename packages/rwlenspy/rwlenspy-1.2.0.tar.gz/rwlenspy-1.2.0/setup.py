# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['rwlenspy']

package_data = \
{'': ['*']}

install_requires = \
['Cython>=0.29.33',
 'astropy>=6.0.0',
 'matplotlib>=3.8.2',
 'numpy>=1.21.0',
 'scipy>=1.7.0',
 'setuptools>=66.1.1']

setup_kwargs = {
    'name': 'rwlenspy',
    'version': '1.2.0',
    'description': 'Lensing simulation from Fermat Potenials',
    'long_description': '# RWLensPy\n\nThis is a python package that generates observed morphologies and propagation transfer functions for radio wave propgation recorded by a radio telescope.\n\nThe code can be installed with:\n\n`pip install rwlenspy`\n\n## Examples\n\nFor examples see `examples/`. The image ray trace is shown in the `example_animate_*.py` files and how to get the coherent transfer function for a baseband simulation is shown in `example_transfer*.py`.\n\n<img src="./examples/plots/singelens_spatial_freqslice.gif" width=42%>    <img src="./examples/plots/singlelens_baseband_spatial_arrival.gif" width=42%>\n\n## Custom/Dev Install\n\nThe package is built with Poetry and Cython using C++11 and OpenMP. This requires having a compiler like `gcc` if one is editing the code. If one requires a dev install, this can be done with:\n\n`poetry install --with test,dev`\n\n`poetry run python`\n\nOnce installed, tests can be run with:\n\n`poetry run pytest`\n',
    'author': 'Zarif Kader',
    'author_email': 'kader.zarif@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9',
}
from build import *
build(setup_kwargs)

setup(**setup_kwargs)
