import {
  useInfiniteQuery,
  useMutation,
  useQueryClient,
  type InfiniteData,
  type UseInfiniteQueryResult,
  type UseMutationResult,
} from "@tanstack/react-query";

import { type ApiError, apiFetch } from "@/lib/api/client";
import type {
  DashboardRead,
  TaskCreate,
  TaskList,
  TaskPriority,
  TaskRead,
  TaskStatus,
  TaskUpdate,
} from "@/lib/api/types";
import { DASHBOARD_QUERY_KEY } from "@/hooks/useDashboard";

export const TASKS_QUERY_KEY = ["tasks"] as const;
const PAGE_SIZE = 20;

export interface TaskFilters {
  status: TaskStatus | "";
  priority: TaskPriority | "";
  q: string;
}

type TaskPages = InfiniteData<TaskList, string | null>;

function buildQueryString(filters: TaskFilters, cursor: string | null): string {
  const params = new URLSearchParams({ limit: String(PAGE_SIZE) });
  if (filters.status !== "") params.set("status", filters.status);
  if (filters.priority !== "") params.set("priority", filters.priority);
  if (filters.q.trim() !== "") params.set("q", filters.q.trim());
  if (cursor !== null) params.set("cursor", cursor);
  return params.toString();
}

export function useTasks(filters: TaskFilters): UseInfiniteQueryResult<TaskPages, ApiError> {
  return useInfiniteQuery<TaskList, ApiError, TaskPages, readonly unknown[], string | null>({
    queryKey: [...TASKS_QUERY_KEY, filters],
    initialPageParam: null,
    queryFn: ({ pageParam }) =>
      apiFetch<TaskList>(`/api/v1/tasks?${buildQueryString(filters, pageParam)}`),
    getNextPageParam: (lastPage) => lastPage.next_cursor,
  });
}

function useInvalidateTaskViews(): () => Promise<void> {
  const queryClient = useQueryClient();
  return async () => {
    await Promise.all([
      queryClient.invalidateQueries({ queryKey: TASKS_QUERY_KEY }),
      queryClient.invalidateQueries({ queryKey: DASHBOARD_QUERY_KEY }),
    ]);
  };
}

export function useCreateTask(): UseMutationResult<TaskRead, ApiError, TaskCreate> {
  const invalidateTaskViews = useInvalidateTaskViews();
  return useMutation<TaskRead, ApiError, TaskCreate>({
    mutationFn: (data) =>
      apiFetch<TaskRead>("/api/v1/tasks", { method: "POST", body: JSON.stringify(data) }),
    onSuccess: invalidateTaskViews,
  });
}

interface UpdateTaskVariables {
  id: string;
  data: TaskUpdate;
}

interface UpdateTaskContext {
  previousTasks: [readonly unknown[], TaskPages | undefined][];
  previousDashboard: DashboardRead | undefined;
}

export function useUpdateTask(): UseMutationResult<
  TaskRead,
  ApiError,
  UpdateTaskVariables,
  UpdateTaskContext
> {
  const queryClient = useQueryClient();
  const invalidateTaskViews = useInvalidateTaskViews();

  return useMutation<TaskRead, ApiError, UpdateTaskVariables, UpdateTaskContext>({
    mutationFn: ({ id, data }) =>
      apiFetch<TaskRead>(`/api/v1/tasks/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
    // Optimistic update so completing a task feels instant (PRD 7.3); rolled back on error.
    onMutate: async ({ id, data }) => {
      await Promise.all([
        queryClient.cancelQueries({ queryKey: TASKS_QUERY_KEY }),
        queryClient.cancelQueries({ queryKey: DASHBOARD_QUERY_KEY }),
      ]);
      const previousTasks = queryClient.getQueriesData<TaskPages>({ queryKey: TASKS_QUERY_KEY });
      const previousDashboard = queryClient.getQueryData<DashboardRead>(DASHBOARD_QUERY_KEY);

      const newStatus = data.status;
      if (newStatus !== undefined && newStatus !== null) {
        queryClient.setQueriesData<TaskPages>({ queryKey: TASKS_QUERY_KEY }, (pages) =>
          pages === undefined
            ? pages
            : {
                ...pages,
                pages: pages.pages.map((page) => ({
                  ...page,
                  items: page.items.map((task) =>
                    task.id === id ? { ...task, status: newStatus } : task,
                  ),
                })),
              },
        );
        if (previousDashboard !== undefined && newStatus !== "todo") {
          const groups = { ...previousDashboard.tasks_by_priority };
          for (const priority of Object.keys(groups) as TaskPriority[]) {
            const group = groups[priority];
            if (group.items.some((task) => task.id === id)) {
              groups[priority] = {
                items: group.items.filter((task) => task.id !== id),
                total: group.total - 1,
              };
            }
          }
          queryClient.setQueryData<DashboardRead>(DASHBOARD_QUERY_KEY, {
            ...previousDashboard,
            tasks_by_priority: groups,
          });
        }
      }
      return { previousTasks, previousDashboard };
    },
    onError: (_error, _variables, context) => {
      if (context === undefined) return;
      for (const [queryKey, pages] of context.previousTasks) {
        queryClient.setQueryData(queryKey, pages);
      }
      queryClient.setQueryData(DASHBOARD_QUERY_KEY, context.previousDashboard);
    },
    onSettled: invalidateTaskViews,
  });
}

export function useDeleteTask(): UseMutationResult<void, ApiError, string> {
  const invalidateTaskViews = useInvalidateTaskViews();
  return useMutation<void, ApiError, string>({
    mutationFn: (id) => apiFetch<void>(`/api/v1/tasks/${id}`, { method: "DELETE" }),
    onSuccess: invalidateTaskViews,
  });
}
