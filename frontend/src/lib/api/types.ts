// Aliases for types generated from the backend's OpenAPI spec (schema.d.ts).
// Nothing here is hand-written; regenerate with `npm run gen:api`.
import type { components } from "@/lib/api/schema";

type Schemas = components["schemas"];

export type TaskRead = Schemas["TaskRead"];
export type TaskCreate = Schemas["TaskCreate"];
export type TaskUpdate = Schemas["TaskUpdate"];
export type TaskList = Schemas["TaskList"];
export type DashboardRead = Schemas["DashboardRead"];
export type TasksByPriority = Schemas["TasksByPriority"];
export type ActivityRead = Schemas["ActivityRead"];

export type TaskPriority = TaskRead["priority"];
export type TaskStatus = TaskRead["status"];

export const PRIORITY_ORDER: readonly TaskPriority[] = ["critical", "high", "normal", "low"];

export const PRIORITY_LABELS: Record<TaskPriority, string> = {
  critical: "Critical",
  high: "High",
  normal: "Normal",
  low: "Low",
};
