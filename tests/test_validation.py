"""Tests for validation diagnostics."""

from gdm.mcp.validation.diagnostics import diagnose_system


def test_diagnose_valid_system(simple_system):
    """Test diagnosing a valid system."""
    report = diagnose_system(simple_system)

    assert report.system_name == "test_system"
    assert report.total_components == 4  # substation, feeder, 2 buses
    assert report.is_valid
    assert len(report.issues) == 0


def test_diagnose_system_structure(simple_system):
    """Test that diagnosis report has correct structure."""
    report = diagnose_system(simple_system)

    assert hasattr(report, "system_name")
    assert hasattr(report, "total_components")
    assert hasattr(report, "valid_components")
    assert hasattr(report, "invalid_components")
    assert hasattr(report, "issues")
    assert isinstance(report.issues, list)


def test_diagnose_multi_substation_system(multi_substation_system):
    """Test diagnosing a system with multiple substations."""
    report = diagnose_system(multi_substation_system)

    assert report.system_name == "multi_sub_system"
    assert report.total_components > 0
    # System should be valid since we constructed it correctly
    assert report.is_valid or len(report.issues) == 0
