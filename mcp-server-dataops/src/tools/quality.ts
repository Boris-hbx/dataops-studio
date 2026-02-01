import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { apiGet } from "../client.js";

export function registerQualityTools(server: McpServer): void {
  server.registerTool("get_quality_rules", {
    description: "Get all quality rules with their 30-day pass rates.",
    inputSchema: {},
  }, async () => {
    try {
      const result = await apiGet("/api/quality/rules");
      return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : String(error);
      return { content: [{ type: "text", text: `Error: ${message}` }], isError: true };
    }
  });

  server.registerTool("get_quality_checks", {
    description: "Get quality check results. Returns recent check executions.",
    inputSchema: {
      limit: z.string().optional().describe("Maximum number of checks to return, default 100"),
    },
  }, async ({ limit }) => {
    try {
      const result = await apiGet("/api/quality/checks", limit ? { limit } : undefined);
      return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : String(error);
      return { content: [{ type: "text", text: `Error: ${message}` }], isError: true };
    }
  });
}
