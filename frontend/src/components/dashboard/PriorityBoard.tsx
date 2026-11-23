import { PriorityColumn } from "@/components/dashboard/PriorityColumn";
import { PRIORITY_ORDER, type TaskPriority, type TasksByPriority } from "@/lib/api/types";

const OPEN_BY_DEFAULT_ON_MOBILE: ReadonlySet<TaskPriority> = new Set(["critical", "high"]);

interface PriorityBoardProps {
  groups: TasksByPriority;
}

export function PriorityBoard({ groups }: PriorityBoardProps) {
  return (
    <section aria-labelledby="priority-board-title">
      <h2 id="priority-board-title" className="sr-only">
        Tasks by priority
      </h2>
      <div className="grid grid-cols-1 gap-3 md:grid-cols-2 lg:grid-cols-4">
        {PRIORITY_ORDER.map((priority) => (
          <PriorityColumn
            key={priority}
            priority={priority}
            tasks={groups[priority].items}
            total={groups[priority].total}
            isOpenByDefaultOnMobile={OPEN_BY_DEFAULT_ON_MOBILE.has(priority)}
          />
        ))}
      </div>
    </section>
  );
}
