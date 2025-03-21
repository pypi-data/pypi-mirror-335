from setuptools import find_packages, setup

setup(
    name="opgg-client", 
    version="0.1.0", 
    author="dwwescalelol", 
    author_email="james.abdallah@gmail.com", 
    description="A Python client for interacting with the OPGG API.",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/dwwescalelol/opgg-client",
    packages=find_packages(exclude=["tests*", "test_data*"]),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    install_requires=[
        "requests>=2.25.1",
        "pydantic>=1.10.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-mock>=3.10.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "opgg-client=main:main",
        ],
    },
)
