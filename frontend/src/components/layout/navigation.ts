import type { IconName } from "@/components/layout/NavIcon";

export interface NavItem {
  href: string;
  label: string;
  icon: IconName;
}

export const SIDEBAR_ITEMS: readonly NavItem[] = [
  { href: "/", label: "Dashboard", icon: "home" },
  { href: "/tasks", label: "Tasks", icon: "tasks" },
  { href: "/food", label: "Food", icon: "food" },
  { href: "/inbox", label: "Inbox", icon: "inbox" },
  { href: "/decisions", label: "Decisions", icon: "decisions" },
  { href: "/history", label: "History", icon: "history" },
  { href: "/settings", label: "Settings", icon: "settings" },
];

export const BOTTOM_NAV_ITEMS: readonly NavItem[] = [
  { href: "/", label: "Home", icon: "home" },
  { href: "/tasks", label: "Tasks", icon: "tasks" },
  { href: "/food", label: "Food", icon: "food" },
  { href: "/decisions", label: "Decisions", icon: "decisions" },
];

export const MORE_ITEMS: readonly NavItem[] = [
  { href: "/inbox", label: "Inbox", icon: "inbox" },
  { href: "/history", label: "History", icon: "history" },
  { href: "/settings", label: "Settings", icon: "settings" },
];

export function isActivePath(pathname: string | null, href: string): boolean {
  if (pathname === null) {
    return false;
  }
  return href === "/" ? pathname === "/" : pathname === href || pathname.startsWith(`${href}/`);
}
