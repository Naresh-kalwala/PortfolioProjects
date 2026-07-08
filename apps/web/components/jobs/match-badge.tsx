import { cn } from "@/lib/utils";

export function MatchBadge({ score }: { score: number | null }) {
  if (score === null || score === undefined) {
    return <span className="text-xs text-muted-foreground">Analyzing…</span>;
  }

  const tone =
    score >= 80
      ? "text-success bg-success/10"
      : score >= 50
        ? "text-warning bg-warning/10"
        : "text-danger bg-danger/10";

  return (
    <span className={cn("inline-flex items-center rounded-full px-2.5 py-1 text-xs font-semibold", tone)}>
      {score}% match
    </span>
  );
}
