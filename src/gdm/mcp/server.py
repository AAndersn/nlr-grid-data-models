"""MCP Server for Grid Data Models.

This module provides the main MCP server implementation that exposes
grid-data-models functionality as tools for AI agents.
"""

import json
import logging
from pathlib import Path
from typing import Annotated, Any

import typer
from gdm.distribution import DistributionSystem
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from gdm.mcp import __version__
from gdm.mcp.exceptions import GDMMCPException
from gdm.mcp.inspection import (
    analyze_topology,
    find_orphaned_components,
    get_component_details,
    get_component_relationships,
    get_system_summary,
    query_components,
    validate_connectivity,
)
from gdm.mcp.operations import merge_systems, split_by_feeder, split_by_substation
from gdm.mcp.schemas import ComponentFilter
from gdm.mcp.utilities import (
    export_subsystem_by_buses,
    get_time_series_summary,
)
from gdm.mcp.validation import apply_fixes, diagnose_system, suggest_fixes
from gdm.mcp.knowledge.documentation import (
    search_documentation,
    get_api_reference as get_api_ref,
    get_code_examples as get_code_ex,
    list_available_components as list_components_doc,
    get_component_fields as get_fields_doc,
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gdm_mcp")

# Create MCP server instance
app = Server("grid-data-models-mcp")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List all available MCP tools."""
    return [
        # Validation tools
        Tool(
            name="diagnose_system",
            description="Diagnose validation errors in a distribution system. Returns detailed error report with component UUIDs, error types, and affected fields.",
            inputSchema={
                "type": "object",
                "properties": {
                    "system_path": {
                        "type": "string",
                        "description": "Path to the distribution system JSON file",
                    }
                },
                "required": ["system_path"],
            },
        ),
        Tool(
            name="suggest_fixes",
            description="Generate fix suggestions for validation errors. Analyzes error report and proposes strategies with confidence levels.",
            inputSchema={
                "type": "object",
                "properties": {
                    "system_path": {
                        "type": "string",
                        "description": "Path to the distribution system JSON file",
                    }
                },
                "required": ["system_path"],
            },
        ),
        Tool(
            name="apply_fixes",
            description="Automatically apply fixes to a distribution system. Creates a fixed copy and returns change log.",
            inputSchema={
                "type": "object",
                "properties": {
                    "system_path": {
                        "type": "string",
                        "description": "Path to the distribution system JSON file",
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Path to save the fixed system",
                    },
                    "auto_approve": {
                        "type": "boolean",
                        "description": "Whether to apply low-confidence fixes (default: false)",
                        "default": False,
                    },
                },
                "required": ["system_path", "output_path"],
            },
        ),
        # System operation tools
        Tool(
            name="merge_systems",
            description="Merge multiple distribution systems into one. Preserves time series and detects conflicts.",
            inputSchema={
                "type": "object",
                "properties": {
                    "system_paths": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of paths to distribution system JSON files to merge",
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Path to save the merged system",
                    },
                    "name": {
                        "type": "string",
                        "description": "Name for the merged system",
                    },
                    "strict": {
                        "type": "boolean",
                        "description": "Error on conflicts (default: true)",
                        "default": True,
                    },
                },
                "required": ["system_paths", "output_path", "name"],
            },
        ),
        Tool(
            name="split_by_substation",
            description="Split a distribution system into separate systems for each substation.",
            inputSchema={
                "type": "object",
                "properties": {
                    "system_path": {
                        "type": "string",
                        "description": "Path to the distribution system JSON file",
                    },
                    "output_dir": {
                        "type": "string",
                        "description": "Directory to save the split systems",
                    },
                    "keep_timeseries": {
                        "type": "boolean",
                        "description": "Preserve time series data (default: true)",
                        "default": True,
                    },
                    "include_unassigned": {
                        "type": "boolean",
                        "description": "Create system for unassigned components (default: true)",
                        "default": True,
                    },
                },
                "required": ["system_path", "output_dir"],
            },
        ),
        Tool(
            name="split_by_feeder",
            description="Split a distribution system into separate systems for each feeder.",
            inputSchema={
                "type": "object",
                "properties": {
                    "system_path": {
                        "type": "string",
                        "description": "Path to the distribution system JSON file",
                    },
                    "output_dir": {
                        "type": "string",
                        "description": "Directory to save the split systems",
                    },
                    "keep_timeseries": {
                        "type": "boolean",
                        "description": "Preserve time series data (default: true)",
                        "default": True,
                    },
                    "include_unassigned": {
                        "type": "boolean",
                        "description": "Create system for unassigned components (default: true)",
                        "default": True,
                    },
                },
                "required": ["system_path", "output_dir"],
            },
        ),
        # Inspection tools
        Tool(
            name="get_system_summary",
            description="Get comprehensive summary of a distribution system including component counts, substations, feeders, and time series.",
            inputSchema={
                "type": "object",
                "properties": {
                    "system_path": {
                        "type": "string",
                        "description": "Path to the distribution system JSON file",
                    }
                },
                "required": ["system_path"],
            },
        ),
        Tool(
            name="query_components",
            description="Query and filter components in a distribution system by type, substation, feeder, phases, etc.",
            inputSchema={
                "type": "object",
                "properties": {
                    "system_path": {
                        "type": "string",
                        "description": "Path to the distribution system JSON file",
                    },
                    "component_types": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Filter by component types (optional)",
                    },
                    "substation": {
                        "type": "string",
                        "description": "Filter by substation name (optional)",
                    },
                    "feeder": {
                        "type": "string",
                        "description": "Filter by feeder name (optional)",
                    },
                    "phases": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Filter by phases (optional)",
                    },
                    "in_service": {
                        "type": "boolean",
                        "description": "Filter by in_service status (optional)",
                    },
                    "has_timeseries": {
                        "type": "boolean",
                        "description": "Filter by time series presence (optional)",
                    },
                },
                "required": ["system_path"],
            },
        ),
        Tool(
            name="analyze_topology",
            description="Analyze network topology: node/edge counts, cycles, islands, radial check, source bus.",
            inputSchema={
                "type": "object",
                "properties": {
                    "system_path": {
                        "type": "string",
                        "description": "Path to the distribution system JSON file",
                    }
                },
                "required": ["system_path"],
            },
        ),
        Tool(
            name="validate_connectivity",
            description="Validate that all buses are reachable from the source bus. Identifies islands and unreachable components.",
            inputSchema={
                "type": "object",
                "properties": {
                    "system_path": {
                        "type": "string",
                        "description": "Path to the distribution system JSON file",
                    }
                },
                "required": ["system_path"],
            },
        ),
        Tool(
            name="get_component_details",
            description="Get detailed information about a specific component by UUID or name.",
            inputSchema={
                "type": "object",
                "properties": {
                    "system_path": {
                        "type": "string",
                        "description": "Path to the distribution system JSON file",
                    },
                    "identifier": {
                        "type": "string",
                        "description": "Component UUID or name",
                    },
                },
                "required": ["system_path", "identifier"],
            },
        ),
        Tool(
            name="find_orphaned_components",
            description="Find components without substation or feeder assignments.",
            inputSchema={
                "type": "object",
                "properties": {
                    "system_path": {
                        "type": "string",
                        "description": "Path to the distribution system JSON file",
                    }
                },
                "required": ["system_path"],
            },
        ),
        Tool(
            name="get_component_relationships",
            description="Get parent and child relationships for a component.",
            inputSchema={
                "type": "object",
                "properties": {
                    "system_path": {
                        "type": "string",
                        "description": "Path to the distribution system JSON file",
                    },
                    "component_id": {
                        "type": "string",
                        "description": "Component UUID or name",
                    },
                },
                "required": ["system_path", "component_id"],
            },
        ),
        # Utility tools
        Tool(
            name="export_subsystem_by_buses",
            description="Extract a subsystem containing specified buses and their connected components.",
            inputSchema={
                "type": "object",
                "properties": {
                    "system_path": {
                        "type": "string",
                        "description": "Path to the distribution system JSON file",
                    },
                    "bus_names": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of bus names to include",
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Path to save the subsystem",
                    },
                    "name": {
                        "type": "string",
                        "description": "Name for the subsystem",
                    },
                    "keep_timeseries": {
                        "type": "boolean",
                        "description": "Preserve time series (default: true)",
                        "default": True,
                    },
                },
                "required": ["system_path", "bus_names", "output_path", "name"],
            },
        ),
        Tool(
            name="get_time_series_summary",
            description="Get summary of all time series data in the system.",
            inputSchema={
                "type": "object",
                "properties": {
                    "system_path": {
                        "type": "string",
                        "description": "Path to the distribution system JSON file",
                    }
                },
                "required": ["system_path"],
            },
        ),
        # Documentation/Knowledge tools
        Tool(
            name="search_gdm_documentation",
            description="Search grid-data-models documentation for relevant content. Returns snippets from docs, API references, and notebooks.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (e.g., 'how to create a bus', 'time series', 'phase')",
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 5)",
                        "default": 5,
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="get_api_reference",
            description="Get detailed API reference for a specific component class (e.g., DistributionBus, DistributionLoad). Returns fields, methods, and usage examples.",
            inputSchema={
                "type": "object",
                "properties": {
                    "component_name": {
                        "type": "string",
                        "description": "Name of the component class (e.g., 'DistributionBus')",
                    }
                },
                "required": ["component_name"],
            },
        ),
        Tool(
            name="get_code_examples",
            description="Get code examples for a specific topic from documentation notebooks.",
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "Topic to search for (e.g., 'creating a bus', 'time series', 'plotting')",
                    }
                },
                "required": ["topic"],
            },
        ),
        Tool(
            name="list_available_components",
            description="List all available distribution component types with descriptions.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="get_component_fields",
            description="Get detailed field information for a specific component type, including types, requirements, and defaults.",
            inputSchema={
                "type": "object",
                "properties": {
                    "component_name": {
                        "type": "string",
                        "description": "Name of the component class (e.g., 'DistributionBus')",
                    }
                },
                "required": ["component_name"],
            },
        ),
    ]


# Tool dispatch map
_TOOL_HANDLERS: dict[str, Any] = {
    "diagnose_system": lambda args: _diagnose_system(args),
    "suggest_fixes": lambda args: _suggest_fixes(args),
    "apply_fixes": lambda args: _apply_fixes(args),
    "merge_systems": lambda args: _merge_systems(args),
    "split_by_substation": lambda args: _split_by_substation(args),
    "split_by_feeder": lambda args: _split_by_feeder(args),
    "get_system_summary": lambda args: _get_system_summary(args),
    "query_components": lambda args: _query_components(args),
    "analyze_topology": lambda args: _analyze_topology(args),
    "validate_connectivity": lambda args: _validate_connectivity(args),
    "get_component_details": lambda args: _get_component_details(args),
    "find_orphaned_components": lambda args: _find_orphaned_components(args),
    "get_component_relationships": lambda args: _get_component_relationships(args),
    "export_subsystem_by_buses": lambda args: _export_subsystem_by_buses(args),
    "get_time_series_summary": lambda args: _get_time_series_summary(args),
    "search_gdm_documentation": lambda args: _search_gdm_documentation(args),
    "get_api_reference": lambda args: _get_api_reference(args),
    "get_code_examples": lambda args: _get_code_examples(args),
    "list_available_components": lambda args: _list_available_components(args),
    "get_component_fields": lambda args: _get_component_fields(args),
}


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls from MCP clients."""
    try:
        logger.info(f"Tool called: {name} with arguments: {arguments}")

        handler = _TOOL_HANDLERS.get(name)
        if handler is not None:
            result = await handler(arguments)
        else:
            result = {"error": f"Unknown tool: {name}"}

        return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]

    except GDMMCPException as e:
        logger.error(f"GDM MCP error in {name}: {str(e)}")
        return [TextContent(type="text", text=json.dumps({"error": str(e)}, indent=2))]
    except Exception as e:
        logger.error(f"Unexpected error in {name}: {str(e)}", exc_info=True)
        return [
            TextContent(
                type="text", text=json.dumps({"error": f"Unexpected error: {str(e)}"}, indent=2)
            )
        ]


# Tool implementations
async def _diagnose_system(args: dict) -> dict:
    """Diagnose system validation errors."""
    system_path = args["system_path"]
    system = DistributionSystem.from_json(system_path)
    report = diagnose_system(system)
    return report.model_dump()


async def _suggest_fixes(args: dict) -> dict:
    """Suggest fixes for validation errors."""
    system_path = args["system_path"]
    system = DistributionSystem.from_json(system_path)
    report = diagnose_system(system)
    suggestions = suggest_fixes(report)
    return {
        "validation_report": report.model_dump(),
        "suggestions": [s.model_dump() for s in suggestions],
    }


async def _apply_fixes(args: dict) -> dict:
    """Apply fixes to a system."""
    system_path = args["system_path"]
    output_path = args["output_path"]
    auto_approve = args.get("auto_approve", False)

    system = DistributionSystem.from_json(system_path)
    report = diagnose_system(system)
    suggestions = suggest_fixes(report)

    fixed_system, fix_result = apply_fixes(system, suggestions, auto_approve)

    # Save fixed system
    fixed_system.to_json(output_path, overwrite=True)

    return {
        "fix_result": fix_result.model_dump(),
        "output_path": output_path,
    }


async def _merge_systems(args: dict) -> dict:
    """Merge multiple systems."""
    system_paths = args["system_paths"]
    output_path = args["output_path"]
    name = args["name"]
    strict = args.get("strict", True)

    systems = [DistributionSystem.from_json(path) for path in system_paths]
    merged_system, report = merge_systems(systems, name, strict)

    # Save merged system
    merged_system.to_json(output_path, overwrite=True)

    return {
        "merge_report": report.model_dump(),
        "output_path": output_path,
    }


async def _split_by_substation(args: dict) -> dict:
    """Split system by substation."""
    system_path = args["system_path"]
    output_dir = args["output_dir"]
    keep_timeseries = args.get("keep_timeseries", True)
    include_unassigned = args.get("include_unassigned", True)

    system = DistributionSystem.from_json(system_path)
    subsystems, report = split_by_substation(system, keep_timeseries, include_unassigned)

    # Save subsystems
    output_dir_path = Path(output_dir)
    output_dir_path.mkdir(parents=True, exist_ok=True)

    output_files = {}
    for name, subsystem in subsystems.items():
        output_file = output_dir_path / f"{name}.json"
        subsystem.to_json(str(output_file), overwrite=True)
        output_files[name] = str(output_file)

    return {
        "split_report": report.model_dump(),
        "output_files": output_files,
    }


async def _split_by_feeder(args: dict) -> dict:
    """Split system by feeder."""
    system_path = args["system_path"]
    output_dir = args["output_dir"]
    keep_timeseries = args.get("keep_timeseries", True)
    include_unassigned = args.get("include_unassigned", True)

    system = DistributionSystem.from_json(system_path)
    subsystems, report = split_by_feeder(system, keep_timeseries, include_unassigned)

    # Save subsystems
    output_dir_path = Path(output_dir)
    output_dir_path.mkdir(parents=True, exist_ok=True)

    output_files = {}
    for name, subsystem in subsystems.items():
        output_file = output_dir_path / f"{name}.json"
        subsystem.to_json(str(output_file), overwrite=True)
        output_files[name] = str(output_file)

    return {
        "split_report": report.model_dump(),
        "output_files": output_files,
    }


async def _get_system_summary(args: dict) -> dict:
    """Get system summary."""
    system_path = args["system_path"]
    system = DistributionSystem.from_json(system_path)
    summary = get_system_summary(system)
    return summary.model_dump()


async def _query_components(args: dict) -> dict:
    """Query components with filters."""
    system_path = args["system_path"]
    system = DistributionSystem.from_json(system_path)

    filters = ComponentFilter(
        component_types=args.get("component_types"),
        substation=args.get("substation"),
        feeder=args.get("feeder"),
        phases=args.get("phases"),
        in_service=args.get("in_service"),
        has_timeseries=args.get("has_timeseries"),
    )

    components = query_components(system, filters)
    return {"components": [c.model_dump() for c in components], "count": len(components)}


async def _analyze_topology(args: dict) -> dict:
    """Analyze topology."""
    system_path = args["system_path"]
    system = DistributionSystem.from_json(system_path)
    metrics = analyze_topology(system)
    return metrics.model_dump()


async def _validate_connectivity(args: dict) -> dict:
    """Validate connectivity."""
    system_path = args["system_path"]
    system = DistributionSystem.from_json(system_path)
    return validate_connectivity(system)


async def _get_component_details(args: dict) -> dict:
    """Get component details."""
    system_path = args["system_path"]
    identifier = args["identifier"]
    system = DistributionSystem.from_json(system_path)
    return get_component_details(system, identifier)


async def _find_orphaned_components(args: dict) -> dict:
    """Find orphaned components."""
    system_path = args["system_path"]
    system = DistributionSystem.from_json(system_path)
    orphaned = find_orphaned_components(system)
    return {"orphaned_components": [c.model_dump() for c in orphaned], "count": len(orphaned)}


async def _get_component_relationships(args: dict) -> dict:
    """Get component relationships."""
    system_path = args["system_path"]
    component_id = args["component_id"]
    system = DistributionSystem.from_json(system_path)
    relationships = get_component_relationships(system, component_id)
    return {
        "parents": [p.model_dump() for p in relationships.get("parents", [])],
        "children": [c.model_dump() for c in relationships.get("children", [])],
    }


async def _export_subsystem_by_buses(args: dict) -> dict:
    """Export subsystem by buses."""
    system_path = args["system_path"]
    bus_names = args["bus_names"]
    output_path = args["output_path"]
    name = args["name"]
    keep_timeseries = args.get("keep_timeseries", True)

    system = DistributionSystem.from_json(system_path)
    subsystem = export_subsystem_by_buses(system, bus_names, name, keep_timeseries)

    # Save subsystem
    subsystem.to_json(output_path, overwrite=True)

    summary = get_system_summary(subsystem)
    return {
        "output_path": output_path,
        "subsystem_summary": summary.model_dump(),
    }


async def _get_time_series_summary(args: dict) -> dict:
    """Get time series summary."""
    system_path = args["system_path"]
    system = DistributionSystem.from_json(system_path)
    return get_time_series_summary(system)


# Documentation/Knowledge handlers
async def _search_gdm_documentation(args: dict) -> dict:
    """Search GDM documentation."""
    query = args["query"]
    max_results = args.get("max_results", 5)

    results = search_documentation(query, max_results)
    return {"query": query, "results": [r.model_dump() for r in results]}


async def _get_api_reference(args: dict) -> dict:
    """Get API reference for a component."""
    component_name = args["component_name"]
    result = get_api_ref(component_name)
    return result.model_dump()


async def _get_code_examples(args: dict) -> dict:
    """Get code examples for a topic."""
    topic = args["topic"]
    examples = get_code_ex(topic)
    return {"topic": topic, "examples": [e.model_dump() for e in examples]}


async def _list_available_components(args: dict) -> dict:
    """List available components."""
    components = list_components_doc()
    return {"components": [c.model_dump() for c in components]}


async def _get_component_fields(args: dict) -> dict:
    """Get component field information."""
    component_name = args["component_name"]
    fields = get_fields_doc(component_name)
    return {"component_name": component_name, "fields": fields}


def _run_server(
    host: Annotated[str, typer.Option(help="Server host")] = "localhost",
    port: Annotated[int, typer.Option(help="Server port")] = 8000,
    log_level: Annotated[str, typer.Option(help="Logging level")] = "INFO",
    allow_auto_fix: Annotated[
        bool, typer.Option("--allow-auto-fix", help="Allow auto-fix operations")
    ] = False,
):
    """Start the GDM MCP server."""
    # Set log level
    logging.getLogger("gdm_mcp").setLevel(log_level.upper())

    logger.info(f"Starting GDM MCP Server v{__version__}")
    logger.info(f"Host: {host}, Port: {port}")
    logger.info(f"Auto-fix allowed: {allow_auto_fix}")

    # Run the server
    import asyncio

    async def run():
        async with stdio_server() as (read_stream, write_stream):
            await app.run(read_stream, write_stream, app.create_initialization_options())

    asyncio.run(run())


def main():
    typer.run(_run_server)


if __name__ == "__main__":
    main()
