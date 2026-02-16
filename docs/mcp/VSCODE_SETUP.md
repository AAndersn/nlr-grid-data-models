# Using Grid Data Models MCP Server with VS Code

This guide explains how to use the Grid Data Models MCP server with GitHub Copilot Agent Mode in VS Code.

## Prerequisites

1. **VS Code**: Latest version with GitHub Copilot extension
2. **GitHub Copilot**: Active subscription with Agent Mode support
3. **Package Installed**: `grid-data-models-mcp` must be installed

## Setup

### 1. Install the Package

```bash
cd /Users/alatif/Documents/GitHub/grid-data-models-mcp
pip install -e .
```

### 2. Verify Installation

```bash
which gdm-mcp-server
gdm-mcp-server --help
```

### 3. Configure VS Code

The MCP server is already configured in `.vscode/settings.json`:

```json
{
  "github.copilot.chat.experimental.servers": [
    {
      "name": "grid-data-models",
      "command": "gdm-mcp-server",
      "env": {
        "GDM_REPO_PATH": "/Users/alatif/Documents/GitHub/grid-data-models"
      }
    }
  ]
}
```

### 4. Restart VS Code

Close and reopen VS Code to load the MCP server configuration.

### 5. Verify MCP Server Integration

After restarting:
- Open Copilot Chat (Cmd+Shift+I / Ctrl+Shift+I)
- Type `@` and you should see `@grid-data-models` in the available agent list
- Select `@grid-data-models` to interact with the MCP server tools

## Usage

GitHub Copilot's Agent Mode allows it to interact with MCP servers. Once configured, you can use the `@grid-data-models` agent to interact with your distribution system models:

### Example Prompts

**Validation & Diagnostics:**
```
@grid-data-models diagnose the system in model.json for validation errors

@grid-data-models suggest fixes for the validation errors in my system

@grid-data-models apply automatic fixes to resolve validation issues
```

**System Operations:**
```
@grid-data-models merge system1.json and system2.json into combined.json

@grid-data-models split the system in large_model.json by substation

@grid-data-models split the system by feeders
```

**Inspection & Analysis:**
```
@grid-data-models give me a summary of the components in system.json

@grid-data-models query all transformers in the SUBSTATION_1 substation

@grid-data-models analyze the topology and check for connectivity issues

@grid-data-models find orphaned components in my system
```

**Documentation & Learning:**
```
@grid-data-models search the documentation for time series examples

@grid-data-models show me the API reference for DistributionBus

@grid-data-models what fields are required for DistributionLoad?

@grid-data-models give me code examples for creating a transformer
```

## Available Tools

The MCP server exposes 21 tools:

### Validation (3 tools)
- `diagnose_system` - Identify validation errors
- `suggest_fixes` - Get fix suggestions
- `apply_fixes` - Auto-apply fixes

### Operations (3 tools)
- `merge_systems` - Merge multiple systems
- `split_by_substation` - Split by substation
- `split_by_feeder` - Split by feeder

### Inspection (6 tools)
- `get_system_summary` - Component counts and overview
- `query_components` - Filter and query components
- `analyze_topology` - Network topology analysis
- `get_component_details` - Detailed component info
- `validate_connectivity` - Check reachability
- `find_orphaned_components` - Find unassigned components

### Utilities (4 tools)
- `export_subsystem_by_buses` - Extract subsystem
- `get_time_series_summary` - Time series overview
- `get_component_relationships` - Parent/child relationships

### Documentation (5 tools)
- `search_gdm_documentation` - Search docs
- `get_api_reference` - API reference
- `get_code_examples` - Usage examples
- `list_available_components` - List components
- `get_component_fields` - Field information

## Troubleshooting

### Server Not Connecting

1. Check the command exists:
   ```bash
   which gdm-mcp-server
   ```

2. Test the server manually:
   ```bash
   gdm-mcp-server
   ```

3. Check VS Code output panel:
   - Open Command Palette (Cmd+Shift+P)
   - Select "View: Toggle Output"
   - Choose "GitHub Copilot" from dropdown

### Server Crashes

Check logs in VS Code:
1. Open Command Palette
2. "Developer: Show Logs"
3. Look for MCP-related errors

### Tools Not Available

1. Verify package is installed:
   ```bash
   python -c "import gdm_mcp; print(gdm_mcp.__version__)"
   ```

2. Reinstall if needed:
   ```bash
   pip install --force-reinstall -e .
   ```

### Documentation Search Returns No Results

Set the correct repository path:
```bash
export GDM_REPO_PATH="/Users/alatif/Documents/GitHub/grid-data-models"
```

Or update `.vscode/settings.json` with the correct path.

## Tips

1. **Use @ Mentions**: Start prompts with `@grid-data-models` to explicitly use the MCP server
2. **Be Specific**: Include file paths and specific component names
3. **Iterative Workflow**: Break complex tasks into multiple prompts
4. **Reference Files**: Use file paths relative to workspace root

## Examples

### Complete Workflow

```
User: @grid-data-models I have a system file at tests/data/system.json. 
      Can you diagnose it for validation errors?

Copilot: [Uses diagnose_system tool]
         Found 5 validation errors:
         1. Bus 'bus_1' missing voltage
         2. Transformer 'xfmr_1' has invalid winding configuration
         ...

User: @grid-data-models Can you suggest fixes for these errors?

Copilot: [Uses suggest_fixes tool]
         Suggestions for fixing validation errors:
         1. Bus 'bus_1': Set voltage to 12.47 kV (common distribution voltage)
         ...

User: @grid-data-models Apply the high-confidence fixes automatically

Copilot: [Uses apply_fixes tool]
         Applied 3 fixes successfully. 2 low-confidence fixes skipped.
         Download fixed system: [provides JSON]
```

## Configuration Options

### Environment Variables

Set in `.vscode/settings.json` under `env`:

- `GDM_REPO_PATH`: Path to grid-data-models repository (for documentation search)
- `MCP_LOG_LEVEL`: Set to `DEBUG` for verbose logging

### Custom Settings

Update `.vscode/settings.json`:

```json
{
  "github.copilot.chat.experimental.servers": [
    {
      "name": "grid-data-models",
      "command": "gdm-mcp-server",
      "args": ["--log-level", "debug"],
      "env": {
        "GDM_REPO_PATH": "/path/to/grid-data-models",
        "MCP_LOG_LEVEL": "DEBUG"
      }
    }
  ]
}
```

## Support

For issues:
- GitHub Issues: https://github.com/NREL-Distribution-Suites/grid-data-models-mcp/issues
- Documentation: https://github.com/NREL-Distribution-Suites/grid-data-models-mcp

## Notes

- MCP server support via GitHub Copilot Agent Mode
- Requires GitHub Copilot subscription
- Server runs locally and processes files on your machine
- No data is sent to external servers except standard Copilot API calls
- Use `@grid-data-models` prefix to invoke the MCP server in Copilot Chat
