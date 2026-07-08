"use client";

import { UserButton } from "@clerk/nextjs";
import { Bell } from "lucide-react";

import { ThemeToggle } from "@/components/theme-toggle";

export function Topbar() {
  return (
    <header className="sticky top-0 z-10 flex h-16 items-center justify-end gap-3 border-b border-border bg-background/80 px-6 backdrop-blur">
      <button
        className="flex h-8 w-8 items-center justify-center rounded-md border border-border text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
        aria-label="Notifications"
      >
        <Bell size={16} />
      </button>
      <ThemeToggle />
      <UserButton afterSignOutUrl="/sign-in" />
    </header>
  );
}
