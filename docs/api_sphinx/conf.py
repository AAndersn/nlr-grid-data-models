from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

project = "Grid-Data-Models API"
author = "NLR Distribution Suite"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinxcontrib.autodoc_pydantic",
]

autosummary_generate = True
autodoc_member_order = "bysource"

# Keep output concise and avoid noisy internals by default.
autodoc_default_options = {
    "members": True,
    "undoc-members": False,
    "show-inheritance": True,
}

autodoc_pydantic_model_show_json = False
autodoc_pydantic_model_show_config_summary = False
autodoc_pydantic_model_show_config_member = False
autodoc_pydantic_model_show_validator_summary = False
autodoc_pydantic_model_show_field_summary = True
autodoc_mock_imports = ["mcp"]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "pydata_sphinx_theme"
html_title = "Grid-Data-Models API"
html_static_path = ["_static"]
