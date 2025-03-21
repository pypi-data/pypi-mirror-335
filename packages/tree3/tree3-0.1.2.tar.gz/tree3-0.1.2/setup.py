from setuptools import setup, find_packages

setup(
    name="tree3",
    version="0.1.2",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "tree3=tree3.cli:main",
        ],
    },
)
