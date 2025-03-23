from setuptools import setup, find_packages

setup(
    name="publiccomps",
    version="0.0.1",
    author="Jon Ma",
    author_email="jon@publiccomps.com",
    description="Official SDK for accessing Public Comps data",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://publiccomps.com",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
