from pathlib import Path

from setuptools import setup, find_packages


def read_long_description() -> str:
    """Read from README.md file in root of source directory."""
    root = Path(__file__).resolve().parent
    readme = root / "README.md"
    return readme.read_text(encoding="utf-8")


setup(
    name="black-nb",
    description="Apply black to all code cells in a Jupyter notebook.",
    long_description=read_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/tomcatling/black-nb",
    author="Tom Catling",
    author_email="tomcatling@gmail.com",
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Operating System :: Unix",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    packages=find_packages(),
    use_scm_version={"version_scheme": "post-release"},
    setup_requires=["setuptools_scm"],
    python_requires=">3.6",
    install_requires=[
        "attrs>=18.2.0",
        "black>=21.4b0",
        "click>=7.0",
        "nbformat>=4.4.0",
    ],
    entry_points={"console_scripts": ["black-nb=black_nb.cli:cli"]},
)
