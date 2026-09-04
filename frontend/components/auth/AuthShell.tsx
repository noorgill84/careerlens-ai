import Link from "next/link";

export function AuthShell({
  title,
  subtitle,
  children,
  footer,
}: {
  title: string;
  subtitle: string;
  children: React.ReactNode;
  footer: React.ReactNode;
}) {
  return (
    <main className="flex min-h-screen items-center justify-center px-6 py-16">
      <div className="w-full max-w-sm">
        <Link href="/" className="mb-8 flex items-center justify-center gap-2">
          <span className="h-2 w-2 rounded-full bg-spectrum-gradient" />
          <span className="font-display text-lg font-semibold">CareerLens AI</span>
        </Link>
        <div className="card p-8">
          <h1 className="mb-1 font-display text-xl font-medium">{title}</h1>
          <p className="mb-6 text-sm text-text-muted">{subtitle}</p>
          {children}
        </div>
        <p className="mt-6 text-center text-sm text-text-muted">{footer}</p>
      </div>
    </main>
  );
}
