from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="essential_building_blocks",
    version="1.0.1",
    packages=find_packages(exclude=["tests"]),
    install_requires=[],
    url="https://github.com/TheAdaptoid/Building-Blocks",
    author="Marion Forrest",
    author_email="111011653+TheAdaptoid@users.noreply.github.com",
    description="A Python package of common functions, classes, and data structures.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
