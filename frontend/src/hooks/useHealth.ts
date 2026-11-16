import { useQuery, type UseQueryResult } from "@tanstack/react-query";

import { type ApiError, apiFetch } from "@/lib/api/client";
import type { components } from "@/lib/api/schema";

type HealthResponse = components["schemas"]["HealthResponse"];

const HEALTH_REFETCH_INTERVAL_MS = 60_000;

export function useHealth(): UseQueryResult<HealthResponse, ApiError> {
  return useQuery<HealthResponse, ApiError>({
    queryKey: ["health"],
    queryFn: () => apiFetch<HealthResponse>("/api/v1/health"),
    refetchInterval: HEALTH_REFETCH_INTERVAL_MS,
    retry: 1,
  });
}
