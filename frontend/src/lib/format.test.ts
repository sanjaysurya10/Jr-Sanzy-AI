import { describe, expect, it } from "vitest";

import { fromDateTimeLocalValue, toDateTimeLocalValue } from "@/lib/format";

describe("datetime-local conversion", () => {
  it("round-trips a timestamp through the input value", () => {
    const original = "2030-06-15T10:30:00.000Z";

    expect(fromDateTimeLocalValue(toDateTimeLocalValue(original))).toBe(original);
  });

  it("treats an empty input as no due date, both ways", () => {
    expect(toDateTimeLocalValue(null)).toBe("");
    expect(fromDateTimeLocalValue("")).toBeNull();
  });

  it("produces the format datetime-local inputs require", () => {
    expect(toDateTimeLocalValue("2030-06-15T10:30:00.000Z")).toMatch(
      /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$/,
    );
  });
});
