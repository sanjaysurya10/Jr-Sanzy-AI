"use client";

import Link from "next/link";
import { useState } from "react";

import { TaskItem } from "@/components/dashboard/TaskItem";
import { NavIcon } from "@/components/layout/NavIcon";
import { EmptyState } from "@/components/ui/EmptyState";
import type { PlaceholderTask, Priority } from "@/lib/placeholder";

const MAX_VISIBLE_TASKS = 5;

interface PriorityStyle {
  label: string;
  emptyMessage: string;
  container: string;
  heading: string;
}

// Same width for every column; Critical gets a tinted background, not more space.
const PRIORITY_STYLES: Record<Priority, PriorityStyle> = {
  critical: {
    label: "Critical",
    emptyMessage: "Nothing critical. Good.",
    container: "border-t-red-600 bg-red-50 dark:border-t-red-500 dark:bg-red-950/40",
    heading: "text-red-800 dark:text-red-300",
  },
  high: {
    label: "High",
    emptyMessage: "No high-priority tasks.",
    container: "border-t-orange-500 bg-surface",
    heading: "text-orange-800 dark:text-orange-300",
  },
  normal: {
    label: "Normal",
    emptyMessage: "No normal-priority tasks.",
    container: "border-t-blue-600 bg-surface dark:border-t-blue-500",
    heading: "text-blue-800 dark:text-blue-300",
  },
  low: {
    label: "Low",
    emptyMessage: "No low-priority tasks.",
    container: "border-t-green-600 bg-surface dark:border-t-green-500",
    heading: "text-green-800 dark:text-green-300",
  },
};

interface PriorityColumnProps {
  priority: Priority;
  tasks: PlaceholderTask[];
  isOpenByDefaultOnMobile: boolean;
}

export function PriorityColumn({ priority, tasks, isOpenByDefaultOnMobile }: PriorityColumnProps) {
  const [isOpen, setIsOpen] = useState(isOpenByDefaultOnMobile);
  const style = PRIORITY_STYLES[priority];
  const visibleTasks = tasks.slice(0, MAX_VISIBLE_TASKS);
  const hiddenTaskCount = tasks.length - visibleTasks.length;
  const headingId = `priority-${priority}-heading`;
  const panelId = `priority-${priority}-panel`;
  const headingText = (
    <>
      <span>{style.label}</span>
      <span className="text-xs font-medium text-muted">{tasks.length}</span>
    </>
  );

  return (
    <section
      aria-labelledby={headingId}
      className={`min-w-0 rounded-lg border border-border border-t-4 ${style.container}`}
    >
      <h3 id={headingId} className={`text-sm font-semibold ${style.heading}`}>
        <button
          type="button"
          aria-expanded={isOpen}
          aria-controls={panelId}
          onClick={() => setIsOpen((wasOpen) => !wasOpen)}
          className="flex min-h-11 w-full items-center gap-2 px-3 md:hidden"
        >
          {headingText}
          <NavIcon
            name="chevron"
            className={`ml-auto h-4 w-4 transition-transform ${isOpen ? "rotate-180" : ""}`}
          />
        </button>
        <span className="hidden min-h-11 items-center gap-2 px-3 md:flex">{headingText}</span>
      </h3>
      <div id={panelId} className={`px-3 pb-3 ${isOpen ? "block" : "hidden md:block"}`}>
        {tasks.length === 0 ? (
          <EmptyState message={style.emptyMessage} />
        ) : (
          <ul className="flex flex-col gap-2">
            {visibleTasks.map((task) => (
              <TaskItem key={task.id} task={task} />
            ))}
          </ul>
        )}
        {hiddenTaskCount > 0 ? (
          <Link
            href={`/tasks?priority=${priority}`}
            className="mt-2 flex min-h-11 items-center text-sm font-medium text-accent hover:underline"
          >
            +{hiddenTaskCount} more
          </Link>
        ) : null}
      </div>
    </section>
  );
}
