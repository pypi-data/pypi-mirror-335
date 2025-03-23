import os
import sys
from setuptools import setup, find_packages

PACKAGE_NAME = "ansible-keepalived-config"

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


def fread(file) -> str:
    with open(file, "r") as f:
        return f.read()


setup(
    name=PACKAGE_NAME,
    version=fread(os.path.join(ROOT_DIR, "VERSION")).strip(),
    long_description=fread(os.path.join(ROOT_DIR, "README.md")).strip(),
    long_description_content_type="text/markdown",
    author="Nils Weyand",
    url=f"https://github.com/Slinred/{PACKAGE_NAME}",
    license=fread(os.path.join(ROOT_DIR, "LICENSE")).strip(),
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "ansible-core",
        "keepalived-config",
    ],
    python_requires=">=3.10",
)
