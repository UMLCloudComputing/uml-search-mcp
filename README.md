# UML Search MCP Server

An MCP server for searching across the UMass Lowell web domain.

## Usage

The MCP server can be used locally by either

- Run as host process: `uv run server.py`
  - Accessible at `localhost:8000/mcp`
- Run as a docker container: `./build_and_run.sh`
  - Accessible at `0.0.0.0:8000/mcp` or `localhost:8000/mcp` locally

> [!NOTE]
> If you're using the MCP Inspector tool for local development, uml-search-mcp uses the Streamable HTTP transport, not STDIO or server-sent events (SSE).

## ☸ Kubernetes

For production deployments on kubernetes check the reference manifest, `k8s/k8s_prod.yaml`.

## 🧩 Technologies

- Docker
- MCP
- Prometheus

## 🛠️ Tool Calls

![Tool Calls](./images/tool_calls.png)

## 🔬 Metrics

This MCP server exposes a Proemtheus `/metrics` endpoint which can be scraped for metrics

The `k8s/` directory also contains a `ServiceMonitor` manifest to point a Prometheus instance on k8s to the MCP server.

Application Metrics exposed:

- `uml_search_mcp_tool_calls_total`: Total number of MCP tool executions for uml-search-mcp
- `uml_search_mcp_tool_execution_seconds`: Time spent executing on MCP tool in seconds for uml-search-mcp
