"use client";

import { useQueryClient } from "@tanstack/react-query";
import type { Session } from "@supabase/supabase-js";
import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";

import { setAuthHandlers } from "@/lib/api/client";
import { getSupabase } from "@/lib/supabase";

interface AuthState {
  session: Session | null;
  isLoading: boolean;
  signOut: () => Promise<void>;
}

const AuthContext = createContext<AuthState | null>(null);

export function useAuth(): AuthState {
  const state = useContext(AuthContext);
  if (state === null) {
    throw new Error("useAuth must be used inside AuthProvider");
  }
  return state;
}

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const queryClient = useQueryClient();
  const [session, setSession] = useState<Session | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const supabase = getSupabase();
    let isActive = true;

    supabase.auth.getSession().then(({ data }) => {
      if (isActive) {
        setSession(data.session);
        setIsLoading(false);
      }
    });

    const { data: subscription } = supabase.auth.onAuthStateChange((event, nextSession) => {
      setSession(nextSession);
      setIsLoading(false);
      if (event === "SIGNED_OUT") {
        queryClient.clear();
      }
    });

    setAuthHandlers({
      getAccessToken: async () => (await supabase.auth.getSession()).data.session?.access_token ?? null,
      refreshAccessToken: async () =>
        (await supabase.auth.refreshSession()).data.session?.access_token ?? null,
      onSessionExpired: () => {
        void supabase.auth.signOut();
      },
    });

    return () => {
      isActive = false;
      subscription.subscription.unsubscribe();
      setAuthHandlers(null);
    };
  }, [queryClient]);

  const signOut = useCallback(async () => {
    await getSupabase().auth.signOut();
  }, []);

  const value = useMemo(() => ({ session, isLoading, signOut }), [session, isLoading, signOut]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
