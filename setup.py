
"""Setup module for nb-filter-cells."""

from pathlib import Path

from setuptools import setup


def read_long_description() -> str:
    """Read from README.md file in root of source directory."""
    root = Path(__file__).resolve().parent
    readme = root / "README.md"
    return readme.read_text(encoding="utf-8")


setup(
    name="nb-filter-cells",
    version="0.0.1",
    description="Filter Jupyter notebook cells by tag",
    long_description=read_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/liamcoatman/nb-filter-cells",
    author="Liam Coatman",
    author_email="liam.coatman@gmail.com",
    license="ISC",
    scripts=["nb-filter-cells"],
    install_requires=["nbformat"],
)
