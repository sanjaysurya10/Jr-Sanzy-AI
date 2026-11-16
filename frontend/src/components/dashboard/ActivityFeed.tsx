import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import type { PlaceholderActivity } from "@/lib/placeholder";

interface ActivityFeedProps {
  entries: PlaceholderActivity[];
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
                {entry.timeLabel}
              </span>
              <span className="min-w-0 break-words">
                <span className="font-medium">{entry.actor}:</span> {entry.summary}
              </span>
            </li>
          ))}
        </ul>
      )}
    </Card>
  );
}
