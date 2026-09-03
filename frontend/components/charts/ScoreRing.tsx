"use client";

import { cn } from "@/lib/utils";

interface ScoreRingProps {
  score: number; // 0-100
  size?: number;
  strokeWidth?: number;
  label?: string;
  className?: string;
}

/**
 * The signature element: a spectral score ring. The arc is drawn with the
 * blue -> violet -> cyan gradient used throughout the product, so every
 * score in the app (resume, ATS, match %) reads as "light passed through
 * the same instrument" rather than a generic progress ring.
 */
export function ScoreRing({ score, size = 96, strokeWidth = 8, label, className }: ScoreRingProps) {
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const clamped = Math.max(0, Math.min(100, score));
  const offset = circumference - (clamped / 100) * circumference;
  const gradientId = `score-gradient-${size}-${label ?? "x"}`;

  return (
    <div className={cn("relative inline-flex items-center justify-center", className)} style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        <defs>
          <linearGradient id={gradientId} x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#3B82F6" />
            <stop offset="55%" stopColor="#8B5CF6" />
            <stop offset="100%" stopColor="#22D3EE" />
          </linearGradient>
        </defs>
        <circle cx={size / 2} cy={size / 2} r={radius} stroke="#232B3D" strokeWidth={strokeWidth} fill="none" />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={`url(#${gradientId})`}
          strokeWidth={strokeWidth}
          fill="none"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          style={{ transition: "stroke-dashoffset 0.8s ease-out" }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="font-mono text-xl font-medium text-text-primary">{Math.round(clamped)}</span>
        {label && <span className="text-[10px] uppercase tracking-wide text-text-faint">{label}</span>}
      </div>
    </div>
  );
}
