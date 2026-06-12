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

## 🛠️ Tool Calls

<table>
  <tr>
    <th>Tool Name</th>
    <th>Description</th>
    <th>Function Signature</th>
    <th>Response Schema</th>
    <th>Misc.</th>
  </tr>
  <tr>
    <td><code>search_uml_people</code></td>
    <td>Search for people at UMass Lowell</td>
    <td>
      <pre><code>
        ... (query: str
              top_k: int)
      </code></pre>
    </td>
    <td>
      <pre><code>
        {
          name: str
          role: str
          department: str
          building: str
          email: str
          phone_number: str
        }
      </code></pre>
    </td>
    <td>Identified as `PeopleSearchResultItem` object</td>
  </tr>
  <tr>
    <td><code>search_uml_website</code></td>
    <td>Search the general UMass Lowell website</td>
    <td>
      <pre><code>
        ... (query: str
              top_k: int)
      </code></pre>
    </td>
    <td>
      <pre><code>
        {
          title: str
          detail: str
          url: str
        }
      </code></pre>
    </td>
    <td>Identified as `SearchResultItem` object</td>
  </tr>
  <tr>
    <td><code>search_uml_places</code></td>
    <td>Search for places across UMass Lowell</td>
    <td>
      <pre><code>
        ... (query: str
              top_k: int)
      </code></pre>
    </td>
    <td>
      <pre><code>
        {
          name: str
          address: str
          map_url: str
          phone_number: Optional[str]
        }
      </code></pre>
    </td>
    <td>Identified as `PlaceSearchResultItem` object</td>
  </tr>
  <tr>
    <td><code>search_uml_news</code></td>
    <td>Search for UMass Lowell news</td>
    <td>
      <pre><code>
        ... (query: str
              top_k: int)
      </code></pre>
    </td>
    <td>
      <pre><code>
        {
          title: str
          detail: str
          url: str
        }
      </code></pre>
    </td>
    <td>Identified as `NewsSearchResultItem` object</td>
  </tr>
  <tr>
    <td><code>parse_uml_url</code></td>
    <td>Parse and return the markdown content from a URL from the UMass Lowell domain</td>
    <td>
      <pre><code>
        ... (url: str)
      </code></pre>
    </td>
    <td>
      <pre><code>
        str
      </code></pre>
    </td>
    <td>Returns a raw string as the processed markdown content.</td>
  </tr>
 </table>
