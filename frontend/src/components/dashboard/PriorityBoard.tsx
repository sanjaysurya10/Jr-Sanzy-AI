import { PriorityColumn } from "@/components/dashboard/PriorityColumn";
import type { PlaceholderTask, Priority } from "@/lib/placeholder";

const PRIORITY_ORDER: readonly Priority[] = ["critical", "high", "normal", "low"];
const OPEN_BY_DEFAULT_ON_MOBILE: ReadonlySet<Priority> = new Set(["critical", "high"]);

interface PriorityBoardProps {
  tasks: PlaceholderTask[];
}

export function PriorityBoard({ tasks }: PriorityBoardProps) {
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
            tasks={tasks.filter((task) => task.priority === priority)}
            isOpenByDefaultOnMobile={OPEN_BY_DEFAULT_ON_MOBILE.has(priority)}
          />
        ))}
      </div>
    </section>
  );
}
