"""Setup script for the shardcast package."""

from setuptools import setup, find_packages

setup(
    name="shardcast",
    version="0.1.0",
    description="A package for distributing large files via HTTP",
    author="felix",
    packages=find_packages(),
    classifiers=[],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "shardcast-origin=shardcast.origin_server:main",
            "shardcast-middle=shardcast.middle_node:main",
            "shardcast-client=shardcast.client_node:main",
        ],
    },
)
