// Static placeholder data for the Phase 2 dashboard. Replaced by GET /api/v1/dashboard
// and the generated API types in Phase 4.

export type Priority = "critical" | "high" | "normal" | "low";

export interface PlaceholderTask {
  id: string;
  title: string;
  priority: Priority;
  dueLabel: string | null;
}

export interface PlaceholderBriefing {
  headline: string;
  bullets: string[];
}

export interface PlaceholderDecision {
  id: string;
  title: string;
  rationale: string;
}

export interface PlaceholderActivity {
  id: string;
  actor: string;
  summary: string;
  timeLabel: string;
}

export const PLACEHOLDER_BRIEFING: PlaceholderBriefing = {
  headline: "One critical task and two interviews to prepare for today.",
  bullets: [
    "Submit the visa renewal form before 17:00.",
    "Two high-priority tasks are due today.",
    "Three decisions are waiting for your approval.",
  ],
};

export const PLACEHOLDER_TASKS: PlaceholderTask[] = [
  { id: "t1", title: "Submit visa renewal form", priority: "critical", dueLabel: "Today 17:00" },
  { id: "t2", title: "Prepare for backend interview", priority: "high", dueLabel: "Today" },
  { id: "t3", title: "Reply to recruiter about start date", priority: "high", dueLabel: "Today" },
  { id: "t4", title: "Update CV with latest project", priority: "normal", dueLabel: "Tomorrow" },
  { id: "t5", title: "Book dentist appointment", priority: "normal", dueLabel: null },
  { id: "t6", title: "Review system design notes", priority: "normal", dueLabel: "Thursday" },
  { id: "t7", title: "Renew gym membership", priority: "normal", dueLabel: "Friday" },
  { id: "t8", title: "Plan meals for the week", priority: "normal", dueLabel: null },
  { id: "t9", title: "Back up laptop", priority: "normal", dueLabel: null },
  { id: "t10", title: "Clean up downloads folder", priority: "normal", dueLabel: null },
];

export const PLACEHOLDER_DECISIONS: PlaceholderDecision[] = [
  {
    id: "d1",
    title: "Add task: apply for Backend Engineer role",
    rationale: "Matches your target role and location.",
  },
  {
    id: "d2",
    title: "Add task: confirm interview slot",
    rationale: "The email asks for a reply by Wednesday.",
  },
  {
    id: "d3",
    title: "Add task: complete coding assessment",
    rationale: "Deadline mentioned in the subject line.",
  },
];

export const PLACEHOLDER_ACTIVITY: PlaceholderActivity[] = [
  { id: "a1", actor: "You", summary: "Completed “Send signed contract”", timeLabel: "09:12" },
  { id: "a2", actor: "System", summary: "Email sync found 4 new job emails", timeLabel: "09:00" },
  { id: "a3", actor: "You", summary: "Created “Prepare for backend interview”", timeLabel: "08:47" },
  { id: "a4", actor: "System", summary: "Morning briefing generated", timeLabel: "07:31" },
];
