import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

const API_URL = "http://api.test";

function jsonResponse(status: number, body: unknown): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

async function loadClient(): Promise<typeof import("@/lib/api/client")> {
  vi.resetModules();
  return import("@/lib/api/client");
}

describe("apiFetch", () => {
  const fetchMock = vi.fn<typeof fetch>();

  beforeEach(() => {
    vi.stubEnv("NEXT_PUBLIC_API_URL", API_URL);
    vi.stubGlobal("fetch", fetchMock);
  });

  afterEach(() => {
    vi.unstubAllEnvs();
    vi.unstubAllGlobals();
    fetchMock.mockReset();
  });

  it("prefixes the base URL and returns the parsed body", async () => {
    fetchMock.mockResolvedValue(jsonResponse(200, { status: "ok", version: "0.1.0" }));
    const { apiFetch } = await loadClient();

    const body = await apiFetch<{ status: string }>("/api/v1/health");

    expect(body).toEqual({ status: "ok", version: "0.1.0" });
    expect(fetchMock.mock.calls[0][0]).toBe(`${API_URL}/api/v1/health`);
  });

  it("throws a typed ApiError from the standard error body", async () => {
    fetchMock.mockResolvedValue(
      jsonResponse(404, {
        error: { code: "TASK_NOT_FOUND", message: "Task not found", details: { id: "t1" } },
      }),
    );
    const { ApiError, apiFetch } = await loadClient();

    const error: unknown = await apiFetch("/api/v1/tasks/t1").catch((caught: unknown) => caught);

    expect(error).toBeInstanceOf(ApiError);
    expect(error).toMatchObject({
      status: 404,
      code: "TASK_NOT_FOUND",
      message: "Task not found",
      details: { id: "t1" },
    });
  });

  it("falls back to INTERNAL when the error body is not the standard shape", async () => {
    fetchMock.mockResolvedValue(new Response("<html>Bad gateway</html>", { status: 502 }));
    const { apiFetch } = await loadClient();

    const error: unknown = await apiFetch("/api/v1/health").catch((caught: unknown) => caught);

    expect(error).toMatchObject({ status: 502, code: "INTERNAL" });
  });

  it("throws NETWORK_ERROR when the backend cannot be reached", async () => {
    fetchMock.mockRejectedValue(new TypeError("Failed to fetch"));
    const { apiFetch } = await loadClient();

    const error: unknown = await apiFetch("/api/v1/health").catch((caught: unknown) => caught);

    expect(error).toMatchObject({ status: 0, code: "NETWORK_ERROR" });
  });

  it("throws CONFIG_ERROR without calling fetch when the base URL is missing", async () => {
    vi.stubEnv("NEXT_PUBLIC_API_URL", "");
    const { apiFetch } = await loadClient();

    const error: unknown = await apiFetch("/api/v1/health").catch((caught: unknown) => caught);

    expect(error).toMatchObject({ status: 0, code: "CONFIG_ERROR" });
    expect(fetchMock).not.toHaveBeenCalled();
  });
});
