"use client";

import { useState } from "react";
import Link from "next/link";
import { AuthShell } from "@/components/auth/AuthShell";
import { Button } from "@/components/ui/Button";
import { supabase } from "@/lib/supabase";
import { CheckCircle2 } from "lucide-react";

export default function ResetPasswordPage() {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sent, setSent] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    const { error } = await supabase.auth.resetPasswordForEmail(email, {
      redirectTo: `${window.location.origin}/auth/callback?next=/settings`,
    });
    setLoading(false);
    if (error) {
      setError(error.message);
      return;
    }
    setSent(true);
  }

  if (sent) {
    return (
      <AuthShell title="Check your inbox" subtitle="" footer={<Link href="/sign-in" className="text-spectrum-cyan hover:underline">Back to sign in</Link>}>
        <div className="flex flex-col items-center gap-3 py-4 text-center">
          <CheckCircle2 size={28} className="text-signal-good" />
          <p className="text-sm text-text-muted">If an account exists for {email}, a reset link is on its way.</p>
        </div>
      </AuthShell>
    );
  }

  return (
    <AuthShell
      title="Reset your password"
      subtitle="We'll email you a link to set a new one."
      footer={<Link href="/sign-in" className="text-spectrum-cyan hover:underline">Back to sign in</Link>}
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
        {error && <p className="text-sm text-signal-bad">{error}</p>}
        <Button type="submit" disabled={loading} className="w-full">
          {loading ? "Sending…" : "Send reset link"}
        </Button>
      </form>
    </AuthShell>
  );
}
