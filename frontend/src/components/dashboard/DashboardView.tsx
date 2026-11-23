"use client";

import { ActivityFeed } from "@/components/dashboard/ActivityFeed";
import { BriefingCard } from "@/components/dashboard/BriefingCard";
import { DecisionCentre } from "@/components/dashboard/DecisionCentre";
import { PriorityBoard } from "@/components/dashboard/PriorityBoard";
import { useDashboard } from "@/hooks/useDashboard";

function DashboardSkeleton() {
  return (
    <div role="status" aria-label="Loading dashboard" className="flex animate-pulse flex-col gap-4">
      <div className="h-8 w-64 rounded bg-border" />
      <div className="h-32 rounded-lg bg-border" />
      <div className="grid grid-cols-1 gap-3 md:grid-cols-2 lg:grid-cols-4">
        {[0, 1, 2, 3].map((placeholder) => (
          <div key={placeholder} className="h-40 rounded-lg bg-border" />
        ))}
      </div>
    </div>
  );
}

export function DashboardView() {
  const { data, isPending, isError, error, refetch } = useDashboard();

  if (isPending) {
    return <DashboardSkeleton />;
  }

  if (isError) {
    return (
      <div role="alert" className="rounded-lg border border-border bg-surface p-4">
        <p className="font-medium">Could not load the dashboard.</p>
        <p className="mt-1 text-sm text-muted">
          {error.status === 0 ? "The backend is not reachable." : error.message}
        </p>
        <button
          type="button"
          onClick={() => void refetch()}
          className="mt-3 min-h-11 rounded-md border border-border px-4 text-sm font-medium"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="mx-auto flex max-w-7xl flex-col gap-4">
      <h1 className="text-xl font-semibold">{data.greeting.text}</h1>
      <BriefingCard briefing={null} />
      <PriorityBoard groups={data.tasks_by_priority} />
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <DecisionCentre decisions={[]} />
        <ActivityFeed entries={data.activity} />
      </div>
    </div>
  );
}
