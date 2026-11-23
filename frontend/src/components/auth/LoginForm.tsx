"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import type { FormEvent } from "react";

import { useAuth } from "@/components/auth/AuthProvider";
import { getSupabase } from "@/lib/supabase";

const INPUT_CLASSES =
  "mt-1 min-h-11 w-full rounded-md border border-border bg-background px-3 text-base text-foreground";

export function LoginForm() {
  const router = useRouter();
  const { session } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (session !== null) {
      router.replace("/");
    }
  }, [session, router]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    setIsSubmitting(true);
    setErrorMessage(null);
    const { error } = await getSupabase().auth.signInWithPassword({ email, password });
    if (error) {
      setErrorMessage("Sign-in failed. Check your email and password.");
      setIsSubmitting(false);
    }
  }

  return (
    <form
      onSubmit={(event) => void handleSubmit(event)}
      className="w-full max-w-sm rounded-lg border border-border bg-surface p-6"
    >
      <h1 className="text-xl font-semibold">Jr Sanzy</h1>
      <p className="mt-1 text-sm text-muted">Sign in to continue.</p>

      <label className="mt-4 block text-sm font-medium">
        Email
        <input
          type="email"
          autoComplete="email"
          required
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          className={INPUT_CLASSES}
        />
      </label>
      <label className="mt-3 block text-sm font-medium">
        Password
        <input
          type="password"
          autoComplete="current-password"
          required
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          className={INPUT_CLASSES}
        />
      </label>

      {errorMessage !== null ? (
        <p role="alert" className="mt-3 text-sm text-red-700 dark:text-red-300">
          {errorMessage}
        </p>
      ) : null}

      <button
        type="submit"
        disabled={isSubmitting}
        className="mt-4 min-h-11 w-full rounded-md bg-accent px-4 text-sm font-semibold text-background disabled:opacity-60"
      >
        {isSubmitting ? "Signing in…" : "Sign in"}
      </button>
    </form>
  );
}
