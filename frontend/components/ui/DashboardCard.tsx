import { cn } from "@/lib/utils";

interface DashboardCardProps {
  children: React.ReactNode;
  className?: string;
  title?: string;
  eyebrow?: string;
  action?: React.ReactNode;
}

export function DashboardCard({ children, className, title, eyebrow, action }: DashboardCardProps) {
  return (
    <div className={cn("card p-6", className)}>
      {(title || eyebrow || action) && (
        <div className="mb-4 flex items-start justify-between">
          <div>
            {eyebrow && <p className="mb-1 text-xs font-medium uppercase tracking-wider text-spectrum-violet">{eyebrow}</p>}
            {title && <h3 className="font-display text-lg font-medium text-text-primary">{title}</h3>}
          </div>
          {action}
        </div>
      )}
      {children}
    </div>
  );
}
