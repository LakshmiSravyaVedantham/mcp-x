import pytest

from mcp_x.detector import InputType, detect_input_type


def test_detects_cli_tool():
    assert detect_input_type("git") == InputType.CLI


def test_detects_local_openapi_json():
    assert detect_input_type("openapi.json") == InputType.OPENAPI


def test_detects_local_openapi_yaml():
    assert detect_input_type("spec.yaml") == InputType.OPENAPI


def test_detects_http_url():
    assert (
        detect_input_type("https://api.example.com/openapi.json") == InputType.OPENAPI
    )


def test_detects_http_url_no_extension():
    assert detect_input_type("https://api.example.com/spec") == InputType.OPENAPI


def test_unknown_raises():
    with pytest.raises(ValueError, match="Cannot determine input type"):
        detect_input_type("")
