import type { LucideIcon } from "lucide-react";

import { cn } from "@/lib/utils";

interface StatTileProps {
  label: string;
  value: string | number;
  icon: LucideIcon;
  tone?: "default" | "success" | "warning" | "danger";
}

const TONE_CLASSES: Record<NonNullable<StatTileProps["tone"]>, string> = {
  default: "text-primary bg-accent",
  success: "text-success bg-success/10",
  warning: "text-warning bg-warning/10",
  danger: "text-danger bg-danger/10",
};

export function StatTile({ label, value, icon: Icon, tone = "default" }: StatTileProps) {
  return (
    <div className="animate-slide-up rounded-lg border border-border bg-card p-4 shadow-soft">
      <div className="flex items-center justify-between">
        <span className="text-sm text-muted-foreground">{label}</span>
        <div className={cn("flex h-7 w-7 items-center justify-center rounded-md", TONE_CLASSES[tone])}>
          <Icon size={14} />
        </div>
      </div>
      <div className="mt-2 text-2xl font-semibold tracking-tight">{value}</div>
    </div>
  );
}
