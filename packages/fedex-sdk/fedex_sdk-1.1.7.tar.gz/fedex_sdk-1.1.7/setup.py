import setuptools
from setuptools import find_packages

from FedexSDK.__init__ import __version__

setuptools.setup(
    name="fedex-sdk",
    version=__version__,
    author="Esat Yılmaz",
    author_email="esatyilmaz3500@gmail.com",
    description="Fedex Label Create SDK",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    install_requires=[
    ]
)
