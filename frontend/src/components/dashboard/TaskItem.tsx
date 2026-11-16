import type { PlaceholderTask } from "@/lib/placeholder";

interface TaskItemProps {
  task: PlaceholderTask;
}

export function TaskItem({ task }: TaskItemProps) {
  return (
    <li className="rounded-md border border-border bg-surface px-3 py-2">
      <p className="break-words text-sm font-medium">{task.title}</p>
      {task.dueLabel !== null ? (
        <p className="mt-0.5 text-xs text-muted">Due {task.dueLabel}</p>
      ) : null}
    </li>
  );
}
