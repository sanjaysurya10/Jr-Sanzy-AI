"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { NavIcon } from "@/components/layout/NavIcon";
import { SIDEBAR_ITEMS, isActivePath } from "@/components/layout/navigation";

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed inset-y-0 left-0 z-20 hidden w-16 flex-col border-r border-border bg-surface md:flex lg:w-56">
      <div className="flex h-14 items-center justify-center border-b border-border px-4 lg:justify-start">
        <span className="text-base font-semibold lg:hidden" aria-hidden="true">
          JS
        </span>
        <span className="sr-only text-base font-semibold lg:not-sr-only">Jr Sanzy</span>
      </div>
      <nav aria-label="Main" className="flex-1 overflow-y-auto p-2">
        <ul className="flex flex-col gap-1">
          {SIDEBAR_ITEMS.map((item) => {
            const isActive = isActivePath(pathname, item.href);
            return (
              <li key={item.href}>
                <Link
                  href={item.href}
                  aria-current={isActive ? "page" : undefined}
                  title={item.label}
                  className={`flex min-h-11 items-center justify-center gap-3 rounded-md px-3 text-sm font-medium lg:justify-start ${
                    isActive
                      ? "bg-accent/10 text-accent"
                      : "text-muted hover:bg-foreground/5 hover:text-foreground"
                  }`}
                >
                  <NavIcon name={item.icon} />
                  <span className="sr-only lg:not-sr-only">{item.label}</span>
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>
    </aside>
  );
}
