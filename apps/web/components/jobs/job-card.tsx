"use client";

import { Heart, MapPin, Star } from "lucide-react";
import Link from "next/link";

import { MatchBadge } from "@/components/jobs/match-badge";
import { StatusBadge } from "@/components/jobs/status-badge";
import { useApiMutations } from "@/hooks/use-api";
import { cn, formatRelativeTime } from "@/lib/utils";
import type { UserJob } from "@/types";
import { useSWRConfig } from "swr";

const WORKPLACE_LABEL: Record<string, string> = {
  remote: "Remote",
  hybrid: "Hybrid",
  onsite: "Onsite",
};

export function JobCard({ userJob }: { userJob: UserJob }) {
  const { job } = userJob;
  const { patch } = useApiMutations();
  const { mutate } = useSWRConfig();

  async function toggle(field: "is_saved" | "is_favorite") {
    await patch(`/jobs/${userJob.id}`, { [field]: !userJob[field] });
    mutate((key: string) => typeof key === "string" && key.startsWith("/jobs"));
  }

  return (
    <div className="group rounded-lg border border-border bg-card p-4 shadow-soft transition-shadow hover:shadow-md">
      <div className="flex items-start justify-between gap-3">
        <Link href={`/jobs/${userJob.id}`} className="min-w-0 flex-1">
          <h3 className="truncate text-sm font-semibold group-hover:text-primary">{job.title}</h3>
          <p className="mt-0.5 truncate text-sm text-muted-foreground">{job.company}</p>
        </Link>
        <div className="flex shrink-0 items-center gap-1.5">
          <button
            onClick={() => toggle("is_favorite")}
            aria-label="Toggle favorite"
            className={cn(
              "flex h-7 w-7 items-center justify-center rounded-md border border-border transition-colors hover:bg-muted",
              userJob.is_favorite && "border-warning bg-warning/10 text-warning"
            )}
          >
            <Star size={13} fill={userJob.is_favorite ? "currentColor" : "none"} />
          </button>
          <button
            onClick={() => toggle("is_saved")}
            aria-label="Toggle saved"
            className={cn(
              "flex h-7 w-7 items-center justify-center rounded-md border border-border transition-colors hover:bg-muted",
              userJob.is_saved && "border-primary bg-accent text-primary"
            )}
          >
            <Heart size={13} fill={userJob.is_saved ? "currentColor" : "none"} />
          </button>
        </div>
      </div>

      <div className="mt-3 flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
        {job.location && (
          <span className="inline-flex items-center gap-1">
            <MapPin size={12} /> {job.location}
          </span>
        )}
        {job.workplace_type && <span>{WORKPLACE_LABEL[job.workplace_type]}</span>}
        <span>{formatRelativeTime(job.posted_at)}</span>
      </div>

      <div className="mt-3 flex flex-wrap items-center gap-2">
        <MatchBadge score={userJob.match_score} />
        <StatusBadge status={userJob.status} />
      </div>
    </div>
  );
}
