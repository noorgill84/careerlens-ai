import DashboardShellLayout from "@/components/layout/DashboardShellLayout";

export default function Layout({ children }: { children: React.ReactNode }) {
  return <DashboardShellLayout>{children}</DashboardShellLayout>;
}
