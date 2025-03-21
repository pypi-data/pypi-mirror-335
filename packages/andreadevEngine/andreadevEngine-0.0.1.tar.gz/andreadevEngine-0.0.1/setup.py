import setuptools
from setuptools import setup, find_packages

setup(
    name="andreadevEngine",
    version="0.0.1",
    url="https://github.com/AndreaMDev/AndreaDev-Phyton-Engine",
    author="Andrea Manzone",
    author_email="andmandev@gmail.com",
    description="Library to use on top of pygame. Uses GameObject and Component workflow",
    packages=setuptools.find_packages(),
    install_requires=[],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
    ],
    include_package_data=True,
    package_data={'': ["Engine Default Assets/*.***"]},
    )
