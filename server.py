# server.py

import os
import httpx
import time
from typing import Annotated

import functools
import inspect

from fastmcp import FastMCP
from fastmcp.server.lifespan import lifespan

from starlette.requests import Request
from starlette.responses import JSONResponse

from prometheus_client import Counter, Histogram, start_http_server

from umlsearch import query_website, query_people, query_place, query_news, process_url

# Configuration
BROADCAST_ADDRESS = os.getenv("BROADCAST_ADDRESS", "127.0.0.1")
DOCLING_BASE_ADDRESS = os.getenv("DOCLING_BASE_ADDRESS")

# Prometheus configuration
TOOL_CALLS_TOTAL = Counter(
    "uml_search_mcp_tool_calls_total",
    "Total number of MCP tool executions for uml-search-mcp",
    labelnames=["tool_name", "status"],
)

TOOL_EXECUTION_TIME = Histogram(
    "uml_search_mcp_tool_execution_seconds",
    "Time spent executing on MCP tool in seconds for uml-search-mcp",
    labelnames=["tool_name", "status"],
    buckets=(0.01, 0.05, 0.1, 0.5, 1.0, 2.5, 5.0, 10.0, float("inf")),
)


# Custom decorator for Prometheus
def monitor_tool(func):
    """
    A decorator to measure tool execution times and log metrics to Proemtheus.
    Supports both standard sync and async functions automatically.
    """
    tool_name = func.__name__

    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        status = "success"
        try:
            return await func(*args, **kwargs)
        except Exception:
            status = "failure"
            raise
        finally:
            duration = time.perf_counter() - start_time
            TOOL_EXECUTION_TIME.labels(tool_name=tool_name, status=status).observe(
                duration
            )
            TOOL_CALLS_TOTAL.labels(tool_name=tool_name, status=status).inc()

    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        status = "success"
        try:
            return func(*args, **kwargs)
        except Exception:
            status = "failure"
            raise
        finally:
            duration = time.perf_counter() - start_time
            TOOL_EXECUTION_TIME.labels(tool_name, status).observe(duration)
            TOOL_CALLS_TOTAL.labels(tool_name=tool_name, status=status).inc()

    return async_wrapper if inspect.iscoroutinefunction(func) else sync_wrapper


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
@monitor_tool
async def search_uml_people(
    query: Annotated[str, "The search query"],
    top_k: Annotated[int, "The number of results to provide"],
):
    """Search for people at UMass Lowell"""
    results = await query_people(query, top_k)
    return results


# DONE
@mcp_server.tool()
@monitor_tool
async def search_uml_website(
    query: Annotated[str, "The search query"],
    top_k: Annotated[int, "The number of results to provide"],
):
    """Search the general UMass Lowell website"""
    results = await query_website(query, top_k)
    return results


# DONE
@mcp_server.tool()
@monitor_tool
async def search_uml_places(
    query: Annotated[str, "The search query"],
    top_k: Annotated[int, "The number of results to provide"],
):
    """Search for places across UMass Lowell"""
    results = await query_place(query, top_k)
    return results


# DONE
@mcp_server.tool()
@monitor_tool
async def search_uml_news(
    query: Annotated[str, "The search query"],
    top_k: Annotated[int, "The number of results to provide"],
):
    """Search for UMass Lowell news"""
    results = await query_news(query, top_k)
    return results


# DONE
@mcp_server.tool()
@monitor_tool
async def parse_uml_url(url: Annotated[str, "The UMass Lowell domain URL to parse"]):
    """Parse and return content from a URL as markdown for much more detailed information"""
    result = await process_url(client, url, DOCLING_BASE_ADDRESS)
    return result


if __name__ == "__main__":
    PORT = 8000
    print("🔧 Starting the Prometheus metrics server on port: 9090")
    start_http_server(port=9090)
    mcp_server.run(transport="streamable-http", host=BROADCAST_ADDRESS, port=PORT)
