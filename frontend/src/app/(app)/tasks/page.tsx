import { Suspense } from "react";

import { TasksView } from "@/components/tasks/TasksView";

export default function TasksPage() {
  return (
    <Suspense fallback={null}>
      <TasksView />
    </Suspense>
  );
}
