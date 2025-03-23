# --------------------------------------------------------------------------------------------- #
""" 

Setup configuration for the Pyon project.

This file defines the necessary configurations for packaging and distributing the Pyon library,
including dependencies, metadata, and extra requirements for development.

"""
# --------------------------------------------------------------------------------------------- #

from setuptools import setup, find_packages

# --------------------------------------------------------------------------------------------- #

setup(
    name="pyon-core",
    version="0.1.0-alpha",
    description="Python Object Notation: Extended JSON for complex Python types",
    author="Eduardo Rodrigues",
    author_email="ietsira@eonflux.ai",
    url="https://github.com/eonflux-ai/pyon",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.10",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    install_requires=[
        "bitarray>=3.0.0,<4.0",
        "numpy>=2.2.0,<3.0",
        "pandas>=2.2.0,<3.0",
        "python-magic-bin>=0.4.14,<0.5",
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-cov",
            "black",
            "pylint",
        ]
    },
)

# --------------------------------------------------------------------------------------------- #
