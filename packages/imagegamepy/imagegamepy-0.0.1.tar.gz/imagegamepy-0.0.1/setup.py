from setuptools import setup, find_packages
import codecs
import os

VERSION = '0.0.1'
DESCRIPTION = 'A package to create image games and light novels'
LONG_DESCRIPTION = 'A package to create image games and light novels easily'

# Setting up
setup(
    name="imagegamepy",
    version=VERSION,
    author="WinnyCODE (Etchike Hugues Winny Lyonnais)",
    author_email="<winnyblackstart@gmail.com>",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=['PIL', 'pygame', 'numpy'],
    keywords=['python', 'video game', 'Novel', 'game', 'image', 'image game'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
