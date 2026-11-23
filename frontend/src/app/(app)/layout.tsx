import type { ReactNode } from "react";

import { AuthGuard } from "@/components/auth/AuthGuard";
import { BottomNav } from "@/components/layout/BottomNav";
import { Header } from "@/components/layout/Header";
import { Sidebar } from "@/components/layout/Sidebar";

interface AppLayoutProps {
  children: ReactNode;
}

export default function AppLayout({ children }: AppLayoutProps) {
  return (
    <AuthGuard>
      <Sidebar />
      <div className="flex min-h-dvh flex-col md:pl-16 lg:pl-56">
        {/* The pending-decision count comes from the decisions API in Phase 9. */}
        <Header pendingDecisionCount={0} />
        <main className="flex-1 px-4 pb-[calc(5rem+env(safe-area-inset-bottom))] pt-4 md:pb-8 lg:px-6">
          {children}
        </main>
      </div>
      <BottomNav />
    </AuthGuard>
  );
}
