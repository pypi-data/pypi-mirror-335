from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="sgmap",
    use_scm_version=True,
    author="youyo",
    author_email="1003ni@gmail.com",
    description="AWS Security Group Mapping Tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/youyo/sgmap",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "boto3>=1.20.0",
        "click>=8.0.0",
    ],
    extras_require={
        "dev": [
            "build>=0.7.0",
            "setuptools>=42.0.0",
            "setuptools_scm>=6.2.0",
            "wheel>=0.37.0",
            "twine>=3.4.2",
        ],
    },
    entry_points={
        "console_scripts": [
            "sgmap=sgmap.cli:main",
        ],
    },
)