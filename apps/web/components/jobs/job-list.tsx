"use client";

import { useSearchParams } from "next/navigation";

import { JobCard } from "@/components/jobs/job-card";
import { useApiGet } from "@/hooks/use-api";
import type { UserJob } from "@/types";

export function JobList() {
  const searchParams = useSearchParams();
  const query = searchParams.toString();

  const { data, isLoading } = useApiGet<UserJob[]>(`/jobs${query ? `?${query}` : ""}`);

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="h-40 animate-pulse rounded-lg border border-border bg-muted" />
        ))}
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center rounded-lg border border-dashed border-border py-16 text-center">
        <p className="text-sm font-medium">No jobs match these filters yet</p>
        <p className="mt-1 text-xs text-muted-foreground">
          New postings are scanned automatically every 30 minutes.
        </p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
      {data.map((userJob) => (
        <JobCard key={userJob.id} userJob={userJob} />
      ))}
    </div>
  );
}
