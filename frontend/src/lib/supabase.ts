import { createClient, type SupabaseClient } from "@supabase/supabase-js";

let supabaseClient: SupabaseClient | undefined;

// Created on first use, in the browser only, so server renders and tests need no env vars.
export function getSupabase(): SupabaseClient {
  if (supabaseClient) {
    return supabaseClient;
  }
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const anonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
  if (!url || !anonKey) {
    throw new Error("NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY must be set");
  }
  supabaseClient = createClient(url, anonKey);
  return supabaseClient;
}
