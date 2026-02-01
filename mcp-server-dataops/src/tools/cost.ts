import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { apiGet } from "../client.js";

export function registerCostTools(server: McpServer): void {
  server.registerTool("get_cost_summary", {
    description: "Get cost overview with total 30-day cost and per-pipeline breakdown.",
    inputSchema: {},
  }, async () => {
    try {
      const result = await apiGet("/api/cost/summary");
      return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : String(error);
      return { content: [{ type: "text", text: `Error: ${message}` }], isError: true };
    }
  });

  server.registerTool("get_cost_trend", {
    description: "Get 30-day daily cost trend data.",
    inputSchema: {},
  }, async () => {
    try {
      const result = await apiGet("/api/cost/trend");
      return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : String(error);
      return { content: [{ type: "text", text: `Error: ${message}` }], isError: true };
    }
  });
}
