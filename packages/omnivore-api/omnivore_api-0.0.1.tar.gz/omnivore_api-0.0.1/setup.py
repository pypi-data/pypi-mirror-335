from setuptools import setup, find_packages
import subprocess


def get_latest_git_tag():
    try:
        import omnivore_api
        return omnivore_api.__version__
    except Exception as e:
        print(f"An exception occurred while getting the latest git tag: {e}")
        return None


def read_requirements():
    with open("requirements.txt") as f:
        return f.read().splitlines()


VERSION = get_latest_git_tag() or "0.0.1"  # Fallback version

PROJECT_URLS = {
    "Bug Tracker": "https://github.com/yazdipour/OmnivoreQL/issues",
    "Source Code": "https://github.com/yazdipour/OmnivoreQL",
}

setup(
    name="omnivore_api",
    version=VERSION,
    description="Omnivore API Client for Python",
    author="Benature",
    author_email="",
    packages=find_packages(),
    long_description=open("README.md").read(),
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
