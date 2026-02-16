"""Operations module for system-level transformations."""

from gdm.mcp.operations.merger import merge_systems
from gdm.mcp.operations.splitter import split_by_feeder, split_by_substation

__all__ = ["merge_systems", "split_by_feeder", "split_by_substation"]
