import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, type RenderResult } from "@testing-library/react";
import type { ReactElement } from "react";

import type { TaskPriority, TaskRead, TasksByPriority } from "@/lib/api/types";

export function makeTask(overrides: Partial<TaskRead> = {}): TaskRead {
  return {
    id: "task-1",
    title: "Task",
    notes: null,
    priority: "normal",
    status: "todo",
    due_at: null,
    completed_at: null,
    source: "manual",
    source_ref: null,
    is_overdue: false,
    created_at: "2030-01-01T00:00:00Z",
    updated_at: "2030-01-01T00:00:00Z",
    ...overrides,
  };
}

export function makeGroups(
  tasksByPriority: Partial<Record<TaskPriority, { items: TaskRead[]; total?: number }>> = {},
): TasksByPriority {
  const group = (priority: TaskPriority) => {
    const entry = tasksByPriority[priority];
    return { items: entry?.items ?? [], total: entry?.total ?? entry?.items.length ?? 0 };
  };
  return {
    critical: group("critical"),
    high: group("high"),
    normal: group("normal"),
    low: group("low"),
  };
}

export function renderWithQuery(ui: ReactElement): RenderResult {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
  return render(<QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>);
}
