import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { apiGet } from "../client.js";

/**
 * Register all MCP Resources for DataOps Studio.
 *
 * Each resource exposes a read-only data snapshot from the backend API
 * via the `dataops://` URI scheme.
 */
export function registerResources(server: McpServer): void {
  // ── Resource 1: dataops://pipelines ────────────────────────────────
  server.resource(
    "pipelines",
    "dataops://pipelines",
    {
      description:
        "Directory of all data pipelines with status, owner, and performance metrics",
      mimeType: "application/json",
    },
    async (uri) => {
      try {
        const data = await apiGet("/api/pipelines");
        return {
          contents: [
            {
              uri: uri.href,
              mimeType: "application/json" as const,
              text: JSON.stringify(data, null, 2),
            },
          ],
        };
      } catch (err: unknown) {
        const message = err instanceof Error ? err.message : String(err);
        throw new Error(`Failed to read pipelines resource: ${message}`);
      }
    },
  );

  // ── Resource 2: dataops://quality/rules ────────────────────────────
  server.resource(
    "quality-rules",
    "dataops://quality/rules",
    {
      description: "All quality rule definitions with 30-day pass rates",
      mimeType: "application/json",
    },
    async (uri) => {
      try {
        const data = await apiGet("/api/quality/rules");
        return {
          contents: [
            {
              uri: uri.href,
              mimeType: "application/json" as const,
              text: JSON.stringify(data, null, 2),
            },
          ],
        };
      } catch (err: unknown) {
        const message = err instanceof Error ? err.message : String(err);
        throw new Error(`Failed to read quality-rules resource: ${message}`);
      }
    },
  );

  // ── Resource 3: dataops://lineage ──────────────────────────────────
  server.resource(
    "lineage",
    "dataops://lineage",
    {
      description: "Complete data lineage graph with nodes and edges",
      mimeType: "application/json",
    },
    async (uri) => {
      try {
        const data = await apiGet("/api/lineage");
        return {
          contents: [
            {
              uri: uri.href,
              mimeType: "application/json" as const,
              text: JSON.stringify(data, null, 2),
            },
          ],
        };
      } catch (err: unknown) {
        const message = err instanceof Error ? err.message : String(err);
        throw new Error(`Failed to read lineage resource: ${message}`);
      }
    },
  );

  // ── Resource 4: dataops://dashboard ────────────────────────────────
  // Aggregates two API calls (stats + alerts) into a single resource.
  server.resource(
    "dashboard",
    "dataops://dashboard",
    {
      description:
        "Dashboard snapshot with key metrics and recent alerts",
      mimeType: "application/json",
    },
    async (uri) => {
      try {
        const [stats, alerts] = await Promise.all([
          apiGet("/api/dashboard/stats"),
          apiGet("/api/dashboard/alerts"),
        ]);
        return {
          contents: [
            {
              uri: uri.href,
              mimeType: "application/json" as const,
              text: JSON.stringify({ stats, alerts }, null, 2),
            },
          ],
        };
      } catch (err: unknown) {
        const message = err instanceof Error ? err.message : String(err);
        throw new Error(`Failed to read dashboard resource: ${message}`);
      }
    },
  );

  // ── Resource 5: dataops://teams ────────────────────────────────────
  server.resource(
    "teams",
    "dataops://teams",
    {
      description:
        "Team directory with pipeline assignments and performance metrics",
      mimeType: "application/json",
    },
    async (uri) => {
      try {
        const data = await apiGet("/api/teams/stats");
        return {
          contents: [
            {
              uri: uri.href,
              mimeType: "application/json" as const,
              text: JSON.stringify(data, null, 2),
            },
          ],
        };
      } catch (err: unknown) {
        const message = err instanceof Error ? err.message : String(err);
        throw new Error(`Failed to read teams resource: ${message}`);
      }
    },
  );
}
