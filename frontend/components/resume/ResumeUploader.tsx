"use client";

import { useCallback, useState } from "react";
import { UploadCloud, FileText, Loader2, CheckCircle2 } from "lucide-react";
import { cn } from "@/lib/utils";

const PIPELINE_STEPS = [
  "Uploading resume",
  "Extracting resume text",
  "Understanding experience",
  "Identifying skills",
  "Generating semantic profile",
  "Analyzing career opportunities",
  "Generating insights",
];

interface ResumeUploaderProps {
  onFileSelected: (file: File) => void;
  isProcessing: boolean;
  currentStep?: number; // index into PIPELINE_STEPS
  error?: string | null;
}

export function ResumeUploader({ onFileSelected, isProcessing, currentStep = 0, error }: ResumeUploaderProps) {
  const [dragActive, setDragActive] = useState(false);
  const [fileName, setFileName] = useState<string | null>(null);

  const handleFile = useCallback(
    (file: File | undefined) => {
      if (!file) return;
      const isValidType = file.name.endsWith(".pdf") || file.name.endsWith(".docx");
      if (!isValidType) return;
      setFileName(file.name);
      onFileSelected(file);
    },
    [onFileSelected]
  );

  if (isProcessing) {
    return (
      <div className="card p-8">
        <div className="mb-6 flex items-center gap-3">
          <FileText size={20} className="text-spectrum-violet" />
          <span className="font-mono text-sm text-text-muted">{fileName ?? "resume.pdf"}</span>
        </div>
        <ul className="space-y-3">
          {PIPELINE_STEPS.map((step, i) => (
            <li key={step} className="flex items-center gap-3 text-sm">
              {i < currentStep ? (
                <CheckCircle2 size={16} className="text-signal-good" />
              ) : i === currentStep ? (
                <Loader2 size={16} className="animate-spin text-spectrum-cyan" />
              ) : (
                <span className="h-4 w-4 rounded-full border border-border" />
              )}
              <span className={i <= currentStep ? "text-text-primary" : "text-text-faint"}>{step}...</span>
            </li>
          ))}
        </ul>
      </div>
    );
  }

  return (
    <div>
      <label
        onDragOver={(e) => { e.preventDefault(); setDragActive(true); }}
        onDragLeave={() => setDragActive(false)}
        onDrop={(e) => { e.preventDefault(); setDragActive(false); handleFile(e.dataTransfer.files?.[0]); }}
        className={cn(
          "flex cursor-pointer flex-col items-center justify-center rounded-xl2 border-2 border-dashed p-14 text-center transition-colors",
          dragActive ? "border-spectrum-violet bg-spectrum-violet/5" : "border-border hover:border-spectrum-violet/40"
        )}
      >
        <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-surface-raised">
          <UploadCloud size={24} className="text-spectrum-cyan" />
        </div>
        <p className="mb-1 font-medium text-text-primary">Drop your resume here, or click to browse</p>
        <p className="text-sm text-text-muted">PDF or DOCX, up to 5MB</p>
        <input
          type="file"
          accept=".pdf,.docx"
          className="hidden"
          onChange={(e) => handleFile(e.target.files?.[0])}
        />
      </label>
      {error && <p className="mt-3 text-sm text-signal-bad">{error}</p>}
    </div>
  );
}
