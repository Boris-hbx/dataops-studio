import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { apiGet } from "../client.js";

export function registerLineageTools(server: McpServer): void {
  server.registerTool("get_data_lineage", {
    description:
      "Get the data lineage graph showing nodes (tables/datasets) and edges (data flows between them).",
    inputSchema: {},
  }, async () => {
    try {
      const result = await apiGet("/api/lineage");
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
