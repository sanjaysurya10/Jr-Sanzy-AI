import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { BriefingCard } from "@/components/dashboard/BriefingCard";

describe("BriefingCard", () => {
  it("shows the headline and every bullet", () => {
    render(
      <BriefingCard
        briefing={{ headline: "Two tasks due today.", bullets: ["First bullet", "Second bullet"] }}
      />,
    );

    expect(screen.getByText("Two tasks due today.")).toBeTruthy();
    expect(screen.getAllByRole("listitem")).toHaveLength(2);
  });

  it("shows an empty state when there is no briefing", () => {
    render(<BriefingCard briefing={null} />);

    expect(screen.getByText("No briefing yet today.")).toBeTruthy();
    expect(screen.queryByRole("list")).toBeNull();
  });
});
