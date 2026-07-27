from setuptools import setup, find_packages

setup(
    name="henry-8x-python",
    version="1.0.0",
    packages=find_packages(),
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "henry8x = henry8x.cli:main",
        ],
    },
)
