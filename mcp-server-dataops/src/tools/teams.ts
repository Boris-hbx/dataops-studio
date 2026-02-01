import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { apiGet } from "../client.js";

export function registerTeamTools(server: McpServer): void {
  server.registerTool("get_team_stats", {
    description:
      "Get performance statistics for all teams including pipeline counts, costs, success rates, and quality scores.",
    inputSchema: {},
  }, async () => {
    try {
      const result = await apiGet("/api/teams/stats");
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
