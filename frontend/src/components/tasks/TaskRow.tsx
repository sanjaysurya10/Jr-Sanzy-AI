"use client";

import { useState } from "react";

import { TaskItem } from "@/components/dashboard/TaskItem";
import { TaskForm } from "@/components/tasks/TaskForm";
import { useDeleteTask, useUpdateTask } from "@/hooks/useTasks";
import type { TaskRead } from "@/lib/api/types";

const ACTION_BUTTON_CLASSES = "min-h-11 rounded-md px-3 text-sm font-medium text-accent hover:underline";

interface TaskRowProps {
  task: TaskRead;
}

export function TaskRow({ task }: TaskRowProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [isConfirmingDelete, setIsConfirmingDelete] = useState(false);
  const updateTask = useUpdateTask();
  const deleteTask = useDeleteTask();

  if (isEditing) {
    return (
      <li>
        <TaskForm
          initialTask={task}
          submitLabel="Save"
          isSubmitting={updateTask.isPending}
          errorMessage={updateTask.isError ? updateTask.error.message : null}
          onSubmit={(data) =>
            updateTask.mutate({ id: task.id, data }, { onSuccess: () => setIsEditing(false) })
          }
          onCancel={() => setIsEditing(false)}
        />
      </li>
    );
  }

  return (
    <TaskItem
      task={task}
      showPriority
      actions={
        <div className="-ml-3 mt-1 flex flex-wrap items-center">
          <button type="button" onClick={() => setIsEditing(true)} className={ACTION_BUTTON_CLASSES}>
            Edit
          </button>
          {isConfirmingDelete ? (
            <>
              <button
                type="button"
                onClick={() => deleteTask.mutate(task.id)}
                disabled={deleteTask.isPending}
                className="min-h-11 rounded-md px-3 text-sm font-semibold text-red-700 hover:underline dark:text-red-300"
              >
                Confirm delete
              </button>
              <button
                type="button"
                onClick={() => setIsConfirmingDelete(false)}
                className={ACTION_BUTTON_CLASSES}
              >
                Keep
              </button>
            </>
          ) : (
            <button
              type="button"
              onClick={() => setIsConfirmingDelete(true)}
              className={ACTION_BUTTON_CLASSES}
            >
              Delete
            </button>
          )}
          {deleteTask.isError ? (
            <span role="alert" className="text-xs text-red-700 dark:text-red-300">
              {deleteTask.error.message}
            </span>
          ) : null}
        </div>
      }
    />
  );
}
