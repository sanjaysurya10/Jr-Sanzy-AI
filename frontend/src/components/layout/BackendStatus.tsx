"use client";

import { useHealth } from "@/hooks/useHealth";

const DOT_BASE_CLASSES = "h-2 w-2 shrink-0 rounded-full";

export function BackendStatus() {
  const { isPending, isError } = useHealth();

  let label = "Backend: OK";
  let dotClasses = "bg-green-600 dark:bg-green-400";
  if (isPending) {
    label = "Backend: checking…";
    dotClasses = "bg-muted";
  } else if (isError) {
    label = "Backend: unreachable";
    dotClasses = "bg-red-600 dark:bg-red-400";
  }

  return (
    <p role="status" className="flex items-center gap-2 whitespace-nowrap text-xs text-muted">
      <span aria-hidden="true" className={`${DOT_BASE_CLASSES} ${dotClasses}`} />
      {label}
    </p>
  );
}
