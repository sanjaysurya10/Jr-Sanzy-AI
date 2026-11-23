import Link from "next/link";

import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";

const MAX_VISIBLE_DECISIONS = 3;

export interface DecisionSummary {
  id: string;
  title: string;
  rationale: string;
}

interface DecisionCentreProps {
  decisions: DecisionSummary[];
}

export function DecisionCentre({ decisions }: DecisionCentreProps) {
  return (
    <Card
      title={`Decisions (${decisions.length} pending)`}
      titleId="decision-centre-title"
      action={
        <Link
          href="/decisions"
          className="flex min-h-11 items-center text-sm font-medium text-accent hover:underline"
        >
          Review all
        </Link>
      }
    >
      {decisions.length === 0 ? (
        <EmptyState message="Nothing waiting for your approval." />
      ) : (
        <ul className="flex flex-col gap-2">
          {decisions.slice(0, MAX_VISIBLE_DECISIONS).map((decision) => (
            <li key={decision.id} className="rounded-md border border-border px-3 py-2">
              <p className="break-words text-sm font-medium">{decision.title}</p>
              <p className="mt-0.5 text-xs text-muted">{decision.rationale}</p>
            </li>
          ))}
        </ul>
      )}
    </Card>
  );
}
