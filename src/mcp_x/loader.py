import json
from pathlib import Path

import httpx


def load_openapi_spec(target: str) -> dict:  # type: ignore[type-arg]
    """Load OpenAPI spec from URL or file path."""
    if target.startswith("http://") or target.startswith("https://"):
        response = httpx.get(target, follow_redirects=True, timeout=10)
        response.raise_for_status()
        return response.json()  # type: ignore[no-any-return]

    path = Path(target)
    if not path.exists():
        raise FileNotFoundError(f"Spec file not found: {target}")

    if path.suffix in (".yaml", ".yml"):
        try:
            import yaml  # type: ignore[import]

            return yaml.safe_load(path.read_text())  # type: ignore[no-any-return]
        except ImportError:
            raise ImportError("Install PyYAML to load YAML specs: pip install pyyaml")

    return json.loads(path.read_text())  # type: ignore[no-any-return]
