
"""Setup module for black-nb."""

from pathlib import Path

from setuptools import setup


def read_long_description() -> str:
    """Read from README.md file in root of source directory."""
    root = Path(__file__).resolve().parent
    readme = root / "README.md"
    return readme.read_text(encoding="utf-8")


setup(
    name="black-nb",
    version="0.0.4",
    description="Apply black to all code cells in a jupyter notebook.",
    long_description=read_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/tomcatling/black-nb",
    author="Tom Catling",
    author_email="tomcatling@gmail.com",
    license="ISC",
    py_modules=["black_nb"],
    entry_points={
        "console_scripts" : [
            "black-nb=black_nb:main"
        ]
    },
    install_requires=["nbformat", "black", "dataclasses"],
)
