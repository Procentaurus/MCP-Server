import requests


def fetch_data_from_api(url: str, timeout: int = 10):
    """
    Fetch JSON data from a given API endpoint.
    
    Args:
        url (str): The API endpoint to query.
        timeout (int): How long to wait for a response (seconds). Default 10s.
    
    Returns:
        dict | list: Parsed JSON response from the API.
    
    Raises:
        RuntimeError: If the request fails or the response is invalid.
    """
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()  # raises HTTPError if not 200 OK
        return response.json()
    except requests.exceptions.Timeout:
        raise RuntimeError(f"Request to {url} timed out after {timeout}s")
    except requests.exceptions.ConnectionError:
        raise RuntimeError(f"Failed to connect to {url}")
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(f"HTTP error {response.status_code}: {e}")
    except ValueError:
        raise RuntimeError(f"Response from {url} is not valid JSON")
