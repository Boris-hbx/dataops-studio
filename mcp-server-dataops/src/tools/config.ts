import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { apiGet } from "../client.js";

/**
 * Register configuration-related MCP Tools for DataOps Studio.
 *
 * - reload_config — trigger a hot reload of all YAML configuration files
 */
export function registerConfigTools(server: McpServer): void {
  // ── Tool: reload_config ──────────────────────────────────────────────
  server.registerTool(
    "reload_config",
    {
      description:
        "Trigger a hot reload of all YAML configuration files (pipelines, quality rules, annotation tasks). Returns the count of loaded items.",
      inputSchema: {},
    },
    async () => {
      try {
        const result = await apiGet("/api/config/reload");
        return {
          content: [
            { type: "text", text: JSON.stringify(result, null, 2) },
          ],
        };
      } catch (error: unknown) {
        const message =
          error instanceof Error ? error.message : String(error);
        return {
          content: [{ type: "text", text: `Error: ${message}` }],
          isError: true,
        };
      }
    },
  );
}
