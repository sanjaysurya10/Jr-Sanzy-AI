import { useQuery, type UseQueryResult } from "@tanstack/react-query";

import { type ApiError, apiFetch } from "@/lib/api/client";
import type { DashboardRead } from "@/lib/api/types";

export const DASHBOARD_QUERY_KEY = ["dashboard"] as const;
const DASHBOARD_REFETCH_INTERVAL_MS = 60_000;

// Refetches on window focus (the default) and every 60 s while the tab is visible (FR-DASH-6).
export function useDashboard(): UseQueryResult<DashboardRead, ApiError> {
  return useQuery<DashboardRead, ApiError>({
    queryKey: DASHBOARD_QUERY_KEY,
    queryFn: () => apiFetch<DashboardRead>("/api/v1/dashboard"),
    refetchInterval: DASHBOARD_REFETCH_INTERVAL_MS,
    refetchIntervalInBackground: false,
  });
}
