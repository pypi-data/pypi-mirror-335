from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="harness-ar-python",
    version="1.0.0",
    author="Arvind Choudary",
    author_email="arvind.choudary@harness.io",
    description="Harness AR Python Package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/harness/harness-ar-python",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
