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

  describe("with auth handlers", () => {
    function authHandlers(overrides: Partial<import("@/lib/api/client").AuthHandlers> = {}) {
      return {
        getAccessToken: vi.fn().mockResolvedValue("access-1"),
        refreshAccessToken: vi.fn().mockResolvedValue("access-2"),
        onSessionExpired: vi.fn(),
        ...overrides,
      };
    }

    function sentAuthorization(callIndex: number): string | null {
      const init = fetchMock.mock.calls[callIndex][1];
      return new Headers(init?.headers).get("Authorization");
    }

    it("sends the bearer token", async () => {
      fetchMock.mockResolvedValue(jsonResponse(200, {}));
      const { apiFetch, setAuthHandlers } = await loadClient();
      setAuthHandlers(authHandlers());

      await apiFetch("/api/v1/me");

      expect(sentAuthorization(0)).toBe("Bearer access-1");
    });

    it("sends no Authorization header without handlers", async () => {
      fetchMock.mockResolvedValue(jsonResponse(200, {}));
      const { apiFetch } = await loadClient();

      await apiFetch("/api/v1/health");

      expect(sentAuthorization(0)).toBeNull();
    });

    it("refreshes the session once on 401 and retries with the new token", async () => {
      fetchMock
        .mockResolvedValueOnce(jsonResponse(401, { error: { code: "UNAUTHENTICATED", message: "x" } }))
        .mockResolvedValueOnce(jsonResponse(200, { ok: true }));
      const handlers = authHandlers();
      const { apiFetch, setAuthHandlers } = await loadClient();
      setAuthHandlers(handlers);

      const body = await apiFetch("/api/v1/me");

      expect(body).toEqual({ ok: true });
      expect(fetchMock).toHaveBeenCalledTimes(2);
      expect(sentAuthorization(1)).toBe("Bearer access-2");
      expect(handlers.onSessionExpired).not.toHaveBeenCalled();
    });

    it("ends the session when the retry is also rejected", async () => {
      fetchMock.mockResolvedValue(
        jsonResponse(401, { error: { code: "UNAUTHENTICATED", message: "Invalid or expired token" } }),
      );
      const handlers = authHandlers();
      const { ApiError, apiFetch, setAuthHandlers } = await loadClient();
      setAuthHandlers(handlers);

      const error: unknown = await apiFetch("/api/v1/me").catch((caught: unknown) => caught);

      expect(error).toBeInstanceOf(ApiError);
      expect(error).toMatchObject({ status: 401, code: "UNAUTHENTICATED" });
      expect(fetchMock).toHaveBeenCalledTimes(2);
      expect(handlers.onSessionExpired).toHaveBeenCalledOnce();
    });

    it("ends the session without retrying when no refreshed token is available", async () => {
      fetchMock.mockResolvedValue(
        jsonResponse(401, { error: { code: "UNAUTHENTICATED", message: "x" } }),
      );
      const handlers = authHandlers({ refreshAccessToken: vi.fn().mockResolvedValue(null) });
      const { apiFetch, setAuthHandlers } = await loadClient();
      setAuthHandlers(handlers);

      await apiFetch("/api/v1/me").catch(() => undefined);

      expect(fetchMock).toHaveBeenCalledTimes(1);
      expect(handlers.onSessionExpired).toHaveBeenCalledOnce();
    });

    it("does not refresh on other errors", async () => {
      fetchMock.mockResolvedValue(
        jsonResponse(404, { error: { code: "TASK_NOT_FOUND", message: "Task not found" } }),
      );
      const handlers = authHandlers();
      const { apiFetch, setAuthHandlers } = await loadClient();
      setAuthHandlers(handlers);

      await apiFetch("/api/v1/tasks/x").catch(() => undefined);

      expect(handlers.refreshAccessToken).not.toHaveBeenCalled();
    });

    it("sends JSON bodies with a JSON content type", async () => {
      fetchMock.mockResolvedValue(jsonResponse(201, {}));
      const { apiFetch } = await loadClient();

      await apiFetch("/api/v1/tasks", { method: "POST", body: JSON.stringify({ title: "x" }) });

      const headers = new Headers(fetchMock.mock.calls[0][1]?.headers);
      expect(headers.get("Content-Type")).toBe("application/json");
    });

    it("returns null for an empty 204 response", async () => {
      fetchMock.mockResolvedValue(new Response(null, { status: 204 }));
      const { apiFetch } = await loadClient();

      expect(await apiFetch("/api/v1/tasks/x", { method: "DELETE" })).toBeNull();
    });
  });
});
