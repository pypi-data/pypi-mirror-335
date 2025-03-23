from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="PrivyDNS",
    version="0.1.2",
    description="A Python library for secure DNS resolution (DoH, DoT, mTLS) with sync & async support.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Nicholas Adamou",
    author_email="nicholas.adamou@outlook.com",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
