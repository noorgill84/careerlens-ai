"use client";

import { useState } from "react";
import { DashboardCard } from "@/components/ui/DashboardCard";
import { Button } from "@/components/ui/Button";
import { SkillBadge } from "@/components/ui/SkillBadge";
import { api, ApiError } from "@/lib/api";

interface JobAnalysisResult {
  title: string;
  required_skills: string[];
  preferred_skills: string[];
  experience_years_required: number | null;
  education_required: string | null;
  keywords: string[];
}

export default function JobAnalyzerPage() {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [result, setResult] = useState<JobAnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleAnalyze() {
    setError(null);
    setLoading(true);
    try {
      const res = (await api.analyzeJob(title, description)) as JobAnalysisResult;
      setResult(res);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Couldn't analyze this job description.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-4xl">
      <div className="mb-8">
        <h1 className="font-display text-2xl font-medium">Job Description Analyzer</h1>
        <p className="text-sm text-text-muted">Paste a job description to extract structured requirements.</p>
      </div>

      <div className="space-y-4">
        <input
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Job title (e.g. Machine Learning Engineer)"
          className="w-full rounded-lg border border-border bg-surface px-4 py-2.5 text-sm text-text-primary placeholder:text-text-faint focus:outline-none"
        />
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Paste the full job description here..."
          rows={10}
          className="w-full rounded-lg border border-border bg-surface px-4 py-3 text-sm text-text-primary placeholder:text-text-faint focus:outline-none"
        />
        <Button onClick={handleAnalyze} disabled={loading || description.length < 20}>
          {loading ? "Analyzing…" : "Analyze Job Description"}
        </Button>
        {error && <p className="text-sm text-signal-bad">{error}</p>}
      </div>

      {result && (
        <div className="mt-8 space-y-6">
          <DashboardCard title="Required skills">
            <div className="flex flex-wrap gap-2">
              {result.required_skills.length === 0 && <p className="text-sm text-text-faint">None detected.</p>}
              {result.required_skills.map((s) => <SkillBadge key={s} label={s} state="neutral" />)}
            </div>
          </DashboardCard>

          {result.preferred_skills.length > 0 && (
            <DashboardCard title="Preferred skills">
              <div className="flex flex-wrap gap-2">
                {result.preferred_skills.map((s) => <SkillBadge key={s} label={s} state="neutral" />)}
              </div>
            </DashboardCard>
          )}

          <div className="grid grid-cols-2 gap-4">
            <DashboardCard title="Experience required">
              <p className="font-mono text-2xl">{result.experience_years_required ?? "—"}{result.experience_years_required !== null && " yrs"}</p>
            </DashboardCard>
            <DashboardCard title="Education required">
              <p className="font-mono text-lg capitalize">{result.education_required ?? "Not specified"}</p>
            </DashboardCard>
          </div>
        </div>
      )}
    </div>
  );
}
