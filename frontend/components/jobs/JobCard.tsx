import { SkillBadge } from "@/components/ui/SkillBadge";
import { ScoreRing } from "@/components/charts/ScoreRing";
import { MapPin, Tag } from "lucide-react";
import type { JobSummary } from "@/lib/api";

interface JobCardProps {
  job: JobSummary;
  matchScore?: number;
  candidateSkills?: string[];
  onSelect?: () => void;
}

export function JobCard({ job, matchScore, candidateSkills = [], onSelect }: JobCardProps) {
  const candLower = new Set(candidateSkills.map((s) => s.toLowerCase()));

  return (
    <button onClick={onSelect} className="card flex w-full flex-col gap-4 p-5 text-left transition-colors hover:border-spectrum-violet/40">
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="mb-1 flex items-center gap-2">
            <h3 className="font-display text-base font-medium text-text-primary">{job.title}</h3>
            {job.is_sample_data && (
              <span className="flex items-center gap-1 rounded-full border border-border bg-surface-raised px-2 py-0.5 text-[10px] uppercase tracking-wide text-text-faint">
                <Tag size={9} /> Sample data
              </span>
            )}
          </div>
          <p className="text-sm text-text-muted">{job.company}</p>
          {job.location && (
            <p className="mt-1 flex items-center gap-1 text-xs text-text-faint">
              <MapPin size={11} /> {job.location}
            </p>
          )}
        </div>
        {matchScore !== undefined && <ScoreRing score={matchScore} size={56} strokeWidth={5} />}
      </div>

      <div className="flex flex-wrap gap-1.5">
        {job.required_skills.map((skill) => (
          <SkillBadge key={skill} label={skill} state={candLower.has(skill.toLowerCase()) ? "matched" : "missing"} />
        ))}
      </div>
    </button>
  );
}
