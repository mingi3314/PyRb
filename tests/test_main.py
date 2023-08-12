from click.testing import CliRunner
from pytest_mock import MockerFixture

from pyrb.main import cli
from pyrb.portfolio import EbestPortfolio


def test_sut_rebalance(mocker: MockerFixture) -> None:
    # given
    runner = CliRunner()

    mocked_symbols = ["000660", "005930", "035420"]
    mocker.patch.object(
        EbestPortfolio,
        "holding_symbols",
        new_callable=mocker.PropertyMock(return_value=mocked_symbols),
    )

    # when
    result = runner.invoke(cli, ["rebalance"])
    assert result.exit_code == 0
    assert (
        result.output
        == "Selected Stocks and Weights:\n000660: 33.33%\n005930: 33.33%\n035420: 33.33%\n"
    )
