"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { DashboardCard } from "@/components/ui/DashboardCard";
import { SkillBadge } from "@/components/ui/SkillBadge";
import { EmptyState } from "@/components/ui/EmptyState";
import { api, type RoleRecommendation } from "@/lib/api";
import { getActiveResumeId } from "@/lib/active-resume";
import { Compass } from "lucide-react";

export default function CareerInsightsPage() {
  return (
    <Suspense fallback={null}>
      <CareerInsightsContent />
    </Suspense>
  );
}

function CareerInsightsContent() {
  const searchParams = useSearchParams();
  const resumeId = searchParams.get("resume_id") ?? getActiveResumeId();

  const [roles, setRoles] = useState<RoleRecommendation[] | null>(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    if (!resumeId) return;
    api
      .careerInsights(resumeId)
      .then((res) => setRoles(res.recommended_roles))
      .catch(() => setError(true));
  }, [resumeId]);

  if (!resumeId) {
    return (
      <EmptyState
        icon={Compass}
        title="No resume selected"
        description="Analyze a resume first (while signed in, so it's saved) to see personalized career recommendations."
        ctaLabel="Analyze My Resume"
        ctaHref="/resume-analyzer"
      />
    );
  }

  return (
    <div className="mx-auto max-w-4xl">
      <div className="mb-8">
        <h1 className="font-display text-2xl font-medium">Career Insights</h1>
        <p className="text-sm text-text-muted">Roles ranked by compatibility with your extracted skill profile.</p>
      </div>

      {error && <p className="text-sm text-signal-bad">Couldn&apos;t load recommendations. Is the backend running?</p>}

      <div className="space-y-4">
        {roles?.map((r) => (
          <DashboardCard key={r.role}>
            <div className="mb-3 flex items-center justify-between">
              <h3 className="font-display text-base font-medium">{r.role}</h3>
              <span className="font-mono text-lg text-spectrum-cyan">{r.compatibility}%</span>
            </div>
            <p className="mb-3 text-sm text-text-muted">{r.reason}</p>
            <div className="flex flex-wrap gap-2">
              {r.matched_skills.map((s) => <SkillBadge key={s} label={s} state="matched" />)}
              {r.missing_skills.map((s) => <SkillBadge key={s} label={s} state="missing" />)}
            </div>
          </DashboardCard>
        ))}
      </div>
    </div>
  );
}
