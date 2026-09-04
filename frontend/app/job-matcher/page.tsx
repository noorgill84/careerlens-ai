"use client";

import { useEffect, useState } from "react";
import { JobCard } from "@/components/jobs/JobCard";
import { EmptyState } from "@/components/ui/EmptyState";
import { api, type JobSummary } from "@/lib/api";
import { Briefcase, Search } from "lucide-react";
import { useRouter } from "next/navigation";

export default function JobMatcherPage() {
  const router = useRouter();
  const [jobs, setJobs] = useState<JobSummary[]>([]);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState(false);

  // Debounced search against the real backend endpoint — the ranking
  // (semantic when the embedding model is available, skill/keyword-based
  // otherwise) happens server-side in app/services/job_service.py, not as
  // a client-side substring filter.
  useEffect(() => {
    setLoading(true);
    setLoadError(false);
    const timeout = setTimeout(() => {
      api
        .listJobs(query || undefined)
        .then(setJobs)
        .catch(() => setLoadError(true))
        .finally(() => setLoading(false));
    }, 300);
    return () => clearTimeout(timeout);
  }, [query]);

  function handleSelectJob(job: JobSummary) {
    router.push(`/compare?job_id=${job.id}`);
  }

  return (
    <div className="mx-auto max-w-5xl">
      <div className="mb-8">
        <h1 className="font-display text-2xl font-medium">Job Matcher</h1>
        <p className="text-sm text-text-muted">
          Search sample job postings, clearly labeled as demo data. Selecting a job takes you to Compare.
        </p>
      </div>

      <div className="mb-6 flex items-center gap-2 rounded-lg border border-border bg-surface px-4 py-2.5">
        <Search size={16} className="text-text-faint" />
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder='Try "AI jobs involving Python and NLP"'
          className="w-full bg-transparent text-sm text-text-primary placeholder:text-text-faint focus:outline-none"
        />
      </div>

      {loading && <p className="text-sm text-text-faint">Searching…</p>}

      {loadError && (
        <EmptyState
          icon={Briefcase}
          title="Couldn't reach the backend"
          description="Start the FastAPI server (see backend/README.md) and set NEXT_PUBLIC_API_URL to load real job data."
        />
      )}

      {!loading && !loadError && jobs.length === 0 && (
        <EmptyState icon={Briefcase} title="No jobs match" description="Try a different search term." />
      )}

      <div className="grid gap-4 sm:grid-cols-2">
        {jobs.map((job) => (
          <JobCard key={job.id} job={job} onSelect={() => handleSelectJob(job)} />
        ))}
      </div>
    </div>
  );
}
