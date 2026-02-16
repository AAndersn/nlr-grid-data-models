"""Tests for knowledge/documentation tools."""

from gdm.mcp.knowledge.documentation import (
    search_documentation,
    get_api_reference,
    get_code_examples,
    list_available_components,
    get_component_fields,
)


def test_list_available_components():
    """Test listing available components."""
    components = list_available_components()

    # Should have components
    assert len(components) > 0

    # Check that DistributionBus is in the list
    names = [c.name for c in components]
    assert "DistributionBus" in names
    assert "DistributionLoad" in names
    assert "DistributionTransformer" in names

    # Check structure
    for component in components:
        assert component.name
        assert component.description
        assert component.category == "Distribution Component"


def test_get_api_reference():
    """Test getting API reference for a component."""
    # Test with valid component
    result = get_api_reference("DistributionBus")

    assert result.component_name == "DistributionBus"
    assert result.description  # Should have description
    assert len(result.fields) > 0  # Should have fields

    # Check that common fields exist
    field_names = [f["name"] for f in result.fields]
    assert "name" in field_names

    # Test with invalid component
    result = get_api_reference("InvalidComponent")
    assert result.component_name == "InvalidComponent"
    assert "not found" in result.description.lower()


def test_get_component_fields():
    """Test getting component field details."""
    # Test with valid component
    fields = get_component_fields("DistributionBus")

    assert isinstance(fields, dict)
    assert len(fields) > 0

    # Check structure of fields
    for field_name, field_info in fields.items():
        assert "type" in field_info
        assert "required" in field_info
        assert "description" in field_info

    # Test with invalid component
    fields = get_component_fields("InvalidComponent")
    assert "error" in fields


def test_search_documentation():
    """Test searching documentation."""
    # This test may not find results if gdm repo is not available
    results = search_documentation("bus", max_results=5)

    # Should return a list (may be empty if repo not found)
    assert isinstance(results, list)
    assert len(results) <= 5

    # If results found, check structure
    if len(results) > 0 and "not found" not in results[0].title.lower():
        result = results[0]
        assert result.title
        assert result.content
        assert result.relevance_score >= 0


def test_get_code_examples():
    """Test getting code examples."""
    # This test may not find examples if gdm repo is not available
    examples = get_code_examples("bus")

    # Should return a list (may be empty if repo not found)
    assert isinstance(examples, list)

    # If examples found, check structure
    if len(examples) > 0:
        example = examples[0]
        assert example.title
        assert example.code
        assert example.file_path


def test_search_documentation_relevance():
    """Test that search results are sorted by relevance."""
    results = search_documentation("distribution", max_results=3)

    if len(results) >= 2:
        # Check that scores are in descending order
        for i in range(len(results) - 1):
            assert results[i].relevance_score >= results[i + 1].relevance_score
