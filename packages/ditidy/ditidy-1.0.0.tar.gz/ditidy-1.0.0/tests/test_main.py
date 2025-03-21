from click.testing import CliRunner
from ditidy.cli import cli


def test_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0


def test_version():
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0


def test_basic():
    runner = CliRunner()
    result = runner.invoke(cli, ["--config-file", "tests/ditidy.yaml"])
    assert result.exit_code == 0
