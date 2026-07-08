"use client";

import { Plus, X } from "lucide-react";
import { useState } from "react";
import { useSWRConfig } from "swr";

import { useApiMutations } from "@/hooks/use-api";

const MANUAL_SOURCES = [
  { value: "linkedin", label: "LinkedIn" },
  { value: "indeed", label: "Indeed" },
  { value: "dice", label: "Dice" },
  { value: "ziprecruiter", label: "ZipRecruiter" },
  { value: "wellfound", label: "Wellfound" },
];

export function AddManualJobDialog() {
  const [open, setOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const { post } = useApiMutations();
  const { mutate } = useSWRConfig();

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    setSubmitting(true);
    try {
      await post("/jobs/manual", {
        source: formData.get("source"),
        url: formData.get("url"),
        title: formData.get("title"),
        company: formData.get("company"),
        location: formData.get("location") || null,
        description: formData.get("description"),
      });
      mutate((key: string) => typeof key === "string" && key.startsWith("/jobs"));
      setOpen(false);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <>
      <button
        onClick={() => setOpen(true)}
        className="inline-flex h-9 items-center gap-1.5 rounded-md bg-primary px-3 text-sm font-medium text-primary-foreground shadow-soft transition-opacity hover:opacity-90"
      >
        <Plus size={14} /> Add Job
      </button>

      {open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4 animate-fade-in">
          <div className="w-full max-w-lg rounded-lg border border-border bg-card p-5 shadow-soft">
            <div className="mb-4 flex items-center justify-between">
              <div>
                <h2 className="text-sm font-semibold">Add a job you found yourself</h2>
                <p className="mt-1 text-xs text-muted-foreground">
                  LinkedIn, Indeed, Dice, ZipRecruiter, and Wellfound prohibit automated scraping
                  and auto-applying in their terms, so these are never scraped or auto-submitted.
                  Paste the posting here — you still get AI summary, match score, a tailored
                  resume, and a cover letter; you just finish the actual submit step yourself.
                </p>
              </div>
              <button onClick={() => setOpen(false)} className="text-muted-foreground hover:text-foreground">
                <X size={16} />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-3">
              <select name="source" required className="h-9 w-full rounded-md border border-border bg-background px-2.5 text-sm">
                {MANUAL_SOURCES.map((s) => (
                  <option key={s.value} value={s.value}>
                    {s.label}
                  </option>
                ))}
              </select>
              <input name="url" required placeholder="Job posting URL" className="h-9 w-full rounded-md border border-border bg-background px-2.5 text-sm" />
              <div className="grid grid-cols-2 gap-2">
                <input name="title" required placeholder="Job title" className="h-9 rounded-md border border-border bg-background px-2.5 text-sm" />
                <input name="company" required placeholder="Company" className="h-9 rounded-md border border-border bg-background px-2.5 text-sm" />
              </div>
              <input name="location" placeholder="Location (optional)" className="h-9 w-full rounded-md border border-border bg-background px-2.5 text-sm" />
              <textarea
                name="description"
                required
                rows={5}
                placeholder="Paste the full job description here"
                className="w-full rounded-md border border-border bg-background px-2.5 py-2 text-sm"
              />
              <button
                type="submit"
                disabled={submitting}
                className="h-9 w-full rounded-md bg-primary text-sm font-medium text-primary-foreground disabled:opacity-60"
              >
                {submitting ? "Adding…" : "Add & Analyze"}
              </button>
            </form>
          </div>
        </div>
      )}
    </>
  );
}
