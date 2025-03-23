from setuptools import setup, find_packages
import subprocess
from pathlib import Path
import ast

PACKAGE_ENTRY = 'omnivore_api'
VERSION_FLAG = '__version__'

with open("README.md", "r") as fh:
    long_description = fh.read()


def get_version_from_source() -> str:
    p = Path(__file__).parent / PACKAGE_ENTRY / '__init__.py'

    version_row = None
    with open(str(p), 'r', encoding='utf-8') as f:
        r = f.readline()
        while (r):
            if r.startswith(VERSION_FLAG):
                version_row = r
                break

            r = f.readline()

    _, version = version_row.split('=')
    version = version.strip()
    version = ast.literal_eval(version)
    return version


def get_latest_git_tag():
    try:
        return get_version_from_source()
    except:
        pass
    try:
        version = subprocess.check_output(
            ["git", "describe", "--tags", "--abbrev=0"])
        version = version.strip().decode(
            "utf-8")  # Remove trailing newline and decode bytes to string

        # Remove the 'v' from the tag
        if version.startswith("v"):
            version = version[1:]

        return version
    except Exception as e:
        print(f"An exception occurred while getting the latest git tag: {e}")
        return None


def read_requirements():
    with open("requirements.txt") as f:
        return f.read().splitlines()


VERSION = get_latest_git_tag() or "0.0.1"  # Fallback version

PROJECT_URLS = {
    "Bug Tracker": "https://github.com/Benature/OmnivoreAPI/issues",
    "Source Code": "https://github.com/Benature/OmnivoreAPI",
}

setup(
    name="omnivore_api",
    version=VERSION,
    description="Omnivore API Client for Python",
    author="Benature",
    author_email="",
    packages=find_packages(),
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    keywords="omnivore api readlater graphql gql client",
    platforms="any",
    url="https://github.com/Benature/OmnivoreAPI",
    project_urls=PROJECT_URLS,
    include_package_data=True,
    python_requires=">=3",
    classifiers=[
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    install_requires=read_requirements(),
)
