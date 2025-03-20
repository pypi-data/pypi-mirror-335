import sys
from typing import Literal

import json
import logging

from natural_history_museum_mcp import nhm_api
from mcp.server.fastmcp import FastMCP


COMMUNICATION_TYPE: Literal["stdio", "sse"] = "stdio" # For talking to clients locally
mcp = FastMCP("Natural History Museum Data API")

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    )
logger = logging.getLogger("BlenderMCPServer")

@mcp.tool()
def search_specimens(query: str, limit: int) -> str:
    print("Starting search specimens", file=sys.stderr)
    nhm_api_result = nhm_api.get_by_query(query, limit)

    return json.dumps(nhm_api_result)


def main():
    print("MCP run starting", file=sys.stderr)
    mcp.run(COMMUNICATION_TYPE)

if __name__ == "__main__":
    main()
