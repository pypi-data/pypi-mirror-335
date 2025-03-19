import setuptools
from setuptools import find_packages

setuptools.setup(
    name="qnb-invoice-helper",
    version="1.1.2",
    author="Esat Yılmaz",
    author_email="esatyilmaz3500@gmail.com",
    description="QNB Invoice Creator",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
    install_requires=[
        "pydantic", "requests", "zeep"
    ]
)
