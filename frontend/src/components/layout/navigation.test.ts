import { describe, expect, it } from "vitest";

import {
  BOTTOM_NAV_ITEMS,
  MORE_ITEMS,
  SIDEBAR_ITEMS,
  isActivePath,
} from "@/components/layout/navigation";

describe("navigation", () => {
  it("offers every sidebar destination on mobile through the bottom nav or More", () => {
    const mobileHrefs = [...BOTTOM_NAV_ITEMS, ...MORE_ITEMS].map((item) => item.href).sort();
    const sidebarHrefs = SIDEBAR_ITEMS.map((item) => item.href).sort();

    expect(mobileHrefs).toEqual(sidebarHrefs);
  });

  it("keeps the bottom nav at five items including More", () => {
    expect(BOTTOM_NAV_ITEMS).toHaveLength(4);
  });

  it("marks the dashboard active only on the exact root path", () => {
    expect(isActivePath("/", "/")).toBe(true);
    expect(isActivePath("/tasks", "/")).toBe(false);
  });

  it("marks a section active on its own path and nested paths only", () => {
    expect(isActivePath("/tasks", "/tasks")).toBe(true);
    expect(isActivePath("/tasks/123", "/tasks")).toBe(true);
    expect(isActivePath("/tasks-archive", "/tasks")).toBe(false);
    expect(isActivePath(null, "/tasks")).toBe(false);
  });
});
