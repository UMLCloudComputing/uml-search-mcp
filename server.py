# server.py

import os
import httpx
from typing import Optional, Annotated
from typing_extensions import _AnnotatedAlias
from pydantic import Field
from fastmcp import FastMCP
from fastmcp.server.lifespan import lifespan
from fastmcp.dependencies import CurrentContext
from fastmcp.server.context import Context
from starlette.requests import Request
from starlette.responses import JSONResponse
from umlsearch import query_website, query_people, query_place, query_news, process_url

# Configuration
BROADCAST_ADDRESS = os.getenv("BROADCAST_ADDRESS", "127.0.0.1")
DOCLING_BASE_ADDRESS = os.getenv("DOCLING_BASE_ADDRESS")

# Global and shared AsyncClient object used for url data parsing tool
client = None


@lifespan
async def app_lifespan(server):
    """Initialization and destruction steps for server"""
    print("Starting server...")
    try:
        # Configure server persistent
        global client
        client = httpx.AsyncClient()
        yield
    finally:
        print("Shutting down server...")
        await client.aclose()


mcp_server = FastMCP("UML-Search-MCP-Server", lifespan=app_lifespan)


@mcp_server.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> JSONResponse:
    # Add pre-flight checks here, none at the moment
    return JSONResponse({"status": "ok", "service": "uml-search-mcp"}, status_code=200)


# DONE
@mcp_server.tool()
async def search_uml_people(
    query: Annotated[str, "The search query"],
    top_k: Annotated[int, "The number of results to provide"],
):
    """Search for people at UMass Lowell"""
    results = await query_people(query, top_k)
    return results


# DONE
@mcp_server.tool()
async def search_uml_website(
    query: Annotated[str, "The search query"],
    top_k: Annotated[int, "The number of results to provide"],
):
    """Search the general UMass Lowell website"""
    results = await query_website(query, top_k)
    return results


# DONE
@mcp_server.tool()
async def search_uml_places(
    query: Annotated[str, "The search query"],
    top_k: Annotated[int, "The number of results to provide"],
):
    """Search for places across UMass Lowell"""
    results = await query_place(query, top_k)
    return results


# DONE
@mcp_server.tool()
async def search_uml_news(
    query: Annotated[str, "The search query"],
    top_k: Annotated[int, "The number of results to provide"],
):
    """Search for UMass Lowell news"""
    results = await query_news(query, top_k)
    return results


# DONE
@mcp_server.tool()
async def parse_uml_url(url: Annotated[str, "The UMass Lowell domain URL to parse"]):
    """Parse and return the markdown content from a URL from the UMass Lowell domain"""
    result = await process_url(client, url, DOCLING_BASE_ADDRESS)
    return result


if __name__ == "__main__":
    mcp_server.run(transport="streamable-http", host=BROADCAST_ADDRESS, port=8000)
