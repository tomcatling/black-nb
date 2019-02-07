import re
import shutil
from pathlib import Path

import black
import pytest
from click.testing import CliRunner

from black_nb.cli import DEFAULT_EXCLUDES, DEFAULT_INCLUDES, cli

THIS_FILE = Path(__file__)
THIS_DIR = THIS_FILE.parent


def test_formatting(tmp_path):
    src_dir = THIS_DIR / "data" / "formatting_tests"
    dst_dir = tmp_path / "formatting_tests"
    shutil.copytree(src_dir, dst_dir)

    unformatted = CliRunner().invoke(cli, ["--check", str(dst_dir)])
    assert unformatted.exit_code == 1

    formatting = CliRunner().invoke(cli, [str(dst_dir)])
    assert formatting.exit_code == 0

    formatted = CliRunner().invoke(cli, ["--check", str(dst_dir)])
    assert formatted.exit_code == 0


def test_clear_output(tmp_path):
    src_dir = THIS_DIR / "data" / "clear_output_tests"
    dst_dir = tmp_path / "clear_output_tests"
    shutil.copytree(src_dir, dst_dir)

    uncleared = CliRunner().invoke(
        cli, ["--check", "--clear-output", str(dst_dir)]
    )
    assert uncleared.exit_code == 1

    clearing = CliRunner().invoke(cli, ["--clear-output", str(dst_dir)])
    assert clearing.exit_code == 0

    cleared = CliRunner().invoke(
        cli, ["--check", "--clear-output", str(dst_dir)]
    )
    assert cleared.exit_code == 0


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


@pytest.mark.parametrize("option", ["--include", "--exclude"])
def test_invalid_include_exclude(option):
    result = CliRunner().invoke(cli, [option, "**()(!!*)"])
    assert result.exit_code == 2
