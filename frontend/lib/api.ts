import { getAccessToken } from "@/lib/supabase";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = await getAccessToken();
  const headers: Record<string, string> = {
    ...(options.body instanceof FormData ? {} : { "Content-Type": "application/json" }),
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(options.headers as Record<string, string> | undefined),
  };

  const res = await fetch(`${API_URL}${path}`, { ...options, headers });

  if (!res.ok) {
    let message = `Request failed with status ${res.status}`;
    try {
      const body = await res.json();
      message = body.message || body.detail || message;
    } catch {
      /* response wasn't JSON — keep default message */
    }
    throw new ApiError(message, res.status);
  }

  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

// ---------- Types mirroring backend/app/schemas ----------
export interface SkillOut {
  canonical: string;
  category: string | null;
  matched: boolean;
}

export interface ResumeAnalysis {
  resume_id: string;
  name: string | null;
  email: string | null;
  phone: string | null;
  linkedin: string | null;
  github: string | null;
  portfolio: string | null;
  summary: string | null;
  education: { institution: string | null; degree: string | null; graduation_year: string | null; gpa: string | null }[];
  experience: { company: string | null; position: string | null; duration: string | null }[];
  projects: { name: string | null; raw_text: string }[];
  skills: SkillOut[];
  certifications: string[];
  achievements: string[];
  ats_score: number;
  ats_breakdown: Record<string, number>;
  ats_disclaimer: string;
  improvement_suggestions: string[];
  saved: boolean;
}

export interface JobSummary {
  id: string;
  title: string;
  company: string;
  location: string | null;
  is_sample_data: boolean;
  required_skills: string[];
}

export interface MatchBreakdown {
  overall_score: number;
  semantic_similarity: number;
  technical_skills: number;
  experience: number;
  education: number;
  role_compatibility: number;
  resume_quality: number;
  matched_skills: string[];
  missing_skills: string[];
}

export interface MatchResponse {
  breakdown: MatchBreakdown;
  strengths: string[];
  gaps: string[];
}

export interface RoleRecommendation {
  role: string;
  compatibility: number;
  matched_skills: string[];
  missing_skills: string[];
  reason: string;
}

// ---------- API surface ----------
export const api = {
  uploadResume: (file: File) => {
    const form = new FormData();
    form.append("file", file);
    return request<ResumeAnalysis>("/api/resume/upload", { method: "POST", body: form });
  },
  deleteResume: (resumeId: string) => request<void>(`/api/resume/${resumeId}`, { method: "DELETE" }),
  deleteAllData: () => request<{ deleted_count: number }>("/api/resume/", { method: "DELETE" }),
  listJobs: (query?: string) => request<JobSummary[]>(`/api/jobs${query ? `?q=${encodeURIComponent(query)}` : ""}`),
  getJob: (jobId: string) => request<JobSummary>(`/api/jobs/${jobId}`),
  analyzeJob: (title: string, description: string) =>
    request("/api/jobs/analyze", { method: "POST", body: JSON.stringify({ title, description }) }),
  matchResumeToJob: (resumeId: string, jobId?: string, jobDescription?: string) =>
    request<MatchResponse>("/api/match", {
      method: "POST",
      body: JSON.stringify({ resume_id: resumeId, job_id: jobId, job_description: jobDescription }),
    }),
};
