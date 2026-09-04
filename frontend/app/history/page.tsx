"use client";

import { useEffect, useState } from "react";
import { EmptyState } from "@/components/ui/EmptyState";
import { DashboardCard } from "@/components/ui/DashboardCard";
import { api } from "@/lib/api";
import { History as HistoryIcon } from "lucide-react";

interface HistoryEvent {
  id: string;
  event_type: string;
  summary: string;
  created_at: string;
}

export default function HistoryPage() {
  const [events, setEvents] = useState<HistoryEvent[]>([]);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    api
      .history()
      .then((res) => setEvents((res.history as HistoryEvent[]) ?? []))
      .finally(() => setLoaded(true));
  }, []);

  return (
    <div className="mx-auto max-w-3xl">
      <div className="mb-8">
        <h1 className="font-display text-2xl font-medium">Analysis History</h1>
        <p className="text-sm text-text-muted">Every resume analysis and job match you&apos;ve run.</p>
      </div>

      {loaded && events.length === 0 && (
        <EmptyState
          icon={HistoryIcon}
          title="No analyses yet"
          description="Your resume analyses and job matches will show up here."
          ctaLabel="Analyze My Resume"
          ctaHref="/resume-analyzer"
        />
      )}

      <div className="space-y-3">
        {events.map((e) => (
          <DashboardCard key={e.id}>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium capitalize text-text-primary">{e.event_type.replace(/_/g, " ")}</p>
                <p className="text-sm text-text-muted">{e.summary}</p>
              </div>
              <span className="text-xs text-text-faint">{new Date(e.created_at).toLocaleDateString()}</span>
            </div>
          </DashboardCard>
        ))}
      </div>
    </div>
  );
}
