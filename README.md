# black-nb

`black-nb` applies [black](https://github.com/ambv/black) to the code cells of Jupyter notebooks. It can be called with a list of files or directories and will search for all files ending with '.ipynb', excluding paths containing '.ipynb_checkpoints'. Additional exclusions can be added using one or 
more `-x` options (wildcards not supported), line length can be configured with `-l`.

Non-code cells and cells with cell magic (anything starting with '%%') will be excluded. Line magic ('%') will be treated as a comment
and restored after reformatting.

Notebooks are modified inplace.
 
## Installation

```bash
pip install git+git://github.com/tomcatling/black-nb.git#egg=black-nb
```

`nb-black` requires Python 3.6 or later.

## Usage

To apply black with a line length of 88 to all notebooks under the current directory, excluding anything with 'example' in its path and 'messy.ipynb' in the current directory:

```bash
black-nb . -l 88 -x example -x ./messy.ipynb
```

## Copyright

Copyright © 2019 Tom Catling.

`black-nb` is distributed under the terms of the [ISC licence].

[isc licence]: https://opensource.org/licenses/ISC
