from setuptools import setup, find_packages 

setup(
    author = "Veli Ristimaki",
    description = "a basic package to interface with the Steam API.",
    name = "steam_api_pkg",
    version = "0.1.0",
    packages = find_packages(include=["steam_api_pkg","steam_api_pkg.*"]),
    install_requires = ["requests"],
    python_requires = '>=3.8',

    license="MIT",
    license_files=["LICENSE"],
    
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)