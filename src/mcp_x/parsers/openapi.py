"""OpenAPI spec parser — extracts endpoints as MCP ToolDefinitions."""

from mcp_x.parsers.cli import ToolDefinition


def parse_openapi_spec(spec: dict) -> list[ToolDefinition]:
    """Parse an OpenAPI spec dict into ToolDefinitions.

    Each HTTP operation (GET, POST, PUT, PATCH, DELETE) found under
    ``spec["paths"]`` becomes one ToolDefinition.  The tool name is taken
    from ``operationId`` when present; otherwise it is derived from the HTTP
    method and path (e.g. ``GET /items`` → ``get_items``).
    """
    tools: list[ToolDefinition] = []
    paths = spec.get("paths", {})

    base_url = ""
    servers = spec.get("servers", [])
    if servers:
        base_url = servers[0].get("url", "")

    for path, path_item in paths.items():
        for method, operation in path_item.items():
            if method not in ("get", "post", "put", "patch", "delete"):
                continue
            if not isinstance(operation, dict):
                continue

            # Tool name: prefer operationId, fall back to method_path
            op_id = operation.get("operationId")
            if not op_id:
                clean = (
                    path.strip("/").replace("/", "_").replace("{", "").replace("}", "")
                )
                op_id = f"{method}_{clean}"

            description = (
                operation.get("summary") or operation.get("description") or op_id
            )

            # Collect query/path/header parameters
            params: dict[str, str] = {}
            for param in operation.get("parameters", []):
                pname = param.get("name", "")
                pdesc = param.get(
                    "description",
                    param.get("schema", {}).get("type", "string"),
                )
                if pname:
                    params[pname] = pdesc

            tools.append(
                ToolDefinition(
                    name=op_id,
                    description=f"{method.upper()} {path} — {description}",
                    command=[method.upper(), base_url + path],
                    parameters=params,
                )
            )

    return tools
