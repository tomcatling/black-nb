# nb-filter-cells

`nb-filter-cells` filters Jupyter notebooks cells by tag. 
 
## Installation

```bash
pip install git+git://github.com/liamcoatman/nb-filter-cells.git#egg=nb-filter-cells
```

`nb-filter-cells` requires Python 3.6 or later.

## Usage

To remove all cells with 'exercise' tag:

```bash
nb-filter-cells -i notebook.ipynb -o notebook-solutions.ipynb -t exercise
```

## Copyright

Copyright © 2019 Liam Coatman.

`nb-filter-cells` is distributed under the terms of the [ISC licence].

[isc licence]: https://opensource.org/licenses/ISC
