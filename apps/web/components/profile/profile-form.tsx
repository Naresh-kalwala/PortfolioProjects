"use client";

import { Plus, Trash2 } from "lucide-react";
import { useEffect, useState } from "react";

import { useApiGet, useApiMutations } from "@/hooks/use-api";

interface WorkHistoryEntry {
  company: string;
  title: string;
  start_date: string;
  end_date: string | null;
  is_current: boolean;
  description: string;
  achievements: string[];
}

interface UserProfileData {
  full_name: string | null;
  phone: string | null;
  linkedin_url: string | null;
  portfolio_url: string | null;
  github_url: string | null;
  work_history: WorkHistoryEntry[];
  skills: string[];
  certifications: string[];
  preferred_locations: string[];
  salary_expectation_min: number | null;
  salary_expectation_max: number | null;
  salary_currency: string;
  work_authorization: string | null;
  visa_status: string | null;
  requires_stem_opt: boolean;
  auto_submit_applications: boolean;
  whatsapp_number: string | null;
  notification_preferences: { email: boolean; whatsapp: boolean; browser_push: boolean };
}

const INPUT_CLASS =
  "h-9 w-full rounded-md border border-border bg-background px-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary/40";

const emptyWorkEntry = (): WorkHistoryEntry => ({
  company: "",
  title: "",
  start_date: "",
  end_date: "",
  is_current: false,
  description: "",
  achievements: [],
});

export function ProfileForm() {
  const { data, isLoading } = useApiGet<UserProfileData>("/profile");
  const { put } = useApiMutations();
  const [form, setForm] = useState<UserProfileData | null>(null);
  const [saving, setSaving] = useState(false);
  const [savedAt, setSavedAt] = useState<number | null>(null);

  useEffect(() => {
    if (data) setForm(data);
  }, [data]);

  if (isLoading || !form) {
    return <div className="h-96 animate-pulse rounded-lg border border-border bg-muted" />;
  }

  function update<K extends keyof UserProfileData>(key: K, value: UserProfileData[K]) {
    setForm((prev) => (prev ? { ...prev, [key]: value } : prev));
  }

  async function handleSave() {
    if (!form) return;
    setSaving(true);
    try {
      await put("/profile", form);
      setSavedAt(Date.now());
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="space-y-5">
      <section className="rounded-lg border border-border bg-card p-5 shadow-soft">
        <h2 className="text-sm font-semibold">Personal Info</h2>
        <div className="mt-3 grid grid-cols-1 gap-3 sm:grid-cols-2">
          <input
            className={INPUT_CLASS}
            placeholder="Full name"
            value={form.full_name ?? ""}
            onChange={(e) => update("full_name", e.target.value)}
          />
          <input
            className={INPUT_CLASS}
            placeholder="Phone"
            value={form.phone ?? ""}
            onChange={(e) => update("phone", e.target.value)}
          />
          <input
            className={INPUT_CLASS}
            placeholder="LinkedIn URL"
            value={form.linkedin_url ?? ""}
            onChange={(e) => update("linkedin_url", e.target.value)}
          />
          <input
            className={INPUT_CLASS}
            placeholder="Portfolio URL"
            value={form.portfolio_url ?? ""}
            onChange={(e) => update("portfolio_url", e.target.value)}
          />
          <input
            className={INPUT_CLASS}
            placeholder="GitHub URL"
            value={form.github_url ?? ""}
            onChange={(e) => update("github_url", e.target.value)}
          />
        </div>
      </section>

      <section className="rounded-lg border border-border bg-card p-5 shadow-soft">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold">Work History</h2>
          <button
            onClick={() => update("work_history", [...form.work_history, emptyWorkEntry()])}
            className="inline-flex items-center gap-1 text-xs font-medium text-primary hover:underline"
          >
            <Plus size={12} /> Add role
          </button>
        </div>
        <div className="mt-3 space-y-3">
          {form.work_history.map((entry, i) => (
            <div key={i} className="rounded-md border border-border p-3">
              <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
                <input
                  className={INPUT_CLASS}
                  placeholder="Company"
                  value={entry.company}
                  onChange={(e) => {
                    const copy = [...form.work_history];
                    copy[i] = { ...entry, company: e.target.value };
                    update("work_history", copy);
                  }}
                />
                <input
                  className={INPUT_CLASS}
                  placeholder="Title"
                  value={entry.title}
                  onChange={(e) => {
                    const copy = [...form.work_history];
                    copy[i] = { ...entry, title: e.target.value };
                    update("work_history", copy);
                  }}
                />
                <input
                  className={INPUT_CLASS}
                  placeholder="Start date"
                  value={entry.start_date}
                  onChange={(e) => {
                    const copy = [...form.work_history];
                    copy[i] = { ...entry, start_date: e.target.value };
                    update("work_history", copy);
                  }}
                />
                <input
                  className={INPUT_CLASS}
                  placeholder="End date (blank if current)"
                  value={entry.end_date ?? ""}
                  onChange={(e) => {
                    const copy = [...form.work_history];
                    copy[i] = { ...entry, end_date: e.target.value };
                    update("work_history", copy);
                  }}
                />
              </div>
              <textarea
                className="mt-2 w-full rounded-md border border-border bg-background px-2.5 py-2 text-sm"
                rows={2}
                placeholder="Description / achievements"
                value={entry.description}
                onChange={(e) => {
                  const copy = [...form.work_history];
                  copy[i] = { ...entry, description: e.target.value };
                  update("work_history", copy);
                }}
              />
              <button
                onClick={() => update("work_history", form.work_history.filter((_, idx) => idx !== i))}
                className="mt-2 inline-flex items-center gap-1 text-xs text-danger hover:underline"
              >
                <Trash2 size={12} /> Remove
              </button>
            </div>
          ))}
          {form.work_history.length === 0 && (
            <p className="text-xs text-muted-foreground">No work history yet — add your first role.</p>
          )}
        </div>
      </section>

      <section className="rounded-lg border border-border bg-card p-5 shadow-soft">
        <h2 className="text-sm font-semibold">Skills & Certifications</h2>
        <div className="mt-3 space-y-3">
          <CommaListInput
            label="Skills"
            value={form.skills}
            onChange={(v) => update("skills", v)}
          />
          <CommaListInput
            label="Certifications"
            value={form.certifications}
            onChange={(v) => update("certifications", v)}
          />
          <CommaListInput
            label="Preferred locations"
            value={form.preferred_locations}
            onChange={(v) => update("preferred_locations", v)}
          />
        </div>
      </section>

      <section className="rounded-lg border border-border bg-card p-5 shadow-soft">
        <h2 className="text-sm font-semibold">Compensation & Eligibility</h2>
        <div className="mt-3 grid grid-cols-1 gap-3 sm:grid-cols-2">
          <input
            className={INPUT_CLASS}
            type="number"
            placeholder="Minimum salary expectation"
            value={form.salary_expectation_min ?? ""}
            onChange={(e) => update("salary_expectation_min", e.target.value ? Number(e.target.value) : null)}
          />
          <input
            className={INPUT_CLASS}
            type="number"
            placeholder="Maximum salary expectation"
            value={form.salary_expectation_max ?? ""}
            onChange={(e) => update("salary_expectation_max", e.target.value ? Number(e.target.value) : null)}
          />
          <input
            className={INPUT_CLASS}
            placeholder="Work authorization (e.g. US Citizen, H1-B)"
            value={form.work_authorization ?? ""}
            onChange={(e) => update("work_authorization", e.target.value)}
          />
          <input
            className={INPUT_CLASS}
            placeholder="Visa status"
            value={form.visa_status ?? ""}
            onChange={(e) => update("visa_status", e.target.value)}
          />
        </div>
        <label className="mt-3 flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={form.requires_stem_opt}
            onChange={(e) => update("requires_stem_opt", e.target.checked)}
          />
          I need STEM OPT-friendly employers
        </label>
      </section>

      <section className="rounded-lg border border-border bg-card p-5 shadow-soft">
        <h2 className="text-sm font-semibold">Notifications</h2>
        <div className="mt-3 space-y-2 text-sm">
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={form.notification_preferences.email}
              onChange={(e) =>
                update("notification_preferences", { ...form.notification_preferences, email: e.target.checked })
              }
            />
            Email
          </label>
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={form.notification_preferences.whatsapp}
              onChange={(e) =>
                update("notification_preferences", {
                  ...form.notification_preferences,
                  whatsapp: e.target.checked,
                })
              }
            />
            WhatsApp
          </label>
          {form.notification_preferences.whatsapp && (
            <input
              className={INPUT_CLASS}
              placeholder="WhatsApp number (e.g. +1XXXXXXXXXX)"
              value={form.whatsapp_number ?? ""}
              onChange={(e) => update("whatsapp_number", e.target.value)}
            />
          )}
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={form.notification_preferences.browser_push}
              onChange={(e) =>
                update("notification_preferences", {
                  ...form.notification_preferences,
                  browser_push: e.target.checked,
                })
              }
            />
            Browser push
          </label>
        </div>
      </section>

      <section className="rounded-lg border border-warning/30 bg-warning/5 p-5">
        <h2 className="text-sm font-semibold">Auto-Submit Applications</h2>
        <p className="mt-1 text-xs text-muted-foreground">
          When enabled, applications on ATS platforms we can automate (Greenhouse, Lever, Ashby,
          SmartRecruiters) are submitted automatically once filled. When off (default), every
          application is filled and prepared for you but waits for a one-click confirmation
          before it's actually sent.
        </p>
        <label className="mt-3 flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={form.auto_submit_applications}
            onChange={(e) => update("auto_submit_applications", e.target.checked)}
          />
          Auto-submit without my confirmation
        </label>
      </section>

      <div className="flex items-center gap-3">
        <button
          onClick={handleSave}
          disabled={saving}
          className="h-9 rounded-md bg-primary px-4 text-sm font-medium text-primary-foreground disabled:opacity-60"
        >
          {saving ? "Saving…" : "Save Profile"}
        </button>
        {savedAt && <span className="text-xs text-muted-foreground">Saved</span>}
      </div>
    </div>
  );
}

function CommaListInput({
  label,
  value,
  onChange,
}: {
  label: string;
  value: string[];
  onChange: (value: string[]) => void;
}) {
  const [text, setText] = useState(value.join(", "));

  useEffect(() => {
    setText(value.join(", "));
  }, [value]);

  return (
    <div>
      <label className="mb-1 block text-xs font-medium text-muted-foreground">{label}</label>
      <input
        className={INPUT_CLASS}
        value={text}
        onChange={(e) => setText(e.target.value)}
        onBlur={() => onChange(text.split(",").map((s) => s.trim()).filter(Boolean))}
        placeholder="Comma-separated"
      />
    </div>
  );
}
