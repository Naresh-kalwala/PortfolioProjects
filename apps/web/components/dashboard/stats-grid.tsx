"use client";

import {
  AlertTriangle,
  CalendarClock,
  CheckCircle2,
  FileText,
  Gauge,
  Heart,
  Mail,
  Send,
  Sparkles,
  Star,
  XCircle,
} from "lucide-react";

import { StatTile } from "@/components/dashboard/stat-tile";
import { useApiGet } from "@/hooks/use-api";
import type { DashboardStats } from "@/types";

export function StatsGrid() {
  const { data, isLoading } = useApiGet<DashboardStats>("/dashboard/stats");

  if (isLoading || !data) {
    return (
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6">
        {Array.from({ length: 12 }).map((_, i) => (
          <div key={i} className="h-24 animate-pulse rounded-lg border border-border bg-muted" />
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6">
      <StatTile label="Found Today" value={data.jobs_found_today} icon={Sparkles} />
      <StatTile label="Last 24h" value={data.jobs_last_24h} icon={CalendarClock} />
      <StatTile label="Resumes Generated" value={data.resumes_generated} icon={FileText} />
      <StatTile label="Cover Letters" value={data.cover_letters_generated} icon={Mail} />
      <StatTile label="Applied" value={data.applied} icon={Send} tone="success" />
      <StatTile
        label="Manual Action Needed"
        value={data.manual_action_required}
        icon={AlertTriangle}
        tone="warning"
      />
      <StatTile label="Submitted" value={data.submitted} icon={CheckCircle2} tone="success" />
      <StatTile label="Interviews" value={data.interviews} icon={CalendarClock} tone="success" />
      <StatTile label="Rejections" value={data.rejections} icon={XCircle} tone="danger" />
      <StatTile label="Saved" value={data.saved_jobs} icon={Heart} />
      <StatTile label="Favorites" value={data.favorites} icon={Star} />
      <StatTile
        label="Avg Match Score"
        value={data.average_match_score ? `${Math.round(data.average_match_score)}%` : "—"}
        icon={Gauge}
      />
    </div>
  );
}
