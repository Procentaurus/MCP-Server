from mcp.server.fastmcp import FastMCP


def register_prompts(server: FastMCP) -> None:
    @server.prompt(
        name="list_available_currencies",
        title="List Currencies",
        description="Show all available currencies with their full names " \
                    "and ISO codes."
    )
    def list_available_currencies_prompt() -> str:
        return "List all available currencies and their ISO codes " \
               " in a clear format."

    @server.prompt(
        name="fetch_latest_rates",
        title="Fetch Latest Rates",
        description="Retrieve the latest exchange rates vs selected currencies."
    )
    def fetch_latest_rates_prompt(base: str = "EUR",
                                  symbols: list[str] | None = None) -> str:
        if symbols:
            return f"Get the latest rates of the currency {base} for the " \
                   f"given currencies {', '.join(symbols)}."
        return f"Get the latest rates of the currency {base} vs " \
               "all possible currencies."

    @server.prompt(
        name="historical_currency_summary",
        title="Historical Summary",
        description="Summarize what were exchange rates for selected " \
                    "currencies on a given date or date range."
    )
    def historical_rates_prompt(date: str,
                                end_date: str = "",
                                base: str = "EUR",
                                symbols: list[str] | None = None) -> str:

        if symbols:
            symbol_str = ', '.join(symbols)
        else:
            symbol_str = "all currencies"

        if end_date == "":
            date_segment = f"on {date}"
        else:
            date_segment = f"between {date} and {end_date}"

        return (
            f"Give me information about rates for the currency {base} vs "
            f"{symbol_str} {date_segment}."
        )