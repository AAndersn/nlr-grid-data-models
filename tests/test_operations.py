"""Tests for system merge operations."""

import pytest
from gdm.distribution import DistributionSystem
from gdm.distribution.components import DistributionBus, DistributionFeeder, DistributionSubstation
from gdm.distribution.enums import VoltageTypes
from gdm.quantities import Voltage
from gdm.mcp.operations.merger import merge_systems


def test_merge_two_systems(simple_system):
    """Test merging two systems."""
    # Create a completely separate second system to avoid UUID conflicts
    system2 = DistributionSystem(name="test_system_2", auto_add_composed_components=True)
    sub2 = DistributionSubstation(name="sub2", feeders=[])
    feeder2 = DistributionFeeder(name="feeder2")
    sub2.feeders.append(feeder2)
    bus3 = DistributionBus(
        name="bus3",
        phases=["A", "B", "C"],
        voltage_type=VoltageTypes.LINE_TO_LINE,
        rated_voltage=Voltage(12.47, "kV"),
        substation=sub2,
        feeder=feeder2,
    )
    system2.add_component(sub2)
    system2.add_component(bus3)

    systems = [simple_system, system2]
    merged_system, report = merge_systems(systems, name="merged_system", strict=True)

    assert report.success
    assert report.output_system_name == "merged_system"
    assert report.input_system_count == 2
    assert merged_system.name == "merged_system"
    # Should have components from both systems (more than just simple_system's 3 components)
    assert report.total_components_merged > 3


def test_merge_with_conflicts(simple_system):
    """Test that merge detects UUID conflicts."""
    # Try to merge system with itself (same UUIDs)
    systems = [simple_system, simple_system]

    with pytest.raises(Exception):  # Should raise MergeConflictError
        merged_system, report = merge_systems(systems, name="conflicted", strict=True)


def test_merge_preserves_names(simple_system):
    """Test that merge preserves component structure."""
    # Create new system with different names
    system2 = DistributionSystem(name="system2", auto_add_composed_components=True)
    sub_copy = DistributionSubstation(name="sub1_copy", feeders=[])
    feeder_copy = DistributionFeeder(name="feeder1_copy")
    sub_copy.feeders.append(feeder_copy)
    bus1_copy = DistributionBus(
        name="bus1_copy",
        phases=["A", "B", "C"],
        voltage_type=VoltageTypes.LINE_TO_LINE,
        rated_voltage=Voltage(12.47, "kV"),
        substation=sub_copy,
        feeder=feeder_copy,
    )
    system2.add_component(sub_copy)
    system2.add_component(bus1_copy)

    systems = [simple_system, system2]
    merged_system, report = merge_systems(systems, name="merged", strict=True)

    # Check that both original and copy components exist
    component_names = {c.name for c in merged_system.iter_all_components()}
    assert "bus1" in component_names
    assert "bus1_copy" in component_names
