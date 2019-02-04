<h1 align="center">black-nb :notebook: </h2>

<p align="center">
<a href="https://travis-ci.com/tomcatling/black-nb"><img alt="Build Status" src="https://travis-ci.com/tomcatling/black-nb.svg?branch=master"></a>
<a href="https://codecov.io/github/tomcatling/black-nb?branch=master"><img alt="Code Coverage" src="https://codecov.io/github/tomcatling/black-nb/coverage.svg?branch=master"></a>
<a href="https://github.com/ambv/black"><img alt="Code Style" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
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

To reformat everything below `./` excluding `./outputs/*` and `*.ipynb_checkpoints/*` :

```bash
black-nb --exclude /(outputs|\.ipynb_checkpoints)/ .
```

## Command Line Options

*black-nb* doesn't provide many options.  You can list them by running `black-nb --help`:

```text
black-nb [OPTIONS] [SRC]...

Options:
  -l, --line-length INTEGER   Where to wrap around.  [default: 88]
                              
  --check                     Don't write the files back, just return the
                              status.  Return code 0 means nothing would
                              change.  Return code 1 means some files would be
                              reformatted.  Return code 123 means there was an
                              internal error.
                              
  --include TEXT              A regular expression that matches files and
                              directories that should be included on
                              recursive searches. On Windows, use forward
                              slashes for directories.  [default: \.ipynb$]
                              
  --exclude TEXT              A regular expression that matches files and
                              directories that should be excluded on
                              recursive searches. On Windows, use forward
                              slashes for directories.  [default:
                              build/|buck-out/|dist/|_build/|\.eggs/|\.git/|
                              \.hg/|\.mypy_cache/|\.nox/|\.tox/|\.venv/|\.ipynb_checkpoints]
                              
  --clear-output              Clearing code output is included in formatting.
  
  --help                      Show this message and exit.
```


## Copyright

Copyright © 2019 Tom Catling.

`black-nb` is distributed under the terms of the [ISC licence].

[isc licence]: https://opensource.org/licenses/ISC
