# setup.py
import io
import os
from setuptools import setup, find_packages
# these things are needed for the README.md show on pypi (if you dont need delete it)
here = os.path.abspath(os.path.dirname(__file__))
# Import the README and use it as the long-description.
DESCRIPTION = 'Hi-Compass: A human hg38 cell-type specific Hi-C(10k for now) predict deep learning model'
try:
    with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = '\\n' + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION
# Package meta-data.
NAME = 'hicompass'

EMAIL = '2247143021@qq.com'
URL="https://github.com/EndeavourSyc/Hi-Compass/"
AUTHOR = 'Yuanchen Sun'
VERSION = '0.1.7'
setup(
name=NAME,
version=VERSION,
author=AUTHOR,
author_email=EMAIL,
license='MIT',
description=DESCRIPTION,
url=URL,
long_description_content_type="text/markdown",
long_description=long_description,
packages=find_packages(),
install_requires=["numpy",
"pandas", "scikit-image", "pyBigWig", "cooler", ],   # PyTorch is not included as it needs to be installed manually according to the system configuration
classifiers=[
'Programming Language :: Python',
"Programming Language :: Python :: 3",
"License :: OSI Approved :: MIT License",
"Operating System :: OS Independent",],
python_requires=">=3.8",
    entry_points={"console_scripts": ["hicompass=hicompass.cli:main",],}
)