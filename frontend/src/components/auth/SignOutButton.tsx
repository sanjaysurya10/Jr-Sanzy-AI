"use client";

import { useAuth } from "@/components/auth/AuthProvider";

export function SignOutButton() {
  const { signOut } = useAuth();

  return (
    <button
      type="button"
      onClick={() => void signOut()}
      className="min-h-11 rounded-md px-3 text-sm font-medium text-muted hover:bg-foreground/5 hover:text-foreground"
    >
      Sign out
    </button>
  );
}
