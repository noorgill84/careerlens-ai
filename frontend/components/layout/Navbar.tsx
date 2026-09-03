"use client";

import Link from "next/link";
import { Button } from "@/components/ui/Button";
import { useAuth } from "@/lib/auth-context";

export function Navbar() {
  const { session, loading } = useAuth();

  return (
    <header className="sticky top-0 z-50 border-b border-border/60 bg-base/80 backdrop-blur-md">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
        <Link href="/" className="flex items-center gap-2">
          <span className="h-2 w-2 rounded-full bg-spectrum-gradient" />
          <span className="font-display text-lg font-semibold tracking-tight">CareerLens AI</span>
        </Link>
        <nav className="hidden items-center gap-8 md:flex">
          <Link href="/#features" className="text-sm text-text-muted hover:text-text-primary">Features</Link>
          <Link href="/#how-it-works" className="text-sm text-text-muted hover:text-text-primary">How it works</Link>
          <Link href="/#technology" className="text-sm text-text-muted hover:text-text-primary">Technology</Link>
        </nav>
        <div className="flex items-center gap-3">
          {!loading && !session && (
            <Link href="/sign-in" className="hidden text-sm text-text-muted hover:text-text-primary sm:inline">Sign in</Link>
          )}
          <Link href={session ? "/dashboard" : "/resume-analyzer"}>
            <Button size="sm">{session ? "Go to Dashboard" : "Try Demo"}</Button>
          </Link>
        </div>
      </div>
    </header>
  );
}
