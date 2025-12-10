import sys
import os
from mcp.server.fastmcp import FastMCP as Server

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from apparatus.tools import register_tools
from apparatus.prompts import register_prompts
from server.params import NAME

server = Server(name=NAME)

register_tools(server)
register_prompts(server)

if __name__ == "__main__":
    server.run()