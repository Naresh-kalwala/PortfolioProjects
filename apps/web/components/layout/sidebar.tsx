"use client";

import {
  Briefcase,
  LayoutDashboard,
  Settings,
  Sparkles,
  Star,
} from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

import { cn } from "@/lib/utils";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/jobs", label: "Jobs", icon: Briefcase },
  { href: "/jobs?is_favorite=true", label: "Favorites", icon: Star },
  { href: "/profile", label: "Profile & Settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="hidden w-64 shrink-0 flex-col border-r border-border bg-card px-4 py-6 md:flex">
      <div className="mb-8 flex items-center gap-2 px-2">
        <div className="flex h-8 w-8 items-center justify-center rounded-md bg-primary text-primary-foreground">
          <Sparkles size={16} />
        </div>
        <span className="text-base font-semibold tracking-tight">JobPilot</span>
      </div>

      <nav className="flex flex-1 flex-col gap-1">
        {NAV_ITEMS.map(({ href, label, icon: Icon }) => {
          const active = pathname === href.split("?")[0];
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                active
                  ? "bg-accent text-accent-foreground"
                  : "text-muted-foreground hover:bg-muted hover:text-foreground"
              )}
            >
              <Icon size={16} />
              {label}
            </Link>
          );
        })}
      </nav>

      <div className="rounded-lg border border-border bg-muted/50 p-3 text-xs text-muted-foreground">
        Scans LinkedIn/Indeed/Dice/ZipRecruiter/Wellfound postings you add manually, plus
        automatic search on Greenhouse, Lever, Ashby, SmartRecruiters, Workday, and Microsoft/Google
        careers — every 30 minutes.
      </div>
    </aside>
  );
}
