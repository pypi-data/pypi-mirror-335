from setuptools import setup, find_packages

with open("../../../README.md", "r", encoding="utf-8") as f:
    description = f.read()

setup(
    name="yinyang_base64",
    version="0.0.1",
    packages=find_packages(),
    install_requires=[],
    long_description=description,
    long_description_content_type="text/markdown"
)