import { ProfileForm } from "@/components/profile/profile-form";
import { ResumeUpload } from "@/components/profile/resume-upload";

export default function ProfilePage() {
  return (
    <div className="mx-auto max-w-4xl space-y-5">
      <div>
        <h2 className="text-xl font-semibold tracking-tight">Profile & Settings</h2>
        <p className="text-sm text-muted-foreground">
          Used to tailor every resume, cover letter, and application question.
        </p>
      </div>

      <ResumeUpload />
      <ProfileForm />
    </div>
  );
}
