"""Phase 3 — Load email templates from config/templates.yaml."""

from pathlib import Path

import yaml

_TEMPLATES_PATH = Path(__file__).resolve().parents[2] / "config" / "templates.yaml"


def load_templates() -> dict:
    """Return dict keyed by style name ('general', 'direct', 'curious')."""
    raw = yaml.safe_load(_TEMPLATES_PATH.read_text(encoding="utf-8"))
    return raw["styles"]
