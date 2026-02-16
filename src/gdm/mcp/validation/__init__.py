"""Validation module for diagnosing and fixing distribution systems."""

from gdm.mcp.validation.diagnostics import diagnose_system
from gdm.mcp.validation.suggestions import suggest_fixes
from gdm.mcp.validation.auto_fixer import apply_fixes

__all__ = ["diagnose_system", "suggest_fixes", "apply_fixes"]
