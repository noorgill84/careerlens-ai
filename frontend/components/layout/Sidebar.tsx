"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { cn } from "@/lib/utils";
import { useAuth } from "@/lib/auth-context";
import { supabase } from "@/lib/supabase";
import {
  LayoutDashboard, FileSearch, Briefcase, FileText, Compass, GitCompare, History, Settings, Menu, X, LogOut,
} from "lucide-react";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/resume-analyzer", label: "Resume Analyzer", icon: FileSearch },
  { href: "/job-matcher", label: "Job Matcher", icon: Briefcase },
  { href: "/job-analyzer", label: "Job Analyzer", icon: FileText },
  { href: "/career-insights", label: "Career Insights", icon: Compass },
  { href: "/compare", label: "Compare", icon: GitCompare },
  { href: "/history", label: "History", icon: History },
  { href: "/settings", label: "Settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);
  const { user } = useAuth();

  async function handleSignOut() {
    await supabase.auth.signOut();
    window.location.href = "/";
  }

  return (
    <>
      <button
        onClick={() => setOpen(true)}
        className="fixed left-4 top-4 z-40 rounded-lg border border-border bg-surface p-2 md:hidden"
        aria-label="Open navigation"
      >
        <Menu size={18} />
      </button>

      {open && (
        <div className="fixed inset-0 z-50 bg-black/60 md:hidden" onClick={() => setOpen(false)}>
          <div className="h-full w-64 bg-surface p-4" onClick={(e) => e.stopPropagation()}>
            <button onClick={() => setOpen(false)} className="mb-6 rounded-lg border border-border p-2" aria-label="Close navigation">
              <X size={18} />
            </button>
            <NavLinks pathname={pathname} onNavigate={() => setOpen(false)} />
          </div>
        </div>
      )}

      <aside className="sticky top-0 hidden h-screen w-60 shrink-0 border-r border-border bg-surface/60 p-4 md:block">
        <Link href="/" className="mb-8 flex items-center gap-2 px-2">
          <span className="h-2 w-2 rounded-full bg-spectrum-gradient" />
          <span className="font-display text-base font-semibold">CareerLens AI</span>
        </Link>
        <NavLinks pathname={pathname} />
        <div className="absolute bottom-4 left-4 right-4 border-t border-border pt-3">
          {user?.email && <p className="mb-2 truncate px-3 text-xs text-text-faint">{user.email}</p>}
          <button
            onClick={handleSignOut}
            className="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm text-text-muted hover:bg-surface-raised/60 hover:text-text-primary"
          >
            <LogOut size={17} /> Sign out
          </button>
        </div>
      </aside>
    </>
  );
}

function NavLinks({ pathname, onNavigate }: { pathname: string; onNavigate?: () => void }) {
  return (
    <nav className="flex flex-col gap-1">
      {NAV_ITEMS.map(({ href, label, icon: Icon }) => {
        const active = pathname === href;
        return (
          <Link
            key={href}
            href={href}
            onClick={onNavigate}
            className={cn(
              "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm transition-colors",
              active
                ? "bg-surface-raised text-text-primary"
                : "text-text-muted hover:bg-surface-raised/60 hover:text-text-primary"
            )}
          >
            <Icon size={17} className={active ? "text-spectrum-cyan" : ""} />
            {label}
          </Link>
        );
      })}
    </nav>
  );
}
