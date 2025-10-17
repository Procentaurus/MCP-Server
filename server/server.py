from mcp import Server

from tools.tools import (get_available_currencies_tool,
                         get_latest_rates_tool,
                         get_historical_rates_tool)
from .manifest import (CAPABILITIES,
                       NAME,
                       VERSION)
server = Server(
    name=NAME,
    version=VERSION,
    capabilities=CAPABILITIES,
)

# Register tools
server.add_tool(get_available_currencies_tool)
server.add_tool(get_latest_rates_tool)
server.add_tool(get_historical_rates_tool)


if __name__ == "__main__":
    server.run()
