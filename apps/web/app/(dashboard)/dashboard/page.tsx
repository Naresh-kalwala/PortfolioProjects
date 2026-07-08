import { Suspense } from "react";

import { StatsGrid } from "@/components/dashboard/stats-grid";
import { AddManualJobDialog } from "@/components/jobs/add-manual-job-dialog";
import { JobList } from "@/components/jobs/job-list";

export default function DashboardPage() {
  return (
    <div className="mx-auto max-w-7xl space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold tracking-tight">Overview</h2>
          <p className="text-sm text-muted-foreground">
            Your AI job assistant's activity across every connected source.
          </p>
        </div>
        <AddManualJobDialog />
      </div>

      <StatsGrid />

      <div>
        <h3 className="mb-3 text-sm font-semibold text-muted-foreground">Recent matches</h3>
        <Suspense>
          <JobList />
        </Suspense>
      </div>
    </div>
  );
}
