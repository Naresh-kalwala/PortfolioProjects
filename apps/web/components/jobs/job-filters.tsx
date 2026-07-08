"use client";

import { Search } from "lucide-react";
import { useRouter, useSearchParams } from "next/navigation";
import { useState } from "react";

const SELECT_CLASS =
  "h-9 rounded-md border border-border bg-card px-2.5 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary/40";

export function JobFilters() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [search, setSearch] = useState(searchParams.get("search") ?? "");

  function updateParam(key: string, value: string) {
    const params = new URLSearchParams(searchParams.toString());
    if (value) params.set(key, value);
    else params.delete(key);
    router.push(`/jobs?${params.toString()}`);
  }

  return (
    <div className="flex flex-wrap items-center gap-2">
      <form
        onSubmit={(e) => {
          e.preventDefault();
          updateParam("search", search);
        }}
        className="relative"
      >
        <Search size={14} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-muted-foreground" />
        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search title or company…"
          className="h-9 w-56 rounded-md border border-border bg-card pl-8 pr-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary/40"
        />
      </form>

      <select
        className={SELECT_CLASS}
        defaultValue={searchParams.get("workplace_type") ?? ""}
        onChange={(e) => updateParam("workplace_type", e.target.value)}
      >
        <option value="">Any workplace</option>
        <option value="remote">Remote</option>
        <option value="hybrid">Hybrid</option>
        <option value="onsite">Onsite</option>
      </select>

      <select
        className={SELECT_CLASS}
        defaultValue={searchParams.get("employment_type") ?? ""}
        onChange={(e) => updateParam("employment_type", e.target.value)}
      >
        <option value="">Any employment type</option>
        <option value="full_time">Full-time</option>
        <option value="contract">Contract</option>
        <option value="part_time">Part-time</option>
        <option value="internship">Internship</option>
      </select>

      <select
        className={SELECT_CLASS}
        defaultValue={searchParams.get("experience_level") ?? ""}
        onChange={(e) => updateParam("experience_level", e.target.value)}
      >
        <option value="">Any level</option>
        <option value="entry">Entry Level</option>
        <option value="mid">Mid Level</option>
        <option value="senior">Senior</option>
      </select>

      <select
        className={SELECT_CLASS}
        defaultValue={searchParams.get("status") ?? ""}
        onChange={(e) => updateParam("status", e.target.value)}
      >
        <option value="">Any status</option>
        <option value="manual_action_required">Manual Action Required</option>
        <option value="submitted">Submitted</option>
        <option value="interview">Interview</option>
        <option value="rejected">Rejected</option>
      </select>

      <select
        className={SELECT_CLASS}
        defaultValue={searchParams.get("sort_by") ?? "posted_at"}
        onChange={(e) => updateParam("sort_by", e.target.value)}
      >
        <option value="posted_at">Newest posted</option>
        <option value="match_score">Best match</option>
        <option value="created_at">Recently found</option>
      </select>
    </div>
  );
}
