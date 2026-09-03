"use client";

import { Suspense, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { ResumeUploader } from "@/components/resume/ResumeUploader";
import { DashboardCard } from "@/components/ui/DashboardCard";
import { ScoreRing } from "@/components/charts/ScoreRing";
import { SkillBadge } from "@/components/ui/SkillBadge";
import { Button } from "@/components/ui/Button";
import { api, ApiError, type ResumeAnalysis } from "@/lib/api";
import { setActiveResumeId } from "@/lib/active-resume";
import { Sparkles } from "lucide-react";

// useSearchParams() requires a Suspense boundary in a static/prerendered
// route, or `next build` fails — see https://nextjs.org/docs/messages/missing-suspense-with-csr-bailout
export default function ResumeAnalyzerPage() {
  return (
    <Suspense fallback={null}>
      <ResumeAnalyzerContent />
    </Suspense>
  );
}

function ResumeAnalyzerContent() {
  const searchParams = useSearchParams();
  const isDemo = searchParams.get("demo") === "1";

  const [isProcessing, setIsProcessing] = useState(false);
  const [step, setStep] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [analysis, setAnalysis] = useState<ResumeAnalysis | null>(null);

  async function handleFile(file: File) {
    setError(null);
    setIsProcessing(true);
    setAnalysis(null);

    // Step the visual pipeline while the real request is in flight.
    // The backend does the actual work in one call; this just keeps the
    // "intelligent processing experience" (spec §35) tied to real progress
    // rather than a fixed fake timer once the request resolves.
    const interval = setInterval(() => setStep((s) => Math.min(s + 1, 5)), 500);

    try {
      const result = await api.uploadResume(file);
      setAnalysis(result);
      setStep(6);
      if (result.saved) setActiveResumeId(result.resume_id);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Something went wrong analyzing your resume. Please try again.");
    } finally {
      clearInterval(interval);
      setIsProcessing(false);
      setStep(0);
    }
  }

  async function handleUseDemoResume() {
    setError(null);
    setIsProcessing(true);
    try {
      // Real demo resume file at /public/demo-resume.docx, run through the
      // exact same upload pipeline as a real file — spec §34 explicitly
      // requires the demo to go through the real pipeline, not fake results.
      const res = await fetch("/demo-resume.docx");
      const blob = await res.blob();
      const file = new File([blob], "demo-resume.docx", {
        type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      });
      await handleFile(file);
    } catch {
      setError("Couldn't load the demo resume. Please try uploading your own.");
      setIsProcessing(false);
    }
  }

  return (
    <div className="mx-auto max-w-4xl">
      <div className="mb-8">
        <h1 className="font-display text-2xl font-medium">Resume Analyzer</h1>
        <p className="text-sm text-text-muted">Upload a PDF or DOCX resume to get AI-powered resume intelligence.</p>
      </div>

      {isDemo && !analysis && !isProcessing && (
        <div className="mb-6 flex items-center justify-between rounded-lg border border-spectrum-violet/30 bg-spectrum-violet/5 px-5 py-4">
          <div className="flex items-center gap-2 text-sm text-text-muted">
            <Sparkles size={16} className="text-spectrum-cyan" />
            Demo mode — run the real pipeline against a clearly labeled sample resume ("Demo Resume").
          </div>
          <Button size="sm" onClick={handleUseDemoResume}>Use Demo Resume</Button>
        </div>
      )}

      {!analysis && (
        <ResumeUploader onFileSelected={handleFile} isProcessing={isProcessing} currentStep={step} error={error} />
      )}

      {analysis && <AnalysisResults analysis={analysis} onReset={() => setAnalysis(null)} />}
    </div>
  );
}

function AnalysisResults({ analysis, onReset }: { analysis: ResumeAnalysis; onReset: () => void }) {
  return (
    <div className="space-y-6">
      {!analysis.saved && (
        <div className="flex items-center justify-between rounded-lg border border-spectrum-violet/30 bg-spectrum-violet/5 px-5 py-4">
          <p className="text-sm text-text-muted">
            This analysis is real, but isn&apos;t saved. Sign in to keep it on your dashboard and unlock job matching.
          </p>
          <Link href="/sign-up"><Button size="sm">Sign up free</Button></Link>
        </div>
      )}
      <div className="flex items-center justify-between">
        <div>
          <p className="font-display text-lg font-medium">{analysis.name ?? "Your resume"}</p>
          <p className="text-sm text-text-muted">{analysis.email}</p>
        </div>
        <div className="flex items-center gap-4">
          {analysis.saved && (
            <Link href="/career-insights" className="text-sm text-spectrum-cyan hover:underline">
              View career insights →
            </Link>
          )}
          <button onClick={onReset} className="text-sm text-text-muted hover:text-text-primary">
            Analyze another resume
          </button>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        <DashboardCard title="ATS-style Score" className="md:col-span-1">
          <ScoreRing score={analysis.ats_score} size={88} strokeWidth={7} />
          <p className="mt-3 text-xs text-text-faint">{analysis.ats_disclaimer}</p>
        </DashboardCard>

        <DashboardCard title="Score Breakdown" className="md:col-span-2">
          <div className="grid grid-cols-3 gap-4">
            {Object.entries(analysis.ats_breakdown).map(([key, value]) => (
              <div key={key}>
                <p className="font-mono text-lg">{value}</p>
                <p className="text-xs capitalize text-text-faint">{key.replace(/_/g, " ")}</p>
              </div>
            ))}
          </div>
        </DashboardCard>
      </div>

      <DashboardCard title={`Skills (${analysis.skills.length})`}>
        <div className="flex flex-wrap gap-2">
          {analysis.skills.map((s) => (
            <SkillBadge key={s.canonical} label={s.canonical} category={s.category} state="matched" />
          ))}
        </div>
      </DashboardCard>

      {analysis.improvement_suggestions.length > 0 && (
        <DashboardCard title="Resume improvement suggestions">
          <ul className="space-y-2">
            {analysis.improvement_suggestions.map((s, i) => (
              <li key={i} className="flex gap-2 text-sm text-text-muted">
                <span className="text-spectrum-cyan">→</span> {s}
              </li>
            ))}
          </ul>
        </DashboardCard>
      )}

      <div className="grid gap-6 md:grid-cols-2">
        <DashboardCard title="Experience">
          {analysis.experience.length === 0 && <p className="text-sm text-text-faint">None detected.</p>}
          <ul className="space-y-3">
            {analysis.experience.map((e, i) => (
              <li key={i} className="text-sm">
                <p className="font-medium text-text-primary">{e.position ?? "—"}</p>
                <p className="text-text-muted">{e.company} {e.duration && `· ${e.duration}`}</p>
              </li>
            ))}
          </ul>
        </DashboardCard>

        <DashboardCard title="Education">
          {analysis.education.length === 0 && <p className="text-sm text-text-faint">None detected.</p>}
          <ul className="space-y-3">
            {analysis.education.map((e, i) => (
              <li key={i} className="text-sm">
                <p className="font-medium text-text-primary">{e.institution ?? "—"}</p>
                <p className="text-text-muted">{e.degree} {e.graduation_year && `· ${e.graduation_year}`}</p>
              </li>
            ))}
          </ul>
        </DashboardCard>
      </div>
    </div>
  );
}
