from dataclasses import dataclass
from pathlib import Path
import re
from typing import Set, Tuple, Dict, List, Optional

import black
import click
import nbformat

DEFAULT_LINE_LENGTH = 79
DEFAULT_INCLUDES = r"\.ipynb$"
DEFAULT_EXCLUDES = (
    r"/(\.git|\.hg|\.mypy_cache|\.nox|\.tox|\.venv|_build|buck-out|build|dist|\.ipynb_checkpoints)/"
)


@click.command(context_settings=dict(help_option_names=["-h", "--help"]))
@click.option(
    "-l",
    "--line-length",
    type=int,
    default=DEFAULT_LINE_LENGTH,
    help="How many characters per line to allow.",
    show_default=True,
)
@click.option(
    "--check",
    is_flag=True,
    help=(
        "Don't write the files back, just return the status.  Return code 0 "
        "means nothing would change.  Return code 1 means some files would be "
        "reformatted.  Return code 123 means there was an internal error."
    ),
)
@click.option(
    "--include",
    type=str,
    default=DEFAULT_INCLUDES,
    help=(
        "A regular expression that matches files and directories that should be "
        "included on recursive searches.  An empty value means all files are "
        "included regardless of the name.  Use forward slashes for directories on "
        "all platforms (Windows, too).  Exclusions are calculated first, inclusions "
        "later."
    ),
    show_default=True,
)
@click.option(
    "--exclude",
    type=str,
    default=DEFAULT_EXCLUDES,
    help=(
        "A regular expression that matches files and directories that should be "
        "excluded on recursive searches.  An empty value means no paths are excluded. "
        "Use forward slashes for directories on all platforms (Windows, too).  "
        "Exclusions are calculated first, inclusions later."
    ),
    show_default=True,
)
@click.option(
    "--clear-output",
    is_flag=True,
    help="Clear cell output as part of formatting.",
)
@click.argument(
    "src",
    nargs=-1,
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=True,
        readable=True,
        allow_dash=True,
    ),
    is_eager=True,
)
@click.option(
    "--config",
    type=click.Path(
        exists=False, file_okay=True, dir_okay=False, readable=True, allow_dash=False
    ),
    is_eager=True,
    callback=black.read_pyproject_toml,
    help="Read configuration from PATH.",
)
@click.pass_context
def main(
    ctx: click.Context,
    line_length: int,
    check: bool,
    include: str,
    exclude: str,
    clear_output: bool,
    src: Tuple[str],
    config: Optional[str],
) -> None:
    """
    The uncompromising code formatter, for Jupyter notebooks.
    """
    write_back = black.WriteBack.from_configuration(check=check, diff=False)
    mode = black.FileMode.from_configuration(
        py36=True,
        pyi=False,
        skip_string_normalization=False,
        skip_numeric_underscore_normalization=False,
    )

    if config:
        black.out(f"Using configuration from {config}.", bold=False, fg="blue")

    try:
        include_regex = black.re_compile_maybe_verbose(include)
    except re.error:
        black.err(f"Invalid regular expression for include given: {include!r}")
        ctx.exit(2)
    try:
        exclude_regex = black.re_compile_maybe_verbose(exclude)
    except re.error:
        black.err(f"Invalid regular expression for exclude given: {exclude!r}")
        ctx.exit(2)

    report = black.Report(check=check, quiet=False, verbose=False)
    root = black.find_project_root(src)
    sources: Set[Path] = set()
    for s in src:
        p = Path(s)
        if p.is_dir():
            sources.update(
                black.gen_python_files_in_dir(
                    p, root, include_regex, exclude_regex, report
                )
            )
        elif p.is_file() or s == "-":
            # if a file was explicitly given, we don't care about its extension
            sources.add(p)
        else:
            black.err(f"invalid path: {s}")
    if len(sources) == 0:
        black.out("No paths given. Nothing to do.")
        ctx.exit(0)

    for source in sources:
        reformat_one(
            src=source,
            line_length=line_length,
            write_back=write_back,
            mode=mode,
            clear_output=clear_output,
            report=report,
        )

    black.out(f"All done!")
    click.secho(str(report), err=True)
    ctx.exit(report.return_code)


def reformat_one(
    src: Path,
    line_length: int,
    write_back: black.WriteBack,
    mode: black.FileMode,
    clear_output: bool,
    report: black.Report,
) -> None:
    """Reformat a single file under `src`."""
    try:

        sub_report = SubReport(write_back=write_back)
        changed = black.Changed.NO

        cache: black.Cache = {}
        if write_back is not black.WriteBack.DIFF:
            cache = black.read_cache(line_length, mode)
            res_src = src.resolve()
            if res_src in cache and cache[res_src] == black.get_cache_info(
                res_src
            ):
                changed = black.Changed.CACHED
        if changed is not black.Changed.CACHED:
            sub_report = format_file_in_place(
                src,
                line_length=line_length,
                write_back=write_back,
                mode=mode,
                clear_output=clear_output,
                sub_report=sub_report
            )
            if sub_report.change_count:
                changed = black.Changed.YES
        if (
            write_back is black.WriteBack.YES
            and changed is not black.Changed.CACHED
        ) or (
            write_back is black.WriteBack.CHECK and changed is black.Changed.NO
        ):
            black.write_cache(cache, [src], line_length, mode)
        report.done(src, changed)
        if changed is not black.Changed.CACHED:
            click.secho(f"    {sub_report}", err=True)
    except Exception as exc:
        report.failed(src, str(exc))


def format_file_in_place(
    src: Path,
    line_length: int,
    write_back: black.WriteBack,
    mode: black.FileMode,
    clear_output: bool,
    sub_report: "SubReport",
) -> "SubReport":
    """
    Format file under `src` path. Return True if changed.

    If `write_back` is YES, write reformatted code to the file.
    """

    with src.open() as fp:
        src_contents = nbformat.read(fp, as_version=nbformat.NO_CONVERT)

    dst_cells: List[Dict] = []
    for cell in src_contents["cells"]:
        if cell["cell_type"] == "code":
            try:
                cell["source"] = format_cell_source(
                    cell["source"], line_length=line_length, mode=mode
                )
                sub_report.done(black.Changed.YES)
            except black.NothingChanged:
                sub_report.done(black.Changed.NO)
            except black.InvalidInput:
                sub_report.failed()
            if clear_output:
                try:
                    cell["outputs"], cell["execution_count"] = clear_cell_outputs(
                        cell["outputs"], cell["execution_count"]
                    )
                    sub_report.done_output(black.Changed.YES)
                except black.NothingChanged:
                    sub_report.done_output(black.Changed.NO)
        dst_cells.append(cell)
    src_contents["cells"] = dst_cells

    # click.echo(src)
    # click.secho(f"    {sub_report}", err=True)

    if write_back is black.WriteBack.YES:
        with src.open("w") as fp:
            nbformat.write(src_contents, fp)

    return sub_report


def clear_cell_outputs(src_outputs: List[str], src_execution_count: int) -> Tuple[List[str], None]:
    if src_outputs == [] and src_execution_count is None:
        raise black.NothingChanged
    return [], None


def format_cell_source(
    src_contents: str, *, line_length: int, mode: black.FileMode
) -> black.FileContent:
    """Reformat contents of cell and return new contents.

    Additionally confirm that the reformatted code is valid by calling
    :func:`assert_equivalent` and :func:`assert_stable` on it.
    `line_length` is passed to :func:`format_str`.
    """

    if src_contents.strip() == "":
        raise black.NothingChanged

    dst_contents = format_str(
        src_contents, line_length=line_length, mode=mode
    )

    if src_contents == dst_contents:
        raise black.NothingChanged

    assert_equivalent(src_contents, dst_contents)
    assert_stable(
        dst_contents, line_length=line_length, mode=mode
    )

    return dst_contents


def format_str(
    src_contents: str, line_length: int, *, mode: black.FileMode = black.FileMode.AUTO_DETECT
) -> black.FileContent:
    trailing_semi_colon = src_contents.rstrip()[-1] == ";"
    src_contents = hide_magic(src_contents)
    dst_contents = black.format_str(src_contents, line_length=line_length, mode=mode)
    dst_contents = dst_contents.rstrip()
    if trailing_semi_colon:
        dst_contents = f"{dst_contents};"
    dst_contents = reveal_magic(dst_contents)
    return dst_contents


def assert_equivalent(src: str, dst: str) -> None:
    black.assert_equivalent(hide_magic(src), hide_magic(dst))


def assert_stable(
    dst: str, line_length: int, mode: black.FileMode = black.FileMode.AUTO_DETECT
) -> None:
    new_dst = format_str(dst, line_length=line_length, mode=mode)
    if dst != new_dst:
        raise AssertionError(
            "INTERNAL ERROR: Black produced different code on the second pass "
            "of the formatter."
        ) from None


def contains_magic(line: str) -> bool:
    if len(line) == 0:
        return False
    else:
        return line[0] == "%" or line[0] == "!"


def hide_magic(source: str) -> str:
    """
    Black can't deal with cell or line magic, so we
    disguise it as a comment. This keeps it in the same
    place in the reformatted code.
    """

    def _hide_magic_line(line: str) -> str:
        return f"###MAGIC###{line}" if contains_magic(line) else line

    return "\n".join(_hide_magic_line(l) for l in source.split("\n"))


def reveal_magic(source: str) -> str:
    """
    Reveal any notebook magic hidden by hide_magic().
    """
    return source.replace("###MAGIC###", "")


@dataclass
class SubReport:
    """
    Provides a reformatting counter for notebook cells.

    Can be rendered with `str(report)`.
    """

    write_back: black.WriteBack
    change_count: int = 0
    same_count: int = 0
    failure_count: int = 0
    output_change_count: int = 0
    output_same_count: int = 0

    def done(self, changed: black.Changed) -> None:
        """
        Increment the counter for successful reformatting.
        """
        if changed is black.Changed.YES:
            self.change_count += 1
        else:
            self.same_count += 1

    def done_output(self, changed: black.Changed) -> None:
        """
        Increment the counter for successful clear output.
        """
        if changed is black.Changed.YES:
            self.output_change_count += 1
        else:
            self.output_same_count += 1

    def failed(self) -> None:
        """
        Increment the counter for failed reformatting.
        """
        self.failure_count += 1

    def __str__(self) -> str:
        """
        Render a report of the current state.
        """
        if self.write_back is black.WriteBack.CHECK:
            reformatted = "would be reformatted"
            unchanged = "would be left unchanged"
            failed = "would fail to reformat"
            cleared = "would be cleared"
        else:
            reformatted = "reformatted"
            unchanged = "left unchanged"
            failed = "failed to reformat"
            cleared = "cleared"
        report = []
        if self.change_count:
            s = "s" if self.change_count > 1 else ""
            report.append(
                click.style(
                    f"{self.change_count} cell{s} {reformatted}", bold=True
                )
            )
        if self.same_count:
            s = "s" if self.same_count > 1 else ""
            report.append(f"{self.same_count} cell{s} {unchanged}")
        if self.failure_count:
            s = "s" if self.failure_count > 1 else ""
            report.append(
                click.style(f"{self.failure_count} cell{s} {failed}", fg="red")
            )
        if self.output_change_count:
            s = "s" if self.change_count > 1 else ""
            report.append(
                click.style(
                    f"{self.change_count} output{s} {cleared}", bold=True
                )
            )
        if self.output_same_count:
            s = "s" if self.same_count > 1 else ""
            report.append(f"{self.same_count} output{s} {unchanged}")
        return ", ".join(report) + "."


if __name__ == "__main__":
    main()
