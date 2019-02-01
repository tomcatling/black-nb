from dataclasses import dataclass, field
from pathlib import Path
from typing import Set, Tuple, Dict, List

import black
import click
import nbformat
from appdirs import user_cache_dir

__version__ = "0.0.1"
DEFAULT_LINE_LENGTH = 79
DEFAULT_INCLUDES = r"\.ipynb$"
CACHE_DIR = Path(user_cache_dir("black", version=__version__))


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
@click.pass_context
def main(
    ctx: click.Context,
    line_length: int,
    check: bool,
    clear_output,
    src: Tuple[str],
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

    include_regex = black.re_compile_maybe_verbose(DEFAULT_INCLUDES)
    exclude_regex = black.re_compile_maybe_verbose(black.DEFAULT_EXCLUDES)

    report = black.Report(check=check, quiet=False, verbose=True)
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
    report: "Report",
) -> None:
    """Reformat a single file under `src`."""
    try:
        changed = black.Changed.NO

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
    except Exception as exc:
        report.failed(src, str(exc))


def format_file_in_place(
    src: Path,
    line_length: int,
    write_back: black.WriteBack,
    mode: black.FileMode,
    clear_output: bool,
) -> "SubReport":
    """
    Format file under `src` path. Return True if changed.

    If `write_back` is YES, write reformatted code to the file.
    """
    # TODO: Set check properly
    check = True if mode is black.WriteBack.CHECK else False
    sub_report = SubReport(check=check)

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
                # TODO: Log this
                cell["execution_count"] = None
                cell["outputs"] = []
        dst_cells.append(cell)
    src_contents["cells"] = dst_cells

    click.echo(src)
    click.secho(f"    {sub_report}", err=True)

    if write_back == write_back.YES:
        with src.open("w") as fp:
            nbformat.write(src_contents, fp)

    return sub_report


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

    # src_contents = _hide_magic(src_contents)

    dst_contents = black.format_str(
        src_contents, line_length=line_length, mode=mode
    )

    if src_contents == dst_contents:
        raise black.NothingChanged

    black.assert_equivalent(src_contents, dst_contents)
    black.assert_stable(
        src_contents, dst_contents, line_length=line_length, mode=mode
    )

    # dst_contents = _reveal_magic(dst_contents)

    return dst_contents


def _contains_magic(line: str) -> bool:
    if len(line) == 0:
        return False
    else:
        return line[0] == "%" or line[0] == "!"


def _hide_magic(source: str) -> str:
    """
    Black can't deal with cell or line magic, so we
    disguise it as a comment. This keeps it in the same
    place in the reformatted code.
    """

    def _hide_magic_line(line: str) -> str:
        return f"###MAGIC###{line}" if _contains_magic(line) else line

    return "\n".join(_hide_magic_line(l) for l in source.splitlines())


def _reveal_magic(source: str) -> str:
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
    check: bool = False
    change_count: int = 0
    same_count: int = 0
    failure_count: int = 0

    def done(self, changed: black.Changed) -> None:
        """
        Increment the counter for successful reformatting.
        """
        if changed is black.Changed.YES:
            self.change_count += 1
        else:
            self.same_count += 1

    def failed(self) -> None:
        """
        Increment the counter for failed reformatting.
        """
        self.failure_count += 1

    def __str__(self) -> str:
        """
        Render a report of the current state.
        """
        if self.check:
            reformatted = "would be reformatted"
            unchanged = "would be left unchanged"
            failed = "would fail to reformat"
        else:
            reformatted = "reformatted"
            unchanged = "left unchanged"
            failed = "failed to reformat"
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
        return ", ".join(report) + "."


if __name__ == "__main__":
    main()
