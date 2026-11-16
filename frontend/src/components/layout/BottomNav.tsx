"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";

import { NavIcon } from "@/components/layout/NavIcon";
import { BOTTOM_NAV_ITEMS, MORE_ITEMS, isActivePath } from "@/components/layout/navigation";

const ITEM_CLASSES =
  "flex min-h-14 w-full flex-col items-center justify-center gap-0.5 text-xs font-medium";

export function BottomNav() {
  const pathname = usePathname();
  const [isMoreOpen, setIsMoreOpen] = useState(false);
  const isMoreActive = MORE_ITEMS.some((item) => isActivePath(pathname, item.href));

  return (
    <nav
      aria-label="Main"
      className="fixed inset-x-0 bottom-0 z-20 border-t border-border bg-surface pb-[env(safe-area-inset-bottom)] md:hidden"
    >
      {isMoreOpen ? (
        <ul id="more-menu" className="border-b border-border px-2 py-1">
          {MORE_ITEMS.map((item) => (
            <li key={item.href}>
              <Link
                href={item.href}
                aria-current={isActivePath(pathname, item.href) ? "page" : undefined}
                onClick={() => setIsMoreOpen(false)}
                className="flex min-h-11 items-center gap-3 rounded-md px-3 text-sm font-medium text-foreground"
              >
                <NavIcon name={item.icon} />
                {item.label}
              </Link>
            </li>
          ))}
        </ul>
      ) : null}
      <ul className="grid grid-cols-5">
        {BOTTOM_NAV_ITEMS.map((item) => {
          const isActive = isActivePath(pathname, item.href);
          return (
            <li key={item.href}>
              <Link
                href={item.href}
                aria-current={isActive ? "page" : undefined}
                onClick={() => setIsMoreOpen(false)}
                className={`${ITEM_CLASSES} ${isActive ? "text-accent" : "text-muted"}`}
              >
                <NavIcon name={item.icon} />
                {item.label}
              </Link>
            </li>
          );
        })}
        <li>
          <button
            type="button"
            aria-expanded={isMoreOpen}
            aria-controls="more-menu"
            onClick={() => setIsMoreOpen((wasOpen) => !wasOpen)}
            className={`${ITEM_CLASSES} ${isMoreOpen || isMoreActive ? "text-accent" : "text-muted"}`}
          >
            <NavIcon name="more" />
            More
          </button>
        </li>
      </ul>
    </nav>
  );
}
