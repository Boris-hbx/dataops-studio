import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { apiGet } from "../client.js";

/**
 * Register annotation-related MCP Tools for DataOps Studio.
 *
 * - list_annotation_tasks  — list all RLHF annotation tasks
 * - get_annotation_quality — retrieve annotation quality metrics
 */
export function registerAnnotationTools(server: McpServer): void {
  // ── Tool 1: list_annotation_tasks ────────────────────────────────────
  server.registerTool(
    "list_annotation_tasks",
    {
      description:
        "List all RLHF annotation tasks with their progress and quality metrics.",
      inputSchema: {},
    },
    async () => {
      try {
        const result = await apiGet("/api/annotation/tasks");
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

  // ── Tool 2: get_annotation_quality ───────────────────────────────────
  server.registerTool(
    "get_annotation_quality",
    {
      description:
        "Get annotation quality metrics including approval rates, inter-annotator agreement (Fleiss Kappa), and per-task-type breakdown.",
      inputSchema: {},
    },
    async () => {
      try {
        const result = await apiGet("/api/annotation/quality");
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
