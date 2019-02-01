[![CircleCI](https://circleci.com/gh/tomcatling/black-nb.svg?style=shield)](https://circleci.com/gh/tomcatling/black-nb)

# black-nb

*black-nb* applies [*black*](https://github.com/ambv/black) to Jupyter notebooks.

Much of the code is taken from the original *black* project and the behaviour is intentionally similar.
 
## Installation

*black-nb* can be installed by running `pip install black-nb`.  It requires
Python 3.6.0+ to run but you can reformat Python 2 code with it, too.

## Usage

To apply *black* with a line length of 120 to all code cells in notebooks under the current directory:

```bash
black-nb . -l 120
```

To check if notebooks pass *black*, including have no output:

```bash
black-nb . -l 120 --clear-output --check
```

To exclude reformat everything below `./` excluding `./outputs/*` :

```bash
black-nb . -l 120 --exclude outputs
```

## Command Line Options

*black-nb* doesn't provide many options.  You can list them by running
`black-nb --help`:

```text
black-nb [OPTIONS] [SRC]...

Options:
  -l, --line-length INTEGER   Where to wrap around.  [default: 88]
                              Don't normalize underscores in numeric literals.
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
