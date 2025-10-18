from mcp.server.fastmcp import FastMCP as Server

from apparatus.tools import register_tools
from apparatus.prompts import register_prompts
from .params import NAME


server = Server(name=NAME)
register_tools(server)
register_prompts(server)


if __name__ == "__main__":
    server.run()
