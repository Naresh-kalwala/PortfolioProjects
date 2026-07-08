"use client";

import { CheckCircle2, FileUp, UploadCloud } from "lucide-react";
import { useRef, useState } from "react";
import { useSWRConfig } from "swr";

import { useApiGet, useApiMutations } from "@/hooks/use-api";

interface MasterResume {
  id: string;
  name: string;
  is_primary: boolean;
  created_at: string;
}

export function ResumeUpload() {
  const { data: resumes } = useApiGet<MasterResume[]>("/resumes/master");
  const { post } = useApiMutations();
  const { mutate } = useSWRConfig();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [uploading, setUploading] = useState(false);
  const [justUploaded, setJustUploaded] = useState(false);

  async function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);
    formData.append("name", file.name);

    setUploading(true);
    try {
      await post("/resumes/master", formData);
      await mutate("/resumes/master");
      setJustUploaded(true);
      setTimeout(() => setJustUploaded(false), 4000);
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  }

  const primary = resumes?.find((r) => r.is_primary);

  return (
    <div className="rounded-lg border border-border bg-card p-5 shadow-soft">
      <h2 className="text-sm font-semibold">Master Resume</h2>
      <p className="mt-1 text-xs text-muted-foreground">
        The single source of truth every tailored resume is generated from. The AI only rewords
        and reorders this content — it never invents experience beyond what's here.
      </p>

      {justUploaded && (
        <div className="mt-3 flex items-center gap-2 rounded-md bg-success/10 p-3 text-sm text-success">
          <CheckCircle2 size={14} />
          Resume uploaded successfully
        </div>
      )}

      {primary && (
        <div className="mt-3 flex items-center gap-2 rounded-md bg-muted p-3 text-sm">
          <FileUp size={14} className="text-primary" />
          {primary.name}
          <span className="ml-auto text-xs text-muted-foreground">Active</span>
        </div>
      )}

      <label className="mt-3 flex h-24 cursor-pointer flex-col items-center justify-center gap-1 rounded-md border border-dashed border-border text-sm text-muted-foreground transition-colors hover:bg-muted">
        <UploadCloud size={18} />
        {uploading ? "Uploading…" : "Upload PDF or DOCX to replace it"}
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.docx"
          className="hidden"
          onChange={handleFileChange}
          disabled={uploading}
        />
      </label>
    </div>
  );
}
