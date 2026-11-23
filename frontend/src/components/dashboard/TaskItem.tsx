"use client";

import type { ReactNode } from "react";

import { useUpdateTask } from "@/hooks/useTasks";
import { PRIORITY_LABELS, type TaskRead } from "@/lib/api/types";
import { formatDue } from "@/lib/format";

interface TaskItemProps {
  task: TaskRead;
  showPriority?: boolean;
  actions?: ReactNode;
}

export function TaskItem({ task, showPriority = false, actions }: TaskItemProps) {
  const updateTask = useUpdateTask();
  const isDone = task.status === "done";

  return (
    <li className="flex items-start gap-2 rounded-md border border-border bg-surface px-3 py-2">
      <button
        type="button"
        role="checkbox"
        aria-checked={isDone}
        aria-label={`${isDone ? "Reopen" : "Mark done"}: ${task.title}`}
        onClick={() =>
          updateTask.mutate({ id: task.id, data: { status: isDone ? "todo" : "done" } })
        }
        className="flex h-11 w-11 shrink-0 items-center justify-center -ml-2 -my-1.5"
      >
        <span
          aria-hidden="true"
          className={`flex h-5 w-5 items-center justify-center rounded border text-xs ${
            isDone ? "border-accent bg-accent text-background" : "border-muted"
          }`}
        >
          {isDone ? "✓" : ""}
        </span>
      </button>
      <div className="min-w-0 flex-1 py-0.5">
        <p className={`break-words text-sm font-medium ${isDone ? "text-muted line-through" : ""}`}>
          {task.title}
        </p>
        {showPriority || task.due_at !== null ? (
          <p className="mt-0.5 text-xs text-muted">
            {showPriority ? <span className="mr-2 font-medium">{PRIORITY_LABELS[task.priority]}</span> : null}
            {task.due_at !== null ? `Due ${formatDue(task.due_at)}` : null}
            {task.is_overdue ? (
              <span className="ml-2 font-semibold text-red-700 dark:text-red-300">Overdue</span>
            ) : null}
          </p>
        ) : null}
        {task.notes !== null && showPriority ? (
          <p className="mt-1 whitespace-pre-line break-words text-xs text-muted">{task.notes}</p>
        ) : null}
        {actions}
      </div>
    </li>
  );
}
