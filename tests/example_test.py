from black_nb.cli import cli
from click.testing import CliRunner


def test_basic():
    runner = CliRunner()
    result = runner.invoke(cli, ["."])
    assert result.exit_code == 0
