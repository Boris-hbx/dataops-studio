import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { apiGet } from "../client.js";

/**
 * Register agent-annotation-related MCP Tools for DataOps Studio.
 *
 * - get_agent_annotation_stats      — get annotation stats (total sessions, tool calls, annotations, rate)
 * - list_agent_sessions             — list all agent sessions
 * - get_agent_session_tool_calls    — get tool calls with their annotations for a specific session
 */
export function registerAgentAnnotationTools(server: McpServer): void {
  // ── Tool 1: get_agent_annotation_stats ──────────────────────────────
  server.registerTool(
    "get_agent_annotation_stats",
    {
      description:
        "Get agent annotation statistics including total sessions, tool calls, annotations, and annotation rate.",
      inputSchema: {},
    },
    async () => {
      try {
        const result = await apiGet("/api/agent-annotation/stats");
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

  // ── Tool 2: list_agent_sessions ─────────────────────────────────────
  server.registerTool(
    "list_agent_sessions",
    {
      description:
        "List all agent sessions with their metadata.",
      inputSchema: {},
    },
    async () => {
      try {
        const result = await apiGet("/api/agent-annotation/sessions");
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

  // ── Tool 3: get_agent_session_tool_calls ────────────────────────────
  server.registerTool(
    "get_agent_session_tool_calls",
    {
      description:
        "Get tool calls with their annotations for a specific agent session.",
      inputSchema: {
        session_id: z.string().describe("Agent session ID"),
      },
    },
    async ({ session_id }) => {
      try {
        const result = await apiGet(
          `/api/agent-annotation/sessions/${session_id}/tool-calls`,
        );
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
