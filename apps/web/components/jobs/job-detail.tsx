"use client";

import { CheckCircle2, Download, ExternalLink, FileText, Mail, Trash2 } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { MatchBadge } from "@/components/jobs/match-badge";
import { StatusBadge } from "@/components/jobs/status-badge";
import { useApiGet, useApiMutations } from "@/hooks/use-api";
import { formatRelativeTime } from "@/lib/utils";
import type { UserJob } from "@/types";

export function JobDetail({ userJobId }: { userJobId: string }) {
  const { data: userJob, mutate } = useApiGet<UserJob>(`/jobs/${userJobId}`);
  const { get, post, remove } = useApiMutations();
  const [resuming, setResuming] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const router = useRouter();

  if (!userJob) {
    return <div className="h-96 animate-pulse rounded-lg border border-border bg-muted" />;
  }

  const { job } = userJob;
  const tailoredResumeId = userJob.tailored_resume_id;
  const coverLetterId = userJob.cover_letter_id;

  async function downloadDocument(kind: "resume" | "cover-letter") {
    const id = kind === "resume" ? tailoredResumeId : coverLetterId;
    if (!id) return;
    const path = kind === "resume" ? `/resumes/tailored/${id}/download` : `/cover-letters/${id}/download`;
    const { url } = await get<{ url: string }>(path);
    window.open(url, "_blank");
  }

  async function handleResumeApplication() {
    setResuming(true);
    try {
      await post(`/jobs/${userJobId}/resume-application`);
      mutate();
    } finally {
      setResuming(false);
    }
  }

  async function handleDelete() {
    if (!window.confirm("Remove this job from your dashboard? This can't be undone.")) return;
    setDeleting(true);
    try {
      await remove(`/jobs/${userJobId}`);
      router.push("/jobs");
    } finally {
      setDeleting(false);
    }
  }

  return (
    <div className="mx-auto max-w-4xl space-y-5">
      <div className="rounded-lg border border-border bg-card p-5 shadow-soft">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <h1 className="text-lg font-semibold">{job.title}</h1>
            <p className="text-sm text-muted-foreground">
              {job.company} · {job.location ?? "Location not specified"} · {formatRelativeTime(job.posted_at)}
            </p>
          </div>
          <div className="flex items-center gap-2">
            <MatchBadge score={userJob.match_score} />
            <StatusBadge status={userJob.status} />
            <button
              onClick={handleDelete}
              disabled={deleting}
              aria-label="Delete job"
              className="flex h-8 w-8 items-center justify-center rounded-md border border-border text-muted-foreground transition-colors hover:border-danger hover:bg-danger/10 hover:text-danger disabled:opacity-60"
            >
              <Trash2 size={14} />
            </button>
          </div>
        </div>

        {userJob.ai_summary && (
          <p className="mt-4 rounded-md bg-muted p-3 text-sm text-foreground">{userJob.ai_summary}</p>
        )}

        <a
          href={job.apply_url}
          target="_blank"
          rel="noreferrer"
          className="mt-4 inline-flex items-center gap-1.5 text-sm font-medium text-primary hover:underline"
        >
          View original posting <ExternalLink size={13} />
        </a>
      </div>

      {userJob.status === "manual_action_required" && (
        <div className="rounded-lg border border-warning/40 bg-warning/10 p-5">
          <h2 className="text-sm font-semibold text-warning">Manual Action Required</h2>
          <p className="mt-1 text-sm text-foreground/80">{userJob.manual_action_reason}</p>
          <ol className="mt-3 space-y-1.5 text-sm">
            {userJob.manual_action_steps.map((step, i) => (
              <li key={i} className="flex items-start gap-2">
                <span className="mt-0.5 flex h-4 w-4 shrink-0 items-center justify-center rounded-full bg-warning/20 text-[10px] font-semibold text-warning">
                  {i + 1}
                </span>
                {step}
              </li>
            ))}
          </ol>
          <div className="mt-4 flex items-center gap-2">
            <a
              href={userJob.resume_application_url ?? job.apply_url}
              target="_blank"
              rel="noreferrer"
              className="inline-flex h-9 items-center gap-1.5 rounded-md bg-primary px-3 text-sm font-medium text-primary-foreground"
            >
              Continue Application <ExternalLink size={13} />
            </a>
            <button
              onClick={handleResumeApplication}
              disabled={resuming}
              className="inline-flex h-9 items-center gap-1.5 rounded-md border border-border px-3 text-sm font-medium hover:bg-muted disabled:opacity-60"
            >
              <CheckCircle2 size={14} /> {resuming ? "Saving…" : "I finished it — mark Submitted"}
            </button>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <div className="rounded-lg border border-border bg-card p-5 shadow-soft">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold">Tailored Resume</h2>
            {userJob.tailored_resume_id && (
              <button
                onClick={() => downloadDocument("resume")}
                className="inline-flex items-center gap-1 text-xs font-medium text-primary hover:underline"
              >
                <Download size={12} /> Download PDF
              </button>
            )}
          </div>
          {userJob.tailored_resume_id ? (
            <p className="mt-2 text-xs text-muted-foreground">
              Generated for this posting — keywords and wording optimized without adding anything
              not in your master resume.
            </p>
          ) : (
            <p className="mt-2 flex items-center gap-1.5 text-xs text-muted-foreground">
              <FileText size={12} /> Not generated yet (upload a master resume in Profile first)
            </p>
          )}
        </div>

        <div className="rounded-lg border border-border bg-card p-5 shadow-soft">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold">Cover Letter</h2>
            {userJob.cover_letter_id && (
              <button
                onClick={() => downloadDocument("cover-letter")}
                className="inline-flex items-center gap-1 text-xs font-medium text-primary hover:underline"
              >
                <Download size={12} /> Download PDF
              </button>
            )}
          </div>
          {!userJob.cover_letter_id && (
            <p className="mt-2 flex items-center gap-1.5 text-xs text-muted-foreground">
              <Mail size={12} /> Not generated yet
            </p>
          )}
        </div>
      </div>

      {userJob.missing_skills.length > 0 && (
        <div className="rounded-lg border border-border bg-card p-5 shadow-soft">
          <h2 className="text-sm font-semibold">Skills this job wants that your resume doesn't show</h2>
          <div className="mt-2 flex flex-wrap gap-1.5">
            {userJob.missing_skills.map((skill) => (
              <span key={skill} className="rounded-full bg-muted px-2.5 py-1 text-xs">
                {skill}
              </span>
            ))}
          </div>
        </div>
      )}

      {userJob.resume_improvement_suggestions.length > 0 && (
        <div className="rounded-lg border border-border bg-card p-5 shadow-soft">
          <h2 className="text-sm font-semibold">Suggestions to improve your match</h2>
          <ul className="mt-2 list-disc space-y-1 pl-4 text-sm text-muted-foreground">
            {userJob.resume_improvement_suggestions.map((s, i) => (
              <li key={i}>{s}</li>
            ))}
          </ul>
        </div>
      )}

      <div className="rounded-lg border border-border bg-card p-5 shadow-soft">
        <h2 className="text-sm font-semibold">Full Job Description</h2>
        <p className="mt-2 whitespace-pre-wrap text-sm text-muted-foreground">{job.description}</p>
      </div>
    </div>
  );
}
