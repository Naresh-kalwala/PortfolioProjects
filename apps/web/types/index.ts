export type JobSourcePlatform =
  | "greenhouse"
  | "lever"
  | "ashby"
  | "smartrecruiters"
  | "workday"
  | "microsoft_careers"
  | "google_careers"
  | "company_page"
  | "linkedin"
  | "indeed"
  | "dice"
  | "ziprecruiter"
  | "wellfound";

export type WorkplaceType = "remote" | "hybrid" | "onsite";
export type EmploymentType = "contract" | "full_time" | "part_time" | "internship";
export type ExperienceLevel = "entry" | "mid" | "senior";

export type ApplicationStatus =
  | "new"
  | "summarized"
  | "resume_generated"
  | "cover_letter_generated"
  | "ready_to_apply"
  | "auto_applying"
  | "manual_action_required"
  | "submitted"
  | "interview"
  | "offer"
  | "rejected"
  | "withdrawn";

export type ApplicationMethod = "auto" | "manual_assist";

export interface Job {
  id: string;
  source: JobSourcePlatform;
  title: string;
  company: string;
  company_logo_url: string | null;
  location: string | null;
  workplace_type: WorkplaceType | null;
  employment_type: EmploymentType | null;
  experience_level: ExperienceLevel | null;
  is_stem_opt_friendly: boolean | null;
  is_us_based: boolean;
  description: string;
  requirements: string[];
  preferred_qualifications: string[];
  salary_range: string | null;
  apply_url: string;
  supports_auto_apply: boolean;
  posted_at: string;
  discovered_at: string;
}

export interface UserJob {
  id: string;
  job: Job;
  match_score: number | null;
  match_breakdown: Record<string, number>;
  ai_summary: string | null;
  ai_match_explanation: string | null;
  missing_skills: string[];
  resume_improvement_suggestions: string[];
  status: ApplicationStatus;
  application_method: ApplicationMethod | null;
  manual_action_reason: string | null;
  manual_action_steps: string[];
  resume_application_url: string | null;
  is_saved: boolean;
  is_favorite: boolean;
  tailored_resume_id: string | null;
  cover_letter_id: string | null;
  applied_at: string | null;
  submitted_at: string | null;
  created_at: string;
}

export interface DashboardStats {
  jobs_found_today: number;
  jobs_last_24h: number;
  resumes_generated: number;
  cover_letters_generated: number;
  applied: number;
  manual_action_required: number;
  submitted: number;
  interviews: number;
  rejections: number;
  saved_jobs: number;
  favorites: number;
  average_match_score: number | null;
}

export interface NotificationItem {
  id: string;
  type: string;
  channel: string;
  title: string;
  body: string;
  related_job_id: string | null;
  sent_at: string | null;
  read_at: string | null;
  created_at: string;
}
