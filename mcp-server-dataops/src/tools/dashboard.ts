import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { apiGet } from "../client.js";

export function registerDashboardTools(server: McpServer): void {
  server.registerTool("get_dashboard_stats", {
    description:
      "Get key dashboard metrics including active pipelines, quality score, cost, and alert counts.",
    inputSchema: {},
  }, async () => {
    try {
      const result = await apiGet("/api/dashboard/stats");
      return {
        content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
      };
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : String(error);
      return {
        content: [{ type: "text", text: `Error: ${message}` }],
        isError: true,
      };
    }
  });

  server.registerTool("get_dashboard_alerts", {
    description: "Get recent alerts from the dashboard.",
    inputSchema: {
      limit: z.string().optional().describe(
        "Maximum number of alerts to return, default 20",
      ),
    },
  }, async (args) => {
    try {
      const { limit } = args;
      const result = await apiGet(
        "/api/dashboard/alerts",
        limit ? { limit } : undefined,
      );
      return {
        content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
      };
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : String(error);
      return {
        content: [{ type: "text", text: `Error: ${message}` }],
        isError: true,
      };
    }
  });
}
