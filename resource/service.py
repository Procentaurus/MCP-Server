from .http_client import fetch_data_from_api

BASE_URL = "https://api.frankfurter.dev/v1"


async def get_latest_rates(base: str = "EUR",
                           symbols: str | list[str] | None = None):
    """
    Fetch the latest currency exchange rates.
    """
    params = [f"base={base.upper()}"]
    if symbols:
        if isinstance(symbols, list):
            symbols = ",".join(symbols)
        params.append(f"symbols={symbols.upper()}")

    url = f"{BASE_URL}/latest?{'&'.join(params)}"

    data = await fetch_data_from_api(url)
    if not data:
        return "Unable to fetch forecast data.."
    return data


async def get_available_currencies():
    """
    Fetch a list of all supported currencies.
    """
    url = f"{BASE_URL}/currencies"

    data = await fetch_data_from_api(url)
    if not data:
        return "Unable to fetch forecast data.."
    return data


async def get_historical_rates(date: str,
                               end_date: str = "",
                               base: str = "EUR",
                               symbols: str | list[str] | None = None):
    """
    Fetch historical currency exchange rates for a specific date or range.
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

    data = await fetch_data_from_api(url)
    if not data:
        return "Unable to fetch forecast data.."
    return data