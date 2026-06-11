# server.py

import os
from typing import Optional, Annotated
from typing_extensions import _AnnotatedAlias
from pydantic import Field
from fastmcp import FastMCP
from fastmcp.server.lifespan import lifespan
from fastmcp.dependencies import CurrentContext
from fastmcp.server.context import Context
from starlette.requests import Request
from starlette.responses import JSONResponse
from umlsearch import query_website, query_people

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


@mcp_server.tool()
async def search_uml_people(
    query: Annotated[str, "The search query"],
    top_k: Annotated[int, "The number of results to provide"],
):
    """Search for people at UMass Lowell"""
    results = await query_people(query, top_k)
    return results


@mcp_server.tool()
async def search_uml_website(
    query: Annotated[str, "The search query"],
    top_k: Annotated[int, "The number of results to provide"],
):
    """Search the general UMass Lowell website"""
    results = await query_website(query, top_k)
    return results


@mcp_server.tool()
async def search_uml_places(query: str):
    """Search for places across UMass Lowell"""
    pass


@mcp_server.tool()
async def search_uml_news(query: str):
    """Search for UMass Lowell news"""
    pass


if __name__ == "__main__":
    mcp_server.run(transport="streamable-http", host=BROADCAST_ADDRESS, port=8000)
