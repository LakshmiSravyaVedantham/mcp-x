import pytest

from mcp_x.parsers.openapi import ToolDefinition, parse_openapi_spec

MINIMAL_SPEC = {
    "openapi": "3.0.0",
    "info": {"title": "Test API", "version": "1.0.0"},
    "servers": [{"url": "https://api.example.com"}],
    "paths": {
        "/users": {
            "get": {
                "operationId": "list_users",
                "summary": "List all users",
                "parameters": [
                    {
                        "name": "limit",
                        "in": "query",
                        "schema": {"type": "integer"},
                        "description": "Max results",
                    }
                ],
            }
        },
        "/users/{id}": {
            "get": {
                "operationId": "get_user",
                "summary": "Get user by ID",
            },
            "delete": {
                "operationId": "delete_user",
                "summary": "Delete a user",
            },
        },
    },
}


def test_extracts_tool_names():
    tools = parse_openapi_spec(MINIMAL_SPEC)
    names = [t.name for t in tools]
    assert "list_users" in names
    assert "get_user" in names
    assert "delete_user" in names


def test_extracts_descriptions():
    tools = parse_openapi_spec(MINIMAL_SPEC)
    tool = next(t for t in tools if t.name == "list_users")
    assert "List all users" in tool.description


def test_extracts_parameters():
    tools = parse_openapi_spec(MINIMAL_SPEC)
    tool = next(t for t in tools if t.name == "list_users")
    assert "limit" in tool.parameters


def test_fallback_name_without_operation_id():
    spec = {
        "openapi": "3.0.0",
        "info": {"title": "T", "version": "1"},
        "paths": {"/items": {"get": {"summary": "List items"}}},
    }
    tools = parse_openapi_spec(spec)
    assert len(tools) == 1
    assert tools[0].name == "get_items"
