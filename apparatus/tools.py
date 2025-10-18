from mcp.server.fastmcp import FastMCP
from resource.requests import (get_available_currencies,
                               get_latest_rates,
                               get_historical_rates)


def register_tools(server: FastMCP) -> None:

    @server.tool(
        name="get_available_currencies",
        description="Fetch the list of all supported currencies",
    )
    def available_currencies_tool() -> dict:
        currencies = get_available_currencies()
        return {"currencies": currencies}

    @server.tool(
        name="get_latest_rates",
        description="Fetch the latest exchange rates for a given base and" \
                    "optional target currencies.",
    )
    def latest_rates_tool(base: str = "EUR",
                        symbols: list[str] | None = None) -> dict:
        data = get_latest_rates(base=base, symbols=symbols)
        return {"data": data}

    @server.tool(
        name="get_historical_rates",
        description="Fetch historical exchange rates for a given date" \
                    "and optional currencies.",
    )
    def historical_rates_tool(date: str,
                            end_date: str = "",
                            base: str = "EUR",
                            symbols: list[str] | None = None) -> dict:
        data = get_historical_rates(date=date,
                                    end_date=end_date,
                                    base=base,
                                    symbols=symbols)
        return {"data": data}
