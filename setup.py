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
    license="ISC",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Operating System :: Unix",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: ISC License (ISCL)",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    packages=find_packages(),
    use_scm_version={"version_scheme": "post-release"},
    setup_requires=["setuptools_scm"],
    python_requires='>3.6',
    install_requires=[
        "attrs", "black==18.9b0", "click", "nbformat"
    ],
    entry_points={"console_scripts": ["black-nb=black_nb.cli:cli"]},
)