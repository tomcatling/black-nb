<h1 align="center">The uncompromising code formatter, for Jupyter notebooks</h2>

<p align="center">
<img alt="Build Status" src="https://github.com/tomcatling/black-nb/workflows/Python%20application/badge.svg"></a>
<a href="https://github.com/ambv/black"><img alt="Code Style" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
<a href="https://pepy.tech/project/black-nb"><img alt="Code Style" src="https://pepy.tech/badge/black-nb"></a>
</p>

*black-nb* applies [*black*](https://github.com/ambv/black) to Jupyter notebooks.

Much of the code is taken from the original *black* project and the behaviour is intentionally similar.

## Installation

`pip install black-nb`

## Usage

To apply *black* to all code cells in notebooks under the current directory:

```bash
black-nb .
```
To clear cell outputs in addition to reformatting:

```bash
black-nb --clear-output .
```

To check if notebooks pass *black* and additionally have no output (files will be unchanged):

```bash
black-nb --clear-output --check .
```

To reformat all `*.ipynb` files below `./`, excluding paths matching `*/outputs/*` or `*/.ipynb_checkpoints/*`:

```bash
black-nb --exclude '/(outputs|\.ipynb_checkpoints)/' .
```

## Command Line Options

*black-nb* doesn't provide many options.  You can list them by running `black-nb --help`:

```text
Usage: black-nb [OPTIONS] [SRC]...

  The uncompromising code formatter, for Jupyter notebooks.

Options:
  -l, --line-length INTEGER  How many characters per line to allow.  [default:
                             88]
  --check                    Don't write the files back, just return the
                             status.  Return code 0 means nothing would
                             change.  Return code 1 means some files would be
                             reformatted.  Return code 123 means there was an
                             internal error.
  --include TEXT             A regular expression that matches files and
                             directories that should be included on recursive
                             searches.  An empty value means all files are
                             included regardless of the name.  Use forward
                             slashes for directories on all platforms
                             (Windows, too).  Exclusions are calculated first,
                             inclusions later.  [default: \.ipynb$]
  --exclude TEXT             A regular expression that matches files and
                             directories that should be excluded on recursive
                             searches. An empty value means no paths are
                             excluded. Use forward slashes for directories on
                             all platforms (Windows, too). Exclusions are
                             calculated first, inclusions later.  [default: /(
                             \.git|\.hg|\.mypy_cache|\.nox|\.tox|\.venv|_build
                             |buck-out|build|dist|\.ipynb_checkpoints)/]
  --extend-exclude  TEXT     Like --exclude, but adds additional files and
                             directories on top of the excluded ones.
                             (Useful if you simply want to add to the default)
  --force-exclude   TEXT     Like --exclude, but files and directories matching
                             this regex will be excluded even when they are
                             passed explicitly as arguments.
  --stdin-filename  TEXT     The name of the file when passing it through stdin.
                             Useful to make sure Black will respect --force-exclude
                             option on some editors that rely on using stdin.
  -q, --quiet                Don't emit non-error messages to stderr. Errors
                             are still emitted, silence those with
                             2>/dev/null.
  -v, --verbose              Also emit messages to stderr about files that
                             were not changed or were ignored due to
                             --exclude=.
  --clear-output             Clear cell output as part of formatting.
  --config FILE              Read configuration from PATH.
  -h, --help                 Show this message and exit.
```

## Copyright

Copyright © 2019 Tom Catling, Liam Coatman.

`black-nb` is distributed under the terms of the [MIT licence].

[mit licence]: https://opensource.org/licenses/MIT
