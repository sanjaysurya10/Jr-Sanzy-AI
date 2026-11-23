import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import type { ActivityRead } from "@/lib/api/types";
import { formatTime } from "@/lib/format";

const ACTION_LABELS: Record<string, string> = {
  "task.created": "Created",
  "task.completed": "Completed",
  "task.reopened": "Reopened",
  "task.deleted": "Deleted",
};

const ACTOR_LABELS: Record<string, string> = {
  user: "You",
  system: "System",
};

function describe(entry: ActivityRead): string {
  const label = ACTION_LABELS[entry.action] ?? entry.action;
  const title = entry.details.title;
  return typeof title === "string" ? `${label} “${title}”` : label;
}

interface ActivityFeedProps {
  entries: ActivityRead[];
}

export function ActivityFeed({ entries }: ActivityFeedProps) {
  return (
    <Card title="Recent activity" titleId="activity-feed-title">
      {entries.length === 0 ? (
        <EmptyState message="No activity yet." />
      ) : (
        <ul className="flex flex-col divide-y divide-border">
          {entries.map((entry) => (
            <li key={entry.id} className="flex items-baseline gap-3 py-2 text-sm">
              <span className="w-12 shrink-0 text-xs tabular-nums text-muted">
                {formatTime(entry.created_at)}
              </span>
              <span className="min-w-0 break-words">
                <span className="font-medium">{ACTOR_LABELS[entry.actor] ?? entry.actor}:</span>{" "}
                {describe(entry)}
              </span>
            </li>
          ))}
        </ul>
      )}
    </Card>
  );
}
