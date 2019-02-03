import black_nb
from click.testing import CliRunner


def test_basic():
    runner = CliRunner()
    result = runner.invoke(black_nb.main, ["."])
    assert result.exit_code == 0
