"use client";

import { useSearchParams } from "next/navigation";
import { useState } from "react";

import { TaskForm } from "@/components/tasks/TaskForm";
import { TaskRow } from "@/components/tasks/TaskRow";
import { EmptyState } from "@/components/ui/EmptyState";
import { useCreateTask, useTasks, type TaskFilters } from "@/hooks/useTasks";
import { PRIORITY_LABELS, PRIORITY_ORDER, type TaskPriority, type TaskStatus } from "@/lib/api/types";

const SELECT_CLASSES = "mt-1 min-h-11 rounded-md border border-border bg-background px-3 text-base";

const STATUS_OPTIONS: { value: TaskStatus | ""; label: string }[] = [
  { value: "todo", label: "Open" },
  { value: "done", label: "Done" },
  { value: "archived", label: "Archived" },
  { value: "", label: "All" },
];

function isPriority(value: string | null): value is TaskPriority {
  return PRIORITY_ORDER.some((priority) => priority === value);
}

export function TasksView() {
  const searchParams = useSearchParams();
  const priorityParam = searchParams.get("priority");
  const [filters, setFilters] = useState<TaskFilters>({
    status: "todo",
    priority: isPriority(priorityParam) ? priorityParam : "",
    q: "",
  });
  const tasksQuery = useTasks(filters);
  const createTask = useCreateTask();

  const tasks = tasksQuery.data?.pages.flatMap((page) => page.items) ?? [];

  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-4">
      <h1 className="text-xl font-semibold">Tasks</h1>

      <TaskForm
        submitLabel="Add task"
        isSubmitting={createTask.isPending}
        errorMessage={createTask.isError ? createTask.error.message : null}
        onSubmit={(data) => createTask.mutate(data)}
      />

      <div className="flex flex-wrap items-end gap-3">
        <label className="text-sm font-medium">
          Status
          <select
            value={filters.status}
            onChange={(event) =>
              setFilters({ ...filters, status: event.target.value as TaskStatus | "" })
            }
            className={`${SELECT_CLASSES} block`}
          >
            {STATUS_OPTIONS.map((option) => (
              <option key={option.label} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </label>
        <label className="text-sm font-medium">
          Priority
          <select
            value={filters.priority}
            onChange={(event) =>
              setFilters({ ...filters, priority: event.target.value as TaskPriority | "" })
            }
            className={`${SELECT_CLASSES} block`}
          >
            <option value="">All</option>
            {PRIORITY_ORDER.map((priority) => (
              <option key={priority} value={priority}>
                {PRIORITY_LABELS[priority]}
              </option>
            ))}
          </select>
        </label>
        <label className="min-w-40 flex-1 text-sm font-medium">
          Search
          <input
            type="search"
            value={filters.q}
            onChange={(event) => setFilters({ ...filters, q: event.target.value })}
            className={`${SELECT_CLASSES} block w-full`}
          />
        </label>
      </div>

      {tasksQuery.isPending ? (
        <p role="status" className="text-sm text-muted">
          Loading tasks…
        </p>
      ) : tasksQuery.isError ? (
        <div role="alert" className="rounded-lg border border-border bg-surface p-4">
          <p className="font-medium">Could not load tasks.</p>
          <p className="mt-1 text-sm text-muted">{tasksQuery.error.message}</p>
          <button
            type="button"
            onClick={() => void tasksQuery.refetch()}
            className="mt-3 min-h-11 rounded-md border border-border px-4 text-sm font-medium"
          >
            Retry
          </button>
        </div>
      ) : tasks.length === 0 ? (
        <EmptyState message="No tasks match these filters." />
      ) : (
        <>
          <ul className="flex flex-col gap-2">
            {tasks.map((task) => (
              <TaskRow key={task.id} task={task} />
            ))}
          </ul>
          {tasksQuery.hasNextPage ? (
            <button
              type="button"
              onClick={() => void tasksQuery.fetchNextPage()}
              disabled={tasksQuery.isFetchingNextPage}
              className="min-h-11 self-start rounded-md border border-border px-4 text-sm font-medium"
            >
              {tasksQuery.isFetchingNextPage ? "Loading…" : "Load more"}
            </button>
          ) : null}
        </>
      )}
    </div>
  );
}
