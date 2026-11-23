import { fireEvent, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { TaskItem } from "@/components/dashboard/TaskItem";
import { apiFetch } from "@/lib/api/client";
import { makeTask, renderWithQuery } from "@/test/helpers";

vi.mock("@/lib/api/client", async (importOriginal) => ({
  ...(await importOriginal<typeof import("@/lib/api/client")>()),
  apiFetch: vi.fn(),
}));

const apiFetchMock = vi.mocked(apiFetch);

describe("TaskItem", () => {
  beforeEach(() => {
    apiFetchMock.mockReset();
    apiFetchMock.mockResolvedValue(makeTask({ status: "done" }));
  });

  it("completes an open task with a PATCH to the API", async () => {
    renderWithQuery(<ul><TaskItem task={makeTask({ id: "abc", title: "Send form" })} /></ul>);

    fireEvent.click(screen.getByRole("checkbox", { name: "Mark done: Send form" }));

    await waitFor(() => expect(apiFetchMock).toHaveBeenCalled());
    expect(apiFetchMock).toHaveBeenCalledWith("/api/v1/tasks/abc", {
      method: "PATCH",
      body: JSON.stringify({ status: "done" }),
    });
  });

  it("reopens a done task", async () => {
    renderWithQuery(
      <ul><TaskItem task={makeTask({ id: "abc", title: "Send form", status: "done" })} /></ul>,
    );

    const checkbox = screen.getByRole("checkbox", { name: "Reopen: Send form" });
    expect(checkbox.getAttribute("aria-checked")).toBe("true");
    fireEvent.click(checkbox);

    await waitFor(() => expect(apiFetchMock).toHaveBeenCalled());
    expect(apiFetchMock.mock.calls[0][1]).toMatchObject({ body: JSON.stringify({ status: "todo" }) });
  });

  it("shows priority and notes only when asked to", () => {
    const task = makeTask({ priority: "critical", notes: "Bring passport" });

    const { unmount } = renderWithQuery(<ul><TaskItem task={task} /></ul>);
    expect(screen.queryByText("Critical")).toBeNull();
    expect(screen.queryByText("Bring passport")).toBeNull();
    unmount();

    renderWithQuery(<ul><TaskItem task={task} showPriority /></ul>);
    expect(screen.getByText("Critical")).toBeTruthy();
    expect(screen.getByText("Bring passport")).toBeTruthy();
  });
});
