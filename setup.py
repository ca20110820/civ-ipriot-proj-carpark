from setuptools import find_packages, setup

setup(
    name="smartpark",
    version="0.1.0",
    description="IP4RIoT - AT3 Project",
    author="Cedric Anover",
    packages=find_packages(),
    install_requires=[
        "paho-mqtt",
        "sense-hat",
        "toml"
    ],
    entry_points={
        "console_scripts": [
            "smartpark = smartpark.main:main",
        ],
    },
    python_requires=">=3.10"
)
