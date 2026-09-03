"use client";

import { useState } from "react";
import Link from "next/link";
import { AuthShell } from "@/components/auth/AuthShell";
import { Button } from "@/components/ui/Button";
import { supabase } from "@/lib/supabase";
import { CheckCircle2 } from "lucide-react";

export default function SignUpPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [submitted, setSubmitted] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);

    if (password.length < 8) {
      setError("Password must be at least 8 characters.");
      return;
    }

    setLoading(true);
    // Supabase Auth handles password hashing/storage entirely — we never
    // touch or store raw passwords ourselves (spec §26).
    const { error } = await supabase.auth.signUp({
      email,
      password,
      options: { emailRedirectTo: `${window.location.origin}/auth/callback` },
    });
    setLoading(false);

    if (error) {
      setError(error.message);
      return;
    }
    setSubmitted(true);
  }

  if (submitted) {
    return (
      <AuthShell title="Check your inbox" subtitle="" footer={<Link href="/sign-in" className="text-spectrum-cyan hover:underline">Back to sign in</Link>}>
        <div className="flex flex-col items-center gap-3 py-4 text-center">
          <CheckCircle2 size={28} className="text-signal-good" />
          <p className="text-sm text-text-muted">
            We sent a confirmation link to <span className="text-text-primary">{email}</span>. Click it to activate your account.
          </p>
        </div>
      </AuthShell>
    );
  }

  return (
    <AuthShell
      title="Create your account"
      subtitle="Start with a free AI-powered resume analysis."
      footer={
        <>
          Already have an account?{" "}
          <Link href="/sign-in" className="text-spectrum-cyan hover:underline">Sign in</Link>
        </>
      }
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="email" className="mb-1.5 block text-sm text-text-muted">Email</label>
          <input
            id="email"
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full rounded-lg border border-border bg-surface-raised px-3.5 py-2.5 text-sm text-text-primary focus:outline-none"
          />
        </div>
        <div>
          <label htmlFor="password" className="mb-1.5 block text-sm text-text-muted">Password</label>
          <input
            id="password"
            type="password"
            required
            minLength={8}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full rounded-lg border border-border bg-surface-raised px-3.5 py-2.5 text-sm text-text-primary focus:outline-none"
          />
          <p className="mt-1 text-xs text-text-faint">At least 8 characters.</p>
        </div>
        {error && <p className="text-sm text-signal-bad">{error}</p>}
        <Button type="submit" disabled={loading} className="w-full">
          {loading ? "Creating account…" : "Create account"}
        </Button>
      </form>
    </AuthShell>
  );
}
