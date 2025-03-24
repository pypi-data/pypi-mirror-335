from setuptools import setup, find_packages

setup(
    name="image_resizer_lib",
    version="1.0.0",
    description="A simple Python library to resize images with CLI support.",
    author="Harshith Chandra",
    packages=find_packages(),
    install_requires=[
        "Pillow",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)