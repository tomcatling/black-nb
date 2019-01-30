# nb-black

`nb-black` applies black to the code cells of a Jupyter notebook. 
 
## Installation

```bash
pip install git+git://github.com/tomcatling/nb-black.git#egg=nb-black
```

`nb-black` requires Python 3.6 or later.

## Usage

To remove all cells with 'exercise' tag:

```bash
nb-black -i notebook.ipynb -o notebook-blacked.ipynb -l 79
```

## Copyright

Copyright © 2019 Tom Catling.

`nb-black` is distributed under the terms of the [ISC licence].

[isc licence]: https://opensource.org/licenses/ISC
