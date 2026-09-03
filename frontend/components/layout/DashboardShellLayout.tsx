import { Sidebar } from "@/components/layout/Sidebar";

// Unprotected shell — used by routes that work for anonymous visitors too
// (resume-analyzer, job-matcher, job-analyzer), so the "Try Demo" flow from
// the landing page never hits a login wall. See ProtectedShellLayout for
// routes that require a stored resume/account (dashboard, history, etc.).
export default function DashboardShellLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <div className="min-w-0 flex-1 px-6 py-8 md:px-10">{children}</div>
    </div>
  );
}
