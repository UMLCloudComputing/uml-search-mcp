# server.py

import os
from typing import Optional, Annotated
from pydantic import Field
from fastmcp import FastMCP
from fastmcp.server.lifespan import lifespan
from fastmcp.dependencies import CurrentContext
from fastmcp.server.context import Context
from starlette.requests import Request
from starlette.responses import JSONResponse
from umlsearch import (
    Course,
    API,
    parse_catalog_courses_response,
    get_subject_prefix_mapping,
)

# Configuration
BROADCAST_ADDRESS = os.getenv("BROADCAST_ADDRESS", "127.0.0.1")


@lifespan
async def app_lifespan(server):
    """Initialization and destruction steps for server"""
    print("Starting server...")
    try:
        # Configure server persistent
        yield
    finally:
        print("Shutting down server...")


mcp_server = FastMCP("UML-Search-MCP-Server", lifespan=app_lifespan)


@mcp_server.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> JSONResponse:
    # Add pre-flight checks here, none at the moment
    return JSONResponse({"status": "ok", "service": "uml-search-mcp"}, status_code=200)


if __name__ == "__main__":
    mcp_server.run(transport="streamable-http", host=BROADCAST_ADDRESS, port=8000)
