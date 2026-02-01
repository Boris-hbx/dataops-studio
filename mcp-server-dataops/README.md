# MCP Server for DataOps Studio

An MCP (Model Context Protocol) server that connects Claude Desktop / Claude Code to the DataOps Studio backend, enabling natural language queries for pipeline status, quality rules, cost analysis, data lineage, and more.

## Features

- **14 Tools** -- Query pipelines, quality rules, cost data, lineage, dashboard stats, team metrics, annotation tasks, and trigger config reloads
- **5 Resources** -- Read-only data sources for pipelines, quality rules, lineage, dashboard, and teams
- **Error handling** -- All API failures return structured error messages without crashing

## Prerequisites

- Node.js >= 18
- DataOps Studio backend running at `http://localhost:8000`

## Installation

```bash
cd mcp-server-dataops
npm install
npm run build
```

## Configuration

### Claude Code

The project includes `.claude/mcp.json` which configures the MCP server automatically when you open the repository with Claude Code. No manual setup is required.

Alternatively, add the server to your global Claude Code MCP config:

```json
{
  "mcpServers": {
    "dataops-studio": {
      "command": "node",
      "args": ["/absolute/path/to/mcp-server-dataops/dist/index.js"],
      "env": {
        "DATAOPS_API_BASE": "http://localhost:8000"
      }
    }
  }
}
```

### Claude Desktop

Edit `claude_desktop_config.json`:

- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "dataops-studio": {
      "command": "node",
      "args": ["C:\\Project\\demo\\dataops-studio\\mcp-server-dataops\\dist\\index.js"],
      "env": {
        "DATAOPS_API_BASE": "http://localhost:8000"
      }
    }
  }
}
```

On macOS, replace the `args` path with:

```json
"args": ["/Users/<you>/path/to/mcp-server-dataops/dist/index.js"]
```

## Available Tools

### Pipeline Management

| Tool | Description |
|------|-------------|
| `list_pipelines` | List all pipelines, filter by status/owner |
| `get_pipeline_detail` | Get pipeline details and recent executions |
| `list_pipeline_executions` | Get execution history |

### Quality Monitoring

| Tool | Description |
|------|-------------|
| `get_quality_rules` | Get quality rules with 30-day pass rates |
| `get_quality_checks` | Get quality check results |

### Cost Analysis

| Tool | Description |
|------|-------------|
| `get_cost_summary` | Get cost overview and per-pipeline breakdown |
| `get_cost_trend` | Get 30-day daily cost trend |

### Data Lineage

| Tool | Description |
|------|-------------|
| `get_data_lineage` | Get data lineage graph (nodes + edges) |

### Dashboard

| Tool | Description |
|------|-------------|
| `get_dashboard_stats` | Get key dashboard metrics |
| `get_dashboard_alerts` | Get recent alerts |

### Team Management

| Tool | Description |
|------|-------------|
| `get_team_stats` | Get team performance statistics |

### Annotation (RLHF)

| Tool | Description |
|------|-------------|
| `list_annotation_tasks` | List annotation tasks with progress |
| `get_annotation_quality` | Get annotation quality metrics |

### Configuration

| Tool | Description |
|------|-------------|
| `reload_config` | Hot-reload YAML configuration files |

## Available Resources

| URI | Description |
|-----|-------------|
| `dataops://pipelines` | All pipelines directory |
| `dataops://quality/rules` | Quality rules directory |
| `dataops://lineage` | Data lineage graph |
| `dataops://dashboard` | Dashboard snapshot (stats + alerts) |
| `dataops://teams` | Team directory with metrics |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATAOPS_API_BASE` | `http://localhost:8000` | Backend API base URL |

## Development

```bash
# Build TypeScript to dist/
npm run build

# Build and run (useful during development)
npm run dev

# Start the compiled server directly
npm start
```

All logging goes to `stderr` because `stdout` is reserved for the MCP stdio transport. Use `console.error()` for debug output.

## Architecture

```
┌─────────────────────┐     stdio (JSON-RPC)     ┌──────────────────────┐
│  Claude Desktop /   │◄────────────────────────►│  MCP Server          │
│  Claude Code        │                           │  (mcp-server-dataops)│
└─────────────────────┘                           └──────────┬───────────┘
                                                             │ HTTP
                                                             ▼
                                                  ┌──────────────────────┐
                                                  │  FastAPI Backend     │
                                                  │  (localhost:8000)    │
                                                  └──────────────────────┘
```

The MCP server acts as a bridge between Claude's MCP protocol (communicated over stdio using JSON-RPC) and the DataOps Studio FastAPI backend (communicated over HTTP REST). Each MCP tool maps to one or more backend API endpoints. Resources provide read-only snapshots of key data sets, aggregating API responses into a single document.
