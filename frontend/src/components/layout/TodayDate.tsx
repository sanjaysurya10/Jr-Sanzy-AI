"use client";

import { useSyncExternalStore } from "react";

const DATE_FORMAT = new Intl.DateTimeFormat("en-IE", {
  weekday: "long",
  day: "numeric",
  month: "long",
});

function subscribeToNothing(): () => void {
  return () => {};
}

function getTodayLabel(): string {
  return DATE_FORMAT.format(new Date());
}

function getServerLabel(): string {
  return "";
}

// The date is the viewer's local date, so it is only known in the browser.
export function TodayDate() {
  const todayLabel = useSyncExternalStore(subscribeToNothing, getTodayLabel, getServerLabel);

  return <p className="min-h-5 truncate text-sm text-muted">{todayLabel}</p>;
}
