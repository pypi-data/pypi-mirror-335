from setuptools import setup, find_packages

setup(
    name="province-district-nepal",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[],
    author="Suman Bhatta",
    author_email="work.suman.dev@gmail.com",
    description="A Python package to fetch districts by province in Nepal",
    url="https://github.com/suman-bhatta/Nepal-Province-Districts-Package",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
