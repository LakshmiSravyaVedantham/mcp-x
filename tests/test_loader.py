import json
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
from mcp_x.loader import load_openapi_spec


def test_loads_from_json_file():
    spec = {"openapi": "3.0.0", "paths": {}}
    with tempfile.NamedTemporaryFile(suffix=".json", mode="w", delete=False) as f:
        json.dump(spec, f)
        path = f.name
    result = load_openapi_spec(path)
    assert result["openapi"] == "3.0.0"


def test_loads_from_yaml_file():
    yaml_content = "openapi: '3.0.0'\npaths: {}\n"
    with tempfile.NamedTemporaryFile(suffix=".yaml", mode="w", delete=False) as f:
        f.write(yaml_content)
        path = f.name
    result = load_openapi_spec(path)
    assert result["openapi"] == "3.0.0"


def test_raises_on_missing_file():
    with pytest.raises(FileNotFoundError):
        load_openapi_spec("/nonexistent/spec.json")


def test_loads_from_url():
    mock_response = MagicMock()
    mock_response.json.return_value = {"openapi": "3.0.0", "paths": {}}
    mock_response.raise_for_status = MagicMock()

    with patch("httpx.get", return_value=mock_response):
        result = load_openapi_spec("https://api.example.com/openapi.json")

    assert result["openapi"] == "3.0.0"
