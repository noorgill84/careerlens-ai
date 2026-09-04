import { cn } from "@/lib/utils";
import { Check, X } from "lucide-react";

interface SkillBadgeProps {
  label: string;
  state?: "neutral" | "matched" | "missing";
  category?: string | null;
}

export function SkillBadge({ label, state = "neutral", category }: SkillBadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-sm",
        state === "matched" && "border-signal-good/30 bg-signal-good/10 text-signal-good",
        state === "missing" && "border-signal-bad/30 bg-signal-bad/10 text-signal-bad",
        state === "neutral" && "border-border bg-surface-raised text-text-muted"
      )}
      title={category ?? undefined}
    >
      {state === "matched" && <Check size={13} strokeWidth={2.5} />}
      {state === "missing" && <X size={13} strokeWidth={2.5} />}
      {label}
    </span>
  );
}
