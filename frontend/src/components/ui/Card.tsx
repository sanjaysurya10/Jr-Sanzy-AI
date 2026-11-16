import type { ReactNode } from "react";

interface CardProps {
  title: string;
  titleId: string;
  action?: ReactNode;
  children: ReactNode;
}

export function Card({ title, titleId, action, children }: CardProps) {
  return (
    <section
      aria-labelledby={titleId}
      className="min-w-0 rounded-lg border border-border bg-surface p-4"
    >
      <div className="mb-3 flex items-center justify-between gap-3">
        <h2 id={titleId} className="text-sm font-semibold uppercase tracking-wide text-muted">
          {title}
        </h2>
        {action}
      </div>
      {children}
    </section>
  );
}
