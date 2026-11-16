import { fireEvent, render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { PriorityBoard } from "@/components/dashboard/PriorityBoard";
import type { PlaceholderTask, Priority } from "@/lib/placeholder";

function buildTasks(priority: Priority, count: number): PlaceholderTask[] {
  return Array.from({ length: count }, (_, index) => ({
    id: `${priority}-${index}`,
    title: `${priority} task ${index + 1}`,
    priority,
    dueLabel: null,
  }));
}

describe("PriorityBoard", () => {
  it("always renders all four priority columns in order", () => {
    render(<PriorityBoard tasks={[]} />);

    const columnNames = screen
      .getAllByRole("heading", { level: 3 })
      .map((heading) => heading.id);

    expect(columnNames).toEqual([
      "priority-critical-heading",
      "priority-high-heading",
      "priority-normal-heading",
      "priority-low-heading",
    ]);
  });

  it("shows a message in each empty column instead of a blank box", () => {
    render(<PriorityBoard tasks={[]} />);

    expect(screen.getByText("Nothing critical. Good.")).toBeTruthy();
    expect(screen.getByText("No high-priority tasks.")).toBeTruthy();
    expect(screen.getByText("No normal-priority tasks.")).toBeTruthy();
    expect(screen.getByText("No low-priority tasks.")).toBeTruthy();
  });

  it("puts each task in the column for its priority", () => {
    render(<PriorityBoard tasks={[...buildTasks("critical", 1), ...buildTasks("low", 2)]} />);

    const criticalColumn = screen.getByRole("region", { name: /Critical/ });
    const lowColumn = screen.getByRole("region", { name: /Low/ });

    expect(within(criticalColumn).getAllByRole("listitem")).toHaveLength(1);
    expect(within(lowColumn).getAllByRole("listitem")).toHaveLength(2);
    expect(within(lowColumn).queryByText("critical task 1")).toBeNull();
  });

  it("shows at most five tasks and links to the rest", () => {
    render(<PriorityBoard tasks={buildTasks("normal", 7)} />);

    const normalColumn = screen.getByRole("region", { name: /Normal/ });
    const moreLink = within(normalColumn).getByRole("link", { name: "+2 more" });

    expect(within(normalColumn).getAllByRole("listitem")).toHaveLength(5);
    expect(moreLink.getAttribute("href")).toBe("/tasks?priority=normal");
  });

  it("shows no more-link when a column has five tasks or fewer", () => {
    render(<PriorityBoard tasks={buildTasks("high", 5)} />);

    expect(screen.queryByRole("link", { name: /more/ })).toBeNull();
  });

  it("opens Critical and High by default on mobile and toggles a column on tap", () => {
    render(<PriorityBoard tasks={[]} />);

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
