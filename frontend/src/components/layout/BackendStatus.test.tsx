import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { BackendStatus } from "@/components/layout/BackendStatus";
import { apiFetch } from "@/lib/api/client";

vi.mock("@/lib/api/client", async (importOriginal) => ({
  ...(await importOriginal<typeof import("@/lib/api/client")>()),
  apiFetch: vi.fn(),
}));

const apiFetchMock = vi.mocked(apiFetch);

function renderBackendStatus(): void {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retryDelay: 0 } },
  });
  render(
    <QueryClientProvider client={queryClient}>
      <BackendStatus />
    </QueryClientProvider>,
  );
}

describe("BackendStatus", () => {
  beforeEach(() => {
    apiFetchMock.mockReset();
  });

  it("shows a checking state before the first response", () => {
    apiFetchMock.mockReturnValue(new Promise(() => {}));

    renderBackendStatus();

    expect(screen.getByRole("status").textContent).toBe("Backend: checking…");
  });

  it("shows OK when the health endpoint responds", async () => {
    apiFetchMock.mockResolvedValue({ status: "ok", version: "0.1.0" });

    renderBackendStatus();

    expect(await screen.findByText("Backend: OK")).toBeTruthy();
    expect(apiFetchMock).toHaveBeenCalledWith("/api/v1/health");
  });

  it("shows an error state instead of crashing when the backend is down", async () => {
    apiFetchMock.mockRejectedValue(new Error("Could not reach the backend"));

    renderBackendStatus();

    expect(await screen.findByText("Backend: unreachable")).toBeTruthy();
  });
});
