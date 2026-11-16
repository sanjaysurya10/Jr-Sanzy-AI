import Link from "next/link";

import { BackendStatus } from "@/components/layout/BackendStatus";
import { NavIcon } from "@/components/layout/NavIcon";
import { TodayDate } from "@/components/layout/TodayDate";

interface HeaderProps {
  pendingDecisionCount: number;
}

export function Header({ pendingDecisionCount }: HeaderProps) {
  const bellLabel =
    pendingDecisionCount === 1
      ? "1 pending decision"
      : `${pendingDecisionCount} pending decisions`;

  return (
    <header className="sticky top-0 z-10 border-b border-border bg-surface pt-[env(safe-area-inset-top)]">
      <div className="flex h-14 items-center justify-between gap-3 px-4 lg:px-6">
        <div className="min-w-0">
          <p className="text-base font-semibold md:hidden">Jr Sanzy</p>
          <TodayDate />
        </div>
        <div className="flex items-center gap-2">
          <BackendStatus />
          <Link
            href="/decisions"
            aria-label={bellLabel}
            className="relative flex h-11 w-11 items-center justify-center rounded-full text-muted hover:bg-foreground/5 hover:text-foreground"
          >
            <NavIcon name="bell" />
            {pendingDecisionCount > 0 ? (
              <span
                aria-hidden="true"
                className="absolute right-1 top-1 flex h-5 min-w-5 items-center justify-center rounded-full bg-red-700 px-1 text-xs font-semibold text-white"
              >
                {pendingDecisionCount}
              </span>
            ) : null}
          </Link>
          <div
            role="img"
            aria-label="Account"
            className="flex h-9 w-9 items-center justify-center rounded-full bg-accent/15 text-sm font-semibold text-accent"
          >
            S
          </div>
        </div>
      </div>
    </header>
  );
}
