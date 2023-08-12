import click

from pyrb.portfolio import Portfolio, portfolio_factory


class Context:
    def __init__(self, portfolio: Portfolio) -> None:
        self._portfolio = portfolio

    @property
    def portfolio(self) -> Portfolio:
        return self._portfolio


@click.group()
@click.pass_context
def cli(ctx: click.Context) -> None:
    portfolio = portfolio_factory("ebest")
    ctx.obj = Context(portfolio)


@cli.command()
@click.pass_obj
def rebalance(ctx: Context) -> None:
    stocks = _get_target_stocks(ctx.portfolio)
    weights = _get_weights(stocks)

    # Output the chosen stocks and weights to the user
    click.echo("Selected Stocks and Weights:")
    for stock, weight in weights.items():
        click.echo(f"{stock}: {weight*100:.2f}%")
    # Continue with your logic to rebalance the stocks based on the chosen strategy and weights


def _get_target_stocks(portfolio: Portfolio) -> list[str]:
    return portfolio.holding_symbols


def _get_weights(stock_list: list[str]) -> dict[str, float]:
    return {stock: 1 / len(stock_list) for stock in stock_list}


if __name__ == "__main__":
    cli()
