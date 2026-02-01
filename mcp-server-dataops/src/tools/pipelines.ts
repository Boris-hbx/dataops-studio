import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { apiGet } from "../client.js";

export function registerPipelineTools(server: McpServer): void {
  server.registerTool("list_pipelines", {
    description:
      "List all data pipelines. Optionally filter by status or owner.",
    inputSchema: {
      status: z
        .string()
        .optional()
        .describe(
          "Filter by pipeline status, e.g. 'active', 'paused', 'degraded'",
        ),
      owner: z
        .string()
        .optional()
        .describe("Filter by pipeline owner name"),
    },
  }, async ({ status, owner }) => {
    try {
      const params: Record<string, string> = {};
      if (status) params.status = status;
      if (owner) params.owner = owner;
      const result = await apiGet(
        "/api/pipelines",
        Object.keys(params).length > 0 ? params : undefined,
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

  server.registerTool("get_pipeline_detail", {
    description:
      "Get detailed information about a specific pipeline including recent executions.",
    inputSchema: {
      id: z.string().describe("Pipeline ID"),
    },
  }, async ({ id }) => {
    try {
      const result = await apiGet(`/api/pipelines/${id}`);
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

  server.registerTool("list_pipeline_executions", {
    description: "Get execution history for a specific pipeline.",
    inputSchema: {
      id: z.string().describe("Pipeline ID"),
      limit: z
        .string()
        .optional()
        .describe(
          "Maximum number of executions to return, default 50",
        ),
    },
  }, async ({ id, limit }) => {
    try {
      const params: Record<string, string> = {};
      if (limit) params.limit = limit;
      const result = await apiGet(
        `/api/pipelines/${id}/executions`,
        Object.keys(params).length > 0 ? params : undefined,
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
