import { ActivityFeed } from "@/components/dashboard/ActivityFeed";
import { BriefingCard } from "@/components/dashboard/BriefingCard";
import { DecisionCentre } from "@/components/dashboard/DecisionCentre";
import { PriorityBoard } from "@/components/dashboard/PriorityBoard";
import { Badge } from "@/components/ui/Badge";
import {
  PLACEHOLDER_ACTIVITY,
  PLACEHOLDER_BRIEFING,
  PLACEHOLDER_DECISIONS,
  PLACEHOLDER_TASKS,
} from "@/lib/placeholder";

export default function DashboardPage() {
  return (
    <div className="mx-auto flex max-w-7xl flex-col gap-4">
      <div className="flex items-center gap-3">
        <h1 className="text-xl font-semibold">Dashboard</h1>
        <Badge>Placeholder data</Badge>
      </div>
      <BriefingCard briefing={PLACEHOLDER_BRIEFING} />
      <PriorityBoard tasks={PLACEHOLDER_TASKS} />
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <DecisionCentre decisions={PLACEHOLDER_DECISIONS} />
        <ActivityFeed entries={PLACEHOLDER_ACTIVITY} />
      </div>
    </div>
  );
}
