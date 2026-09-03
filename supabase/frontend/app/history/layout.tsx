import ProtectedShellLayout from "@/components/layout/ProtectedShellLayout";

export default function Layout({ children }: { children: React.ReactNode }) {
  return <ProtectedShellLayout>{children}</ProtectedShellLayout>;
}
