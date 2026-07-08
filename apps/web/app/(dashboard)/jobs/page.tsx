import { Suspense } from "react";

import { AddManualJobDialog } from "@/components/jobs/add-manual-job-dialog";
import { JobFilters } from "@/components/jobs/job-filters";
import { JobList } from "@/components/jobs/job-list";

export default function JobsPage() {
  return (
    <div className="mx-auto max-w-7xl space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold tracking-tight">Jobs</h2>
          <p className="text-sm text-muted-foreground">
            Power BI, Power Platform, Microsoft Fabric, and BI/analytics roles posted in the last
            24 hours.
          </p>
        </div>
        <AddManualJobDialog />
      </div>

      <Suspense>
        <JobFilters />
      </Suspense>

      <Suspense>
        <JobList />
      </Suspense>
    </div>
  );
}
