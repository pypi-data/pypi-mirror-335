from setuptools import setup, find_packages

setup(
    name="named_ids",
    version="0.1.0",
    packages=find_packages(),
    package_data={
        "named_ids": ["assets/*.txt"],
    },
    description="Human-readable unique identifiers",
    author="Gergely Papp",
    author_email="gergopool@gmail.com",
    url="https://github.com/gergopool/named_ids",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
