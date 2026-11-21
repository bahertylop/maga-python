"""
Установка пакета car_dealership.

Установка:

    pip install -e .
"""

from setuptools import setup, find_packages


setup(
    name="car-dealership",
    version="1.0.0",
    description="Учебный проект: система учёта автосалона",
    author="Student",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    package_data={"car_dealership.database": ["schema.sql"]},
    python_requires=">=3.9",
    install_requires=[],
    extras_require={
        "test": ["pytest>=7.4.0"],
    },
)
