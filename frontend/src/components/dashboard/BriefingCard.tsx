import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";

export interface BriefingSummary {
  headline: string;
  bullets: string[];
}

interface BriefingCardProps {
  briefing: BriefingSummary | null;
}

export function BriefingCard({ briefing }: BriefingCardProps) {
  return (
    <Card title="Today's briefing" titleId="briefing-title">
      {briefing === null ? (
        <EmptyState message="No briefing yet today." />
      ) : (
        <>
          <p className="text-lg font-semibold">{briefing.headline}</p>
          <ul className="mt-2 list-disc space-y-1 pl-5 text-sm">
            {briefing.bullets.map((bullet) => (
              <li key={bullet}>{bullet}</li>
            ))}
          </ul>
        </>
      )}
    </Card>
  );
}
