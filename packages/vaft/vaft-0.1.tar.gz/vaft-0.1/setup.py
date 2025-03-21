from setuptools import setup, find_packages

setup(
    name="vaft",
    version="0.1",
    packages=find_packages(),
    description="Versatile Analytical Framework for Tokamak",
    author="satelite2517, Hikitonic",
    author_email="satelite2517@snu.ac.kr, peppertonic18@snu.ac.kr",
    url="https://github.com/VEST-Tokamak/vaft",
    install_requires=[
        "h5py",
        "numpy",
        "uncertainties",
        "omas",
        "matplotlib",
    ],
    extras_require={
        "dev": [
            "pytest",
            "black",
            "flake8",
        ],
    },
)