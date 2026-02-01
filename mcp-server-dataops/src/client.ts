/**
 * HTTP client for DataOps Studio backend API.
 *
 * Uses Node.js built-in fetch (Node 18+).
 * All logging goes to stderr because stdout is reserved for MCP stdio transport.
 */

const BASE_URL = process.env.DATAOPS_API_BASE || "http://localhost:8000";

/**
 * Perform a GET request against the DataOps backend and return parsed JSON.
 *
 * @param path   - API path, e.g. "/api/pipelines"
 * @param params - Optional query-string key/value pairs
 * @returns Parsed JSON body typed as T
 * @throws Error on network failure, non-2xx response, or JSON parse failure
 */
export async function apiGet<T>(
  path: string,
  params?: Record<string, string>,
): Promise<T> {
  // -- Build URL --------------------------------------------------------
  const url = new URL(path, BASE_URL);
  if (params) {
    const searchParams = new URLSearchParams(params);
    url.search = searchParams.toString();
  }

  const target = url.toString();
  console.error(`[client] GET ${target}`);

  // -- Execute fetch ----------------------------------------------------
  let response: Response;
  try {
    response = await fetch(target);
  } catch (err: unknown) {
    const message =
      err instanceof Error ? err.message : String(err);
    console.error(`[client] Network error: ${message}`);
    throw new Error(
      `Network error while fetching ${target}: ${message}`,
    );
  }

  // -- Check HTTP status ------------------------------------------------
  if (!response.ok) {
    let body = "";
    try {
      body = await response.text();
    } catch {
      // Ignore read errors; we already know the request failed.
    }
    const detail = `HTTP ${response.status} ${response.statusText}`;
    console.error(`[client] ${detail} — ${body}`);
    throw new Error(
      `${detail} from ${target}${body ? `: ${body}` : ""}`,
    );
  }

  // -- Parse JSON -------------------------------------------------------
  let data: T;
  try {
    data = (await response.json()) as T;
  } catch (err: unknown) {
    const message =
      err instanceof Error ? err.message : String(err);
    console.error(`[client] JSON parse error: ${message}`);
    throw new Error(
      `Failed to parse JSON response from ${target}: ${message}`,
    );
  }

  return data;
}
