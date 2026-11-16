"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import type { ReactNode } from "react";

let browserQueryClient: QueryClient | undefined;

function getQueryClient(): QueryClient {
  // A fresh client per server render; one shared client in the browser.
  if (typeof window === "undefined") {
    return new QueryClient();
  }
  browserQueryClient ??= new QueryClient();
  return browserQueryClient;
}

interface ProvidersProps {
  children: ReactNode;
}

export function Providers({ children }: ProvidersProps) {
  return <QueryClientProvider client={getQueryClient()}>{children}</QueryClientProvider>;
}
