from setuptools import setup, find_packages

setup(
    name="lukhed_markets",
    version="0.1.2",
    description="A collection of broad market analysis functions and api wrappers",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="lukhed",
    author_email="lukhed.mail@gmail.com",
    url="https://github.com/lukhed/lukhed_markets",
    packages=find_packages(),
    include_package_data=True,  # Ensures MANIFEST.in is used
    python_requires=">=3.10",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "lukhed-basic-utils>=1.4.6"
    ],
)