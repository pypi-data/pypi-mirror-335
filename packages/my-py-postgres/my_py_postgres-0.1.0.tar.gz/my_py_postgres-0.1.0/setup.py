from setuptools import setup, find_packages

def read_requirements():
    with open("requirements.txt") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="my-py-postgres",
    version="0.1.0",
    author="Ayman Aamam",
    author_email="aymaneaamam@gmail.com",
    description="PostgreSQL database management system with a user-friendly interface",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Ayman-aa/pypostgres",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "pypostgres=pypostegres.cli:main",
        ],
    },
)