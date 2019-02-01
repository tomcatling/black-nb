import importlib
black_nb = importlib.load_module('black-nb', './black-nb')

import click
from click.testing import CliRunner

def test_hello_world():
    runner = CliRunner()
    result = runner.invoke(black_nb.main, ['.'])
    #assert result.exit_code == 0
    #assert result.output == 'Hello Peter!\n'
    return result
    
test_hello_world()
