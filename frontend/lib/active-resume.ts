const KEY = "careerlens:active_resume_id";

export function setActiveResumeId(resumeId: string) {
  if (typeof window !== "undefined") localStorage.setItem(KEY, resumeId);
}

export function getActiveResumeId(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(KEY);
}

export function clearActiveResumeId() {
  if (typeof window !== "undefined") localStorage.removeItem(KEY);
}
