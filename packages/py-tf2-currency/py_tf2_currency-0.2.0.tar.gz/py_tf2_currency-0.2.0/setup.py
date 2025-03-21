from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="py_tf2_currency",
    version="0.2.0",
    packages=find_packages(),
    install_requires=[],
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Sachin/Derpy",
)
