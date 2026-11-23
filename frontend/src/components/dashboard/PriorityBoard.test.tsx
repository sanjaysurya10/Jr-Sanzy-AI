import { fireEvent, screen, within } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { PriorityBoard } from "@/components/dashboard/PriorityBoard";
import type { TaskPriority, TaskRead } from "@/lib/api/types";
import { makeGroups, makeTask, renderWithQuery } from "@/test/helpers";

vi.mock("@/lib/api/client", async (importOriginal) => ({
  ...(await importOriginal<typeof import("@/lib/api/client")>()),
  apiFetch: vi.fn(),
}));

function buildTasks(priority: TaskPriority, count: number): TaskRead[] {
  return Array.from({ length: count }, (_, index) =>
    makeTask({ id: `${priority}-${index}`, title: `${priority} task ${index + 1}`, priority }),
  );
}

describe("PriorityBoard", () => {
  it("always renders all four priority columns in order", () => {
    renderWithQuery(<PriorityBoard groups={makeGroups()} />);

    const columnIds = screen.getAllByRole("heading", { level: 3 }).map((heading) => heading.id);

    expect(columnIds).toEqual([
      "priority-critical-heading",
      "priority-high-heading",
      "priority-normal-heading",
      "priority-low-heading",
    ]);
  });

  it("shows a message in each empty column instead of a blank box", () => {
    renderWithQuery(<PriorityBoard groups={makeGroups()} />);

    expect(screen.getByText("Nothing critical. Good.")).toBeTruthy();
    expect(screen.getByText("No high-priority tasks.")).toBeTruthy();
    expect(screen.getByText("No normal-priority tasks.")).toBeTruthy();
    expect(screen.getByText("No low-priority tasks.")).toBeTruthy();
  });

  it("puts each task in the column for its priority", () => {
    renderWithQuery(
      <PriorityBoard
        groups={makeGroups({
          critical: { items: buildTasks("critical", 1) },
          low: { items: buildTasks("low", 2) },
        })}
      />,
    );

    const criticalColumn = screen.getByRole("region", { name: /Critical/ });
    const lowColumn = screen.getByRole("region", { name: /Low/ });

    expect(within(criticalColumn).getAllByRole("listitem")).toHaveLength(1);
    expect(within(lowColumn).getAllByRole("listitem")).toHaveLength(2);
    expect(within(lowColumn).queryByText("critical task 1")).toBeNull();
  });

  it("shows the server's total and links to the tasks the column does not show", () => {
    renderWithQuery(
      <PriorityBoard groups={makeGroups({ normal: { items: buildTasks("normal", 5), total: 7 } })} />,
    );

    const normalColumn = screen.getByRole("region", { name: /Normal/ });
    const moreLink = within(normalColumn).getByRole("link", { name: "+2 more" });

    expect(within(normalColumn).getAllByRole("listitem")).toHaveLength(5);
    expect(moreLink.getAttribute("href")).toBe("/tasks?priority=normal");
  });

  it("shows no more-link when the column shows every task", () => {
    renderWithQuery(
      <PriorityBoard groups={makeGroups({ high: { items: buildTasks("high", 5) } })} />,
    );

    expect(screen.queryByRole("link", { name: /more/ })).toBeNull();
  });

  it("marks overdue tasks with text, not only colour", () => {
    renderWithQuery(
      <PriorityBoard
        groups={makeGroups({
          high: {
            items: [makeTask({ priority: "high", due_at: "2020-01-01T09:00:00Z", is_overdue: true })],
          },
        })}
      />,
    );

    expect(screen.getByText("Overdue")).toBeTruthy();
  });

  it("opens Critical and High by default on mobile and toggles a column on tap", () => {
    renderWithQuery(<PriorityBoard groups={makeGroups()} />);

    const criticalToggle = screen.getByRole("button", { name: /Critical/ });
    const highToggle = screen.getByRole("button", { name: /High/ });
    const normalToggle = screen.getByRole("button", { name: /Normal/ });
    const lowToggle = screen.getByRole("button", { name: /Low/ });

    expect(criticalToggle.getAttribute("aria-expanded")).toBe("true");
    expect(highToggle.getAttribute("aria-expanded")).toBe("true");
    expect(normalToggle.getAttribute("aria-expanded")).toBe("false");
    expect(lowToggle.getAttribute("aria-expanded")).toBe("false");

    fireEvent.click(normalToggle);

    expect(normalToggle.getAttribute("aria-expanded")).toBe("true");
  });
});
