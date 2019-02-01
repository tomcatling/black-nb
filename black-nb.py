from pathlib import Path
import pickle
from typing import Any, Set, Tuple, Iterable

from appdirs import user_cache_dir
import black
import click
import nbformat


__version__ = "0.0.1"
DEFAULT_LINE_LENGTH = 79
DEFAULT_INCLUDES = r"\.ipynb$"
CACHE_DIR = Path(user_cache_dir("black", version=__version__))


@click.command(context_settings=dict(help_option_names=["-h", "--help"]))
@click.option(
    "--check",
    is_flag=True,
    help=(
        "Don't write the files back, just return the status.  Return code 0 "
        "means nothing would change.  Return code 1 means some files would be "
        "reformatted.  Return code 123 means there was an internal error."
    ),
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
def main(ctx: click.Context, check: bool, src: Tuple[str]) -> None:
    """
    The uncompromising code formatter, for Jupyter notebooks.
    """

    if check:
        write_back = black.WriteBack.CHECK
    else:
        write_back = black.WriteBack.YES

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
        black.out("No paths given. Nothing to do 😴")
        ctx.exit(0)

    for source in sources:
        reformat_one(
            src=source,
            write_back=write_back,
            report=report,
        )

    bang = "💥 💔 💥" if report.return_code else "✨ 🍰 ✨"
    black.out(f"All done! {bang}")
    click.secho(str(report), err=True)
    ctx.exit(report.return_code)


def reformat_one(
    src: Path,
    write_back: black.WriteBack,
    report: black.Report,
) -> None:
    """Reformat a single file under `src` without spawning child processes.

    If `quiet` is True, non-error messages are not output. `line_length`,
    `write_back`, `fast` and `pyi` options are passed to
    :func:`format_file_in_place` or :func:`format_stdin_to_stdout`.
    """
    try:
        changed = black.Changed.NO

        cache = read_cache()
        res_src = src.resolve()
        if res_src in cache and cache[res_src] == black.get_cache_info(res_src):
            changed = black.Changed.CACHED
        if changed is not black.Changed.CACHED and format_file_in_place(
            src,
            write_back=write_back,
        ):
            changed = black.Changed.YES
        if (changed is not black.Changed.CACHED) or (write_back is black.WriteBack.CHECK and changed is black.Changed.NO):
            black.write_cache(cache, [src], line_length, mode)
        report.done(src, changed)
    except Exception as exc:
        report.failed(src, str(exc))


def read_cache() -> black.Cache:
    """Read the cache if it exists and is well formed.

    If it is not well formed, the call to write_cache later should resolve the issue.
    """
    cache_file = CACHE_DIR / "cache.pickle"
    if not cache_file.exists():
        return {}

    with cache_file.open("rb") as fp:
        try:
            cache: black.Cache = pickle.load(fp)
        except pickle.UnpicklingError:
            return {}

    return cache


def write_cache(cache: black.Cache, sources: Iterable[Path]) -> None:
    """Update the cache file."""
    cache_file = CACHE_DIR / "cache.pickle"
    try:
        if not CACHE_DIR.exists():
            CACHE_DIR.mkdir(parents=True)
        new_cache = {**cache, **{src.resolve(): black.get_cache_info(src) for src in sources}}
        with cache_file.open("wb") as fp:
            pickle.dump(new_cache, fp, protocol=pickle.HIGHEST_PROTOCOL)
    except OSError:
        pass


def format_file_in_place(
    src: Path,
    write_back: black.WriteBack = black.WriteBack.NO,
) -> bool:
    """Format file under `src` path. Return True if changed.

    If `write_back` is DIFF, write a diff to stdout. If it is YES, write reformatted
    code to the file.
    `line_length` and `fast` options are passed to :func:`format_file_contents`.
    """

    src_contents = nbformat.read(src, as_version=nbformat.NO_CONVERT)

    cells = [
        cell for cell in src_contents["cells"]
        if cell["cell_type"] == "code"
    ]

    try:
        dst_contents = format_code_cells(cells)
    except black.NothingChanged:
        return False

    if write_back == write_back.YES:
        nbformat.write(dst_contents, src)

    return True




if __name__ == "__main__":
    main()
