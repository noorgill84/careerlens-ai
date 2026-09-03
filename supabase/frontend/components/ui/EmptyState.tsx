import Link from "next/link";
import { Button } from "@/components/ui/Button";
import type { LucideIcon } from "lucide-react";

interface EmptyStateProps {
  icon: LucideIcon;
  title: string;
  description: string;
  ctaLabel?: string;
  ctaHref?: string;
}

export function EmptyState({ icon: Icon, title, description, ctaLabel, ctaHref }: EmptyStateProps) {
  return (
    <div className="card flex flex-col items-center gap-3 px-8 py-16 text-center">
      <Icon size={28} className="mb-1 text-text-faint" />
      <h3 className="font-display text-lg font-medium">{title}</h3>
      <p className="max-w-sm text-sm text-text-muted">{description}</p>
      {ctaLabel && ctaHref && (
        <Link href={ctaHref} className="mt-3">
          <Button>{ctaLabel}</Button>
        </Link>
      )}
    </div>
  );
}
