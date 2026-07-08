import { cn } from "@/lib/utils";
import type { ApplicationStatus } from "@/types";

const STATUS_LABELS: Record<ApplicationStatus, string> = {
  new: "New",
  summarized: "Analyzed",
  resume_generated: "Resume Ready",
  cover_letter_generated: "Ready to Apply",
  ready_to_apply: "Ready to Apply",
  auto_applying: "Applying…",
  manual_action_required: "Manual Action Required",
  submitted: "Submitted",
  interview: "Interview",
  offer: "Offer",
  rejected: "Rejected",
  withdrawn: "Withdrawn",
};

const STATUS_TONES: Record<ApplicationStatus, string> = {
  new: "bg-muted text-muted-foreground",
  summarized: "bg-muted text-muted-foreground",
  resume_generated: "bg-accent text-accent-foreground",
  cover_letter_generated: "bg-accent text-accent-foreground",
  ready_to_apply: "bg-accent text-accent-foreground",
  auto_applying: "bg-warning/15 text-warning",
  manual_action_required: "bg-warning/15 text-warning",
  submitted: "bg-success/15 text-success",
  interview: "bg-success/15 text-success",
  offer: "bg-success/15 text-success",
  rejected: "bg-danger/15 text-danger",
  withdrawn: "bg-muted text-muted-foreground",
};

export function StatusBadge({ status }: { status: ApplicationStatus }) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2.5 py-1 text-xs font-medium",
        STATUS_TONES[status]
      )}
    >
      {STATUS_LABELS[status]}
    </span>
  );
}
