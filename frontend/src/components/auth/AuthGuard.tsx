"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";
import type { ReactNode } from "react";

import { useAuth } from "@/components/auth/AuthProvider";

interface AuthGuardProps {
  children: ReactNode;
}

export function AuthGuard({ children }: AuthGuardProps) {
  const { session, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && session === null) {
      router.replace("/login");
    }
  }, [isLoading, session, router]);

  if (isLoading || session === null) {
    return (
      <p role="status" className="p-6 text-sm text-muted">
        Loading…
      </p>
    );
  }

  return <>{children}</>;
}
