import { JobDetail } from "@/components/jobs/job-detail";

export default function JobDetailPage({ params }: { params: { id: string } }) {
  return <JobDetail userJobId={params.id} />;
}
