from .generic_request import fetch_data_from_api


BASE_URL = "https://api.frankfurter.dev/v1"


def get_latest_rates(base: str = "EUR",
                     symbols: str | list[str] | None = None):
    """
    Fetch the latest currency exchange rates.

    Args:
        base (str): Base currency (default: "EUR")
        symbols (str | list[str] | None): Comma-separated or list of
                                          target currencies (e.g. "USD,GBP")
    
    Returns:
        dict: Latest exchange rates JSON
    """

    params = [f"base={base.upper()}"]
    if symbols:
        if isinstance(symbols, list):
            symbols = ",".join(symbols)
        params.append(f"symbols={symbols.upper()}")

    return fetch_data_from_api(f"{BASE_URL}/latest?{'&'.join(params)}")


def get_available_currencies():
    """
    Fetch a list of all supported currencies.

    Returns:
        dict: Dictionary of available currency codes and their full names
    """
    return fetch_data_from_api(f"{BASE_URL}/currencies")


def get_historical_rates(date: str,
                         end_date: str = "",
                         base: str = "EUR",
                         symbols: str | list[str] | None = None):
    """
    Fetch historical currency exchange rates for a specific date.

    Args:
        date (str): Date in YYYY-MM-DD format
        end_date (str): Date in YYYY-MM-DD format
        base (str): Base currency (default: "EUR")
        symbols (str | list[str] | None): Target currencies (comma-separated or list)
    
    Returns:
        dict: Historical exchange data for a date or period
    """

    params = [f"base={base.upper()}"]
    if symbols:
        if isinstance(symbols, list):
            symbols = ",".join(symbols)
        params.append(f"symbols={symbols.upper()}")
    if end_date:
        url = f"{BASE_URL}/{date}..{end_date}?{'&'.join(params)}"
    else:
        url = f"{BASE_URL}/{date}?{'&'.join(params)}"
    return fetch_data_from_api(url)
