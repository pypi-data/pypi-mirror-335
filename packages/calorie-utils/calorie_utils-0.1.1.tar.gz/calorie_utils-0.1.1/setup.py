import os
from setuptools import setup, find_packages

setup(
    name="calorie_utils",
    version="0.1.1",
    author="Your Name",
    author_email="your_email@example.com",
    description="A Python library for fetching calorie and macronutrient data from USDA FoodData Central.",
    long_description=open("README.md").read() if os.path.exists("README.md") else "",
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/calorie_utils",
    packages=find_packages(),
    install_requires=[
        "requests"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
