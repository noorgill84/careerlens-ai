import { DashboardCard } from "@/components/ui/DashboardCard";
import { ScoreRing } from "@/components/charts/ScoreRing";
import { SkillBadge } from "@/components/ui/SkillBadge";
import { EmptyState } from "@/components/ui/EmptyState";
import { FileSearch } from "lucide-react";

// This page renders against demo/placeholder data so the UI is reviewable
// without a live backend connected. Wire each section to `lib/api.ts`
// (careerInsights, listJobs, etc.) once auth + a real resume upload exist —
// the shape already matches the backend response types in lib/api.ts.
const DEMO = {
  resumeScore: 84,
  careerScore: 87,
  skillCount: 24,
  jobMatches: 18,
  topSkills: ["Python", "Machine Learning", "SQL", "React", "Docker", "PyTorch"],
  skillGaps: ["AWS", "Kubernetes"],
  recommendedRoles: [
    { role: "Machine Learning Engineer", compatibility: 91 },
    { role: "Data Scientist", compatibility: 87 },
    { role: "AI Engineer", compatibility: 84 },
  ],
  bestMatch: { title: "Machine Learning Engineer", company: "Demo: NovaAI Labs", score: 91 },
};

const hasResume = true; // placeholder for "does this user have an uploaded resume yet"

export default function DashboardPage() {
  if (!hasResume) {
    return (
      <EmptyState
        icon={FileSearch}
        title="No resume analyzed yet"
        description="Upload a resume to see your career intelligence dashboard."
        ctaLabel="Analyze My Resume"
        ctaHref="/resume-analyzer"
      />
    );
  }

  return (
    <div className="mx-auto max-w-6xl">
      <div className="mb-8">
        <h1 className="font-display text-2xl font-medium">Career Intelligence</h1>
        <p className="text-sm text-text-muted">Your AI-powered career overview</p>
      </div>

      {/* Summary cards */}
      <div className="mb-6 grid grid-cols-2 gap-4 lg:grid-cols-4">
        <DashboardCard eyebrow="Resume">
          <div className="flex items-center gap-4">
            <ScoreRing score={DEMO.resumeScore} size={56} strokeWidth={5} />
            <div>
              <p className="font-mono text-2xl">{DEMO.resumeScore}</p>
              <p className="text-xs text-text-faint">Resume Score</p>
            </div>
          </div>
        </DashboardCard>
        <DashboardCard eyebrow="Career">
          <div className="flex items-center gap-4">
            <ScoreRing score={DEMO.careerScore} size={56} strokeWidth={5} />
            <div>
              <p className="font-mono text-2xl">{DEMO.careerScore}</p>
              <p className="text-xs text-text-faint">Career Score</p>
            </div>
          </div>
        </DashboardCard>
        <DashboardCard eyebrow="Profile">
          <p className="font-mono text-3xl">{DEMO.skillCount}</p>
          <p className="text-xs text-text-faint">Skills identified</p>
        </DashboardCard>
        <DashboardCard eyebrow="Opportunities">
          <p className="font-mono text-3xl">{DEMO.jobMatches}</p>
          <p className="text-xs text-text-faint">Job matches</p>
        </DashboardCard>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <DashboardCard title="Top skills" className="lg:col-span-2">
          <div className="flex flex-wrap gap-2">
            {DEMO.topSkills.map((s) => <SkillBadge key={s} label={s} state="matched" />)}
          </div>
        </DashboardCard>

        <DashboardCard title="Skill gaps">
          <div className="flex flex-wrap gap-2">
            {DEMO.skillGaps.map((s) => <SkillBadge key={s} label={s} state="missing" />)}
          </div>
        </DashboardCard>

        <DashboardCard title="Recommended roles" className="lg:col-span-2">
          <ul className="space-y-3">
            {DEMO.recommendedRoles.map((r) => (
              <li key={r.role} className="flex items-center justify-between">
                <span className="text-sm text-text-primary">{r.role}</span>
                <span className="font-mono text-sm text-spectrum-cyan">{r.compatibility}%</span>
              </li>
            ))}
          </ul>
        </DashboardCard>

        <DashboardCard title="Best job match">
          <p className="mb-1 font-medium text-text-primary">{DEMO.bestMatch.title}</p>
          <p className="mb-4 text-sm text-text-muted">{DEMO.bestMatch.company}</p>
          <ScoreRing score={DEMO.bestMatch.score} size={64} strokeWidth={6} label="Match" />
        </DashboardCard>
      </div>
    </div>
  );
}
