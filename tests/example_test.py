import black_nb
import click
from click.testing import CliRunner

def test_basic():
    runner = CliRunner()
    result = runner.invoke(black_nb.main, ['.'])
    assert result.exit_code == 0
    
if __name__ == "__main__":
    test_basic()