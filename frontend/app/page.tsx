import Link from "next/link";
import { Navbar } from "@/components/layout/Navbar";
import { Button } from "@/components/ui/Button";
import { ScoreRing } from "@/components/charts/ScoreRing";
import {
  ScanLine, Layers, GitBranch, Sparkles, ShieldCheck, ArrowRight, Braces,
} from "lucide-react";

const FEATURES = [
  { icon: ScanLine, title: "Resume intelligence", desc: "Extraction of contact info, education, experience, projects and skills — grounded only in what's actually on the page." },
  { icon: Layers, title: "Semantic job matching", desc: "Transformer embeddings compare meaning, not just keywords, so a resume and a job description are read the way a person would read them." },
  { icon: GitBranch, title: "Skill-gap analysis", desc: "See exactly which skills separate you from a role, ranked by how much they typically matter for it." },
  { icon: Sparkles, title: "Explainable AI", desc: "Every score comes with the reasons behind it — a breakdown you can read and act on, not a black box." },
];

const PIPELINE = [
  "Resume PDF/DOCX", "Text extraction", "Skill extraction", "Transformer embeddings", "Hybrid match score",
];

export default function LandingPage() {
  return (
    <main>
      <Navbar />

      {/* Hero */}
      <section className="relative overflow-hidden px-6 pb-24 pt-20 md:pt-28">
        <div className="mx-auto max-w-5xl text-center">
          <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-border bg-surface px-4 py-1.5 text-xs text-text-muted">
            <span className="h-1.5 w-1.5 rounded-full bg-spectrum-cyan" />
            Built on transformer sentence embeddings
          </div>
          <h1 className="font-display text-4xl font-medium leading-[1.1] tracking-tight md:text-6xl">
            Turn your resume into
            <br />
            <span className="text-gradient">career intelligence.</span>
          </h1>
          <p className="mx-auto mt-6 max-w-xl text-balance text-text-muted md:text-lg">
            AI-powered resume analysis, semantic job matching, and personalized career insights —
            explained, not just scored.
          </p>
          <div className="mt-9 flex flex-wrap items-center justify-center gap-3">
            <Link href="/resume-analyzer"><Button size="lg">Analyze My Resume</Button></Link>
            <Link href="/resume-analyzer?demo=1"><Button size="lg" variant="secondary">Try Demo</Button></Link>
          </div>
        </div>

        {/* Signature element: the spectral scan — a resume decomposing into a skill spectrum */}
        <div className="relative mx-auto mt-20 max-w-4xl">
          <div className="card relative overflow-hidden p-8">
            <div className="mb-6 flex items-center justify-between">
              <div className="flex items-center gap-2 text-xs text-text-faint">
                <Braces size={13} /> resume.pdf → candidate_profile.json
              </div>
              <div className="flex items-center gap-3">
                {["Parsed", "Normalized", "Embedded"].map((s) => (
                  <span key={s} className="font-mono text-[10px] uppercase tracking-wider text-signal-good">✓ {s}</span>
                ))}
              </div>
            </div>

            <div className="relative h-2 w-full overflow-hidden rounded-full bg-surface-raised">
              <div className="absolute h-full w-full bg-spectrum-gradient opacity-90" />
              <div className="absolute inset-y-0 w-1/4 animate-scan bg-white/30 blur-sm" />
            </div>

            <div className="mt-6 flex flex-wrap gap-2">
              {["Python", "Machine Learning", "PyTorch", "SQL", "React", "Docker", "NLP"].map((s) => (
                <span key={s} className="rounded-full border border-border bg-surface-raised px-3 py-1 text-xs text-text-muted">
                  {s}
                </span>
              ))}
            </div>

            <div className="mt-8 grid grid-cols-3 gap-4 border-t border-border pt-6">
              <div className="flex flex-col items-center gap-2">
                <ScoreRing score={87} size={72} strokeWidth={6} />
                <span className="text-xs text-text-faint">Overall Match</span>
              </div>
              <div className="flex flex-col items-center gap-2">
                <ScoreRing score={92} size={72} strokeWidth={6} />
                <span className="text-xs text-text-faint">Semantic Fit</span>
              </div>
              <div className="flex flex-col items-center gap-2">
                <ScoreRing score={84} size={72} strokeWidth={6} />
                <span className="text-xs text-text-faint">ATS-style Score</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="mx-auto max-w-6xl px-6 py-20">
        <p className="mb-2 text-xs font-medium uppercase tracking-wider text-spectrum-violet">Features</p>
        <h2 className="mb-12 font-display text-3xl font-medium">What CareerLens actually does</h2>
        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          {FEATURES.map(({ icon: Icon, title, desc }) => (
            <div key={title} className="card p-6">
              <Icon size={20} className="mb-4 text-spectrum-cyan" />
              <h3 className="mb-2 font-display text-base font-medium">{title}</h3>
              <p className="text-sm leading-relaxed text-text-muted">{desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* How it works */}
      <section id="how-it-works" className="mx-auto max-w-6xl px-6 py-20">
        <p className="mb-2 text-xs font-medium uppercase tracking-wider text-spectrum-violet">How it works</p>
        <h2 className="mb-12 font-display text-3xl font-medium">The pipeline, end to end</h2>
        <div className="flex flex-wrap items-center gap-3">
          {PIPELINE.map((step, i) => (
            <div key={step} className="flex items-center gap-3">
              <div className="card px-4 py-3 text-sm text-text-primary">{step}</div>
              {i < PIPELINE.length - 1 && <ArrowRight size={16} className="text-text-faint" />}
            </div>
          ))}
        </div>
      </section>

      {/* AI technology */}
      <section id="technology" className="mx-auto max-w-6xl px-6 py-20">
        <div className="card p-10 md:p-14">
          <p className="mb-2 text-xs font-medium uppercase tracking-wider text-spectrum-violet">AI technology</p>
          <h2 className="mb-4 font-display text-3xl font-medium">Sentence-transformer embeddings, not keyword matching</h2>
          <p className="max-w-2xl text-text-muted">
            CareerLens encodes resumes and job descriptions with{" "}
            <code className="rounded bg-surface-raised px-1.5 py-0.5 font-mono text-sm text-spectrum-cyan">
              all-MiniLM-L6-v2
            </code>{" "}
            and blends that semantic signal with skill overlap, experience, education, and role
            compatibility into one hybrid, explainable score — never cosine similarity alone.
          </p>
        </div>
      </section>

      {/* Explainable AI */}
      <section className="mx-auto max-w-6xl px-6 py-20">
        <div className="grid gap-8 md:grid-cols-2 md:items-center">
          <div>
            <p className="mb-2 text-xs font-medium uppercase tracking-wider text-spectrum-violet">Explainable AI</p>
            <h2 className="mb-4 font-display text-3xl font-medium">Every score comes with its reasons</h2>
            <p className="text-text-muted">
              A match percentage on its own doesn&apos;t help you act. CareerLens always shows what
              drove a score up and what&apos;s pulling it down — in plain language.
            </p>
          </div>
          <div className="card p-6">
            <p className="mb-3 text-sm font-medium text-signal-good">+ Why you match</p>
            <ul className="mb-5 space-y-1.5 text-sm text-text-muted">
              <li>Strong Python and Machine Learning experience</li>
              <li>Relevant internship experience</li>
            </ul>
            <p className="mb-3 text-sm font-medium text-signal-bad">− Potential gaps</p>
            <ul className="space-y-1.5 text-sm text-text-muted">
              <li>AWS</li>
              <li>Production ML deployment</li>
            </ul>
          </div>
        </div>
      </section>

      {/* Demo CTA */}
      <section className="mx-auto max-w-6xl px-6 py-20">
        <div className="card flex flex-col items-center gap-5 p-14 text-center">
          <ShieldCheck size={22} className="text-spectrum-cyan" />
          <h2 className="font-display text-2xl font-medium">See it work on a sample resume</h2>
          <p className="max-w-md text-sm text-text-muted">
            The demo runs the real pipeline against a clearly labeled sample resume — no fabricated results.
          </p>
          <Link href="/resume-analyzer?demo=1"><Button size="lg">Try Demo</Button></Link>
        </div>
      </section>

      <footer className="border-t border-border px-6 py-10">
        <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-4 text-sm text-text-faint sm:flex-row">
          <span>© {new Date().getFullYear()} CareerLens AI — an experimental portfolio project.</span>
          <span>Built with Next.js, FastAPI &amp; Sentence Transformers</span>
        </div>
      </footer>
    </main>
  );
}
