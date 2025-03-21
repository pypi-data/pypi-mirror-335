from setuptools import find_packages, setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="structureddataXX",
    version="0.0.2",
    description="A simple package for math tricks",
    # package_dir={"": "app"},
    packages=find_packages(),
    install_requires=[],  # No external dependencies
    long_description=long_description,
    long_description_content_type="text/markdown",
    # url="https://github.com/ArjanCodes/2023-package",
    author="structured data",
    author_email="structureddatadrive@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    # install_requires=["bson >= 0.5.10"],
    extras_require={
        "dev": ["pytest>=7.0", "twine>=4.0.2"],
    },
    python_requires=">=3.6",
)