"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { DashboardCard } from "@/components/ui/DashboardCard";
import { ScoreRing } from "@/components/charts/ScoreRing";
import { Button } from "@/components/ui/Button";
import { EmptyState } from "@/components/ui/EmptyState";
import { JobCard } from "@/components/jobs/JobCard";
import { api, ApiError, type MatchResponse, type JobSummary } from "@/lib/api";
import { getActiveResumeId } from "@/lib/active-resume";
import { GitCompare } from "lucide-react";

export default function ComparePage() {
  return (
    <Suspense fallback={null}>
      <CompareContent />
    </Suspense>
  );
}

function CompareContent() {
  const searchParams = useSearchParams();
  const resumeId = searchParams.get("resume_id") ?? getActiveResumeId();
  const [jobId, setJobId] = useState<string | null>(searchParams.get("job_id"));

  const [jobs, setJobs] = useState<JobSummary[]>([]);
  const [result, setResult] = useState<MatchResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  // If no job is picked yet, show the catalog to pick from.
  useEffect(() => {
    if (!jobId) api.listJobs().then(setJobs).catch(() => {});
  }, [jobId]);

  useEffect(() => {
    if (!resumeId || !jobId) return;
    setLoading(true);
    setError(null);
    api
      .matchResumeToJob(resumeId, jobId)
      .then(setResult)
      .catch((e) => setError(e instanceof ApiError ? e.message : "Couldn't run this comparison."))
      .finally(() => setLoading(false));
  }, [resumeId, jobId]);

  if (!resumeId) {
    return (
      <EmptyState
        icon={GitCompare}
        title="No resume selected"
        description="Analyze a resume first (while signed in, so it's saved) before comparing it to a job."
        ctaLabel="Analyze My Resume"
        ctaHref="/resume-analyzer"
      />
    );
  }

  if (!jobId) {
    return (
      <div className="mx-auto max-w-5xl">
        <div className="mb-8">
          <h1 className="font-display text-2xl font-medium">Compare</h1>
          <p className="text-sm text-text-muted">Pick a job to compare against your analyzed resume.</p>
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          {jobs.map((job) => (
            <JobCard key={job.id} job={job} onSelect={() => setJobId(job.id)} />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="font-display text-2xl font-medium">Compare</h1>
          <p className="text-sm text-text-muted">Resume vs. job compatibility, fully broken down.</p>
        </div>
        <Button variant="secondary" onClick={() => setJobId(null)}>Choose a different job</Button>
      </div>

      {loading && <p className="text-sm text-text-faint">Comparing…</p>}
      {error && <p className="mb-4 text-sm text-signal-bad">{error}</p>}

      {result && (
        <div className="space-y-6">
          <DashboardCard>
            <div className="flex items-center justify-center py-4">
              <ScoreRing score={result.breakdown.overall_score} size={120} strokeWidth={10} label="Overall" />
            </div>
          </DashboardCard>

          <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
            {([
              ["Semantic", result.breakdown.semantic_similarity],
              ["Skills", result.breakdown.technical_skills],
              ["Experience", result.breakdown.experience],
              ["Education", result.breakdown.education],
              ["Role fit", result.breakdown.role_compatibility],
              ["Resume quality", result.breakdown.resume_quality],
            ] as const).map(([label, value]) => (
              <DashboardCard key={label}>
                <p className="font-mono text-xl">{value}</p>
                <p className="text-xs text-text-faint">{label}</p>
              </DashboardCard>
            ))}
          </div>

          <div className="grid gap-6 md:grid-cols-2">
            <DashboardCard title="Strengths">
              <ul className="space-y-2">
                {result.strengths.map((s, i) => <li key={i} className="text-sm text-signal-good">+ {s}</li>)}
              </ul>
            </DashboardCard>
            <DashboardCard title="Gaps">
              <ul className="space-y-2">
                {result.gaps.map((g, i) => <li key={i} className="text-sm text-signal-bad">− {g}</li>)}
              </ul>
            </DashboardCard>
          </div>
        </div>
      )}
    </div>
  );
}
