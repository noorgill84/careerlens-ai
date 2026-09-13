import DashboardShellLayout from "@/components/layout/DashboardShellLayout";
import { RequireAuth } from "@/components/auth/RequireAuth";

export default function ProtectedShellLayout({ children }: { children: React.ReactNode }) {
  return (
    <RequireAuth>
      <DashboardShellLayout>{children}</DashboardShellLayout>
    </RequireAuth>
  );
}
