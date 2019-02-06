import re
from pathlib import Path
from typing import List

import black
from black_nb.cli import DEFAULT_EXCLUDES, DEFAULT_INCLUDES, cli
from click.testing import CliRunner
import pytest

THIS_FILE = Path(__file__)
THIS_DIR = THIS_FILE.parent


def test_basic():
    runner = CliRunner()
    result = runner.invoke(cli, ["."])
    assert result.exit_code == 0


def test_include_exclude():
    path = THIS_DIR / "data" / "include_exclude_tests"
    include = re.compile(r"\.ipynb$")
    exclude = re.compile(r"/exclude/|/\.definitely_exclude/")
    report = black.Report()
    expected = [Path(path / "b/dont_exclude/a.ipynb")]
    this_abs = THIS_DIR.resolve()
    sources = black.gen_python_files_in_dir(
        path, this_abs, include, exclude, report
    )
    assert sorted(expected) == sorted(sources)


def test_empty_include():
    path = THIS_DIR / "data" / "include_exclude_tests"
    report = black.Report()
    empty = re.compile(r"")
    expected = [
        Path(path / "b/exclude/a.p"),
        Path(path / "b/exclude/a.py"),
        Path(path / "b/exclude/a.ipynb"),
        Path(path / "b/dont_exclude/a.p"),
        Path(path / "b/dont_exclude/a.py"),
        Path(path / "b/dont_exclude/a.ipynb"),
        Path(path / "b/.definitely_exclude/a.p"),
        Path(path / "b/.definitely_exclude/a.py"),
        Path(path / "b/.definitely_exclude/a.ipynb"),
    ]
    this_abs = THIS_DIR.resolve()
    sources = black.gen_python_files_in_dir(
        path, this_abs, empty, re.compile(DEFAULT_EXCLUDES), report
    )
    assert sorted(expected) == sorted(sources)


def test_empty_exclude():
    path = THIS_DIR / "data" / "include_exclude_tests"
    report = black.Report()
    empty = re.compile(r"")
    expected = [
        Path(path / "b/dont_exclude/a.ipynb"),
        Path(path / "b/exclude/a.ipynb"),
        Path(path / "b/.definitely_exclude/a.ipynb"),
    ]
    this_abs = THIS_DIR.resolve()
    sources = black.gen_python_files_in_dir(
        path, this_abs, re.compile(DEFAULT_INCLUDES), empty, report
    )
    assert sorted(expected) == sorted(sources)


def test_invalid_include_exclude():
    for option in ["--include", "--exclude"]:
        result = CliRunner().invoke(cli, ["-", option, "**()(!!*)"])
        assert result.exit_code == 2
