"""Tests for system inspection tools."""

from gdm.mcp.inspection import get_system_summary, query_components
from gdm.mcp.schemas import ComponentFilter


def test_get_system_summary(simple_system):
    """Test getting system summary."""
    summary = get_system_summary(simple_system)

    assert summary.name == "test_system"
    assert summary.total_components == 4
    assert len(summary.components_by_type) > 0
    assert summary.has_timeseries is False  # No time series in simple system


def test_get_system_summary_structure(multi_substation_system):
    """Test summary structure with multiple substations."""
    summary = get_system_summary(multi_substation_system)

    assert summary.name == "multi_sub_system"
    assert len(summary.substations) == 2  # Two substations
    assert len(summary.feeders) == 4  # 2 substations x 2 feeders each
    assert summary.total_components > 0

    # Check component type summaries
    assert len(summary.components_by_type) > 0
    for comp_summary in summary.components_by_type:
        assert comp_summary.count > 0


def test_query_components_by_type(simple_system):
    """Test querying components by type."""
    filters = ComponentFilter(component_types=["DistributionBus"])
    results = query_components(simple_system, filters)

    assert len(results) == 2  # Two buses in simple system
    assert all(c.component_type == "DistributionBus" for c in results)


def test_query_components_by_substation(multi_substation_system):
    """Test querying components by substation."""
    filters = ComponentFilter(substation="sub1")
    results = query_components(multi_substation_system, filters)

    assert len(results) > 0
    assert all(c.substation == "sub1" for c in results if c.substation is not None)


def test_query_components_by_feeder(multi_substation_system):
    """Test querying components by feeder."""
    filters = ComponentFilter(feeder="feeder1_1")
    results = query_components(multi_substation_system, filters)

    assert len(results) > 0
    assert all(c.feeder == "feeder1_1" for c in results if c.feeder is not None)


def test_query_components_no_filters(simple_system):
    """Test querying without filters returns all components."""
    filters = ComponentFilter()
    results = query_components(simple_system, filters)

    assert len(results) == 4  # All components
