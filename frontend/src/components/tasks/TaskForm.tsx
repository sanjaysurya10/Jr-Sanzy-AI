"use client";

import { useState } from "react";
import type { FormEvent } from "react";

import {
  PRIORITY_LABELS,
  PRIORITY_ORDER,
  type TaskCreate,
  type TaskPriority,
  type TaskRead,
} from "@/lib/api/types";
import { fromDateTimeLocalValue, toDateTimeLocalValue } from "@/lib/format";

const FIELD_CLASSES =
  "mt-1 min-h-11 w-full rounded-md border border-border bg-background px-3 text-base text-foreground";
const MAX_TITLE_LENGTH = 200;

interface TaskFormProps {
  initialTask?: TaskRead;
  submitLabel: string;
  isSubmitting: boolean;
  errorMessage: string | null;
  onSubmit: (data: TaskCreate) => void;
  onCancel?: () => void;
}

export function TaskForm({
  initialTask,
  submitLabel,
  isSubmitting,
  errorMessage,
  onSubmit,
  onCancel,
}: TaskFormProps) {
  const [title, setTitle] = useState(initialTask?.title ?? "");
  const [notes, setNotes] = useState(initialTask?.notes ?? "");
  const [priority, setPriority] = useState<TaskPriority>(initialTask?.priority ?? "normal");
  const [dueAt, setDueAt] = useState(toDateTimeLocalValue(initialTask?.due_at ?? null));

  function handleSubmit(event: FormEvent<HTMLFormElement>): void {
    event.preventDefault();
    onSubmit({
      title: title.trim(),
      notes: notes.trim() === "" ? null : notes.trim(),
      priority,
      due_at: fromDateTimeLocalValue(dueAt),
    });
    if (initialTask === undefined) {
      setTitle("");
      setNotes("");
      setDueAt("");
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="grid grid-cols-1 gap-3 rounded-lg border border-border bg-surface p-4 sm:grid-cols-2"
    >
      <label className="block text-sm font-medium sm:col-span-2">
        Title
        <input
          type="text"
          required
          maxLength={MAX_TITLE_LENGTH}
          value={title}
          onChange={(event) => setTitle(event.target.value)}
          className={FIELD_CLASSES}
        />
      </label>
      <label className="block text-sm font-medium">
        Priority
        <select
          value={priority}
          onChange={(event) => setPriority(event.target.value as TaskPriority)}
          className={FIELD_CLASSES}
        >
          {PRIORITY_ORDER.map((option) => (
            <option key={option} value={option}>
              {PRIORITY_LABELS[option]}
            </option>
          ))}
        </select>
      </label>
      <label className="block text-sm font-medium">
        Due
        <input
          type="datetime-local"
          value={dueAt}
          onChange={(event) => setDueAt(event.target.value)}
          className={FIELD_CLASSES}
        />
      </label>
      <label className="block text-sm font-medium sm:col-span-2">
        Notes
        <textarea
          rows={2}
          value={notes}
          onChange={(event) => setNotes(event.target.value)}
          className={`${FIELD_CLASSES} py-2`}
        />
      </label>
      {errorMessage !== null ? (
        <p role="alert" className="text-sm text-red-700 dark:text-red-300 sm:col-span-2">
          {errorMessage}
        </p>
      ) : null}
      <div className="flex gap-2 sm:col-span-2">
        <button
          type="submit"
          disabled={isSubmitting || title.trim() === ""}
          className="min-h-11 rounded-md bg-accent px-4 text-sm font-semibold text-background disabled:opacity-60"
        >
          {submitLabel}
        </button>
        {onCancel !== undefined ? (
          <button
            type="button"
            onClick={onCancel}
            className="min-h-11 rounded-md border border-border px-4 text-sm font-medium"
          >
            Cancel
          </button>
        ) : null}
      </div>
    </form>
  );
}
