#!/usr/bin/env node

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";

import { registerPipelineTools } from "./tools/pipelines.js";
import { registerQualityTools } from "./tools/quality.js";
import { registerCostTools } from "./tools/cost.js";
import { registerLineageTools } from "./tools/lineage.js";
import { registerDashboardTools } from "./tools/dashboard.js";
import { registerTeamTools } from "./tools/teams.js";
import { registerAnnotationTools } from "./tools/annotation.js";
import { registerConfigTools } from "./tools/config.js";
import { registerResources } from "./resources/index.js";

const server = new McpServer({
  name: "dataops-studio",
  version: "1.0.0",
});

// Register all tools (14 total)
registerPipelineTools(server);    // 3 tools
registerQualityTools(server);     // 2 tools
registerCostTools(server);        // 2 tools
registerLineageTools(server);     // 1 tool
registerDashboardTools(server);   // 2 tools
registerTeamTools(server);        // 1 tool
registerAnnotationTools(server);  // 2 tools
registerConfigTools(server);      // 1 tool

// Register all resources (5 total)
registerResources(server);

// Start server with stdio transport
async function main(): Promise<void> {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("DataOps Studio MCP Server started (stdio transport)");
}

main().catch((error) => {
  console.error("Fatal error starting MCP server:", error);
  process.exit(1);
});
