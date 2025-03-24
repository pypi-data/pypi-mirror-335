from setuptools import setup, find_packages

with open("./README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="yinyang_base64",
    version="1.0.1",
    license="MIT",
    url="https://github.com/Lionel-Kyo/YinYangBase64",
    python_requires=">= 3.9", # typing support
    packages=find_packages(),
    install_requires=[],
    description="Base64 but Kanji (Yinyang) characters.",
    long_description=long_description,
    long_description_content_type="text/markdown"
)