"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

import { ArrowIcon, SparkIcon } from "./icons";

interface AnalyzerFormProps {
  compact?: boolean;
  initialValue?: string;
}

export function AnalyzerForm({ compact = false, initialValue = "" }: AnalyzerFormProps) {
  const router = useRouter();
  const [repository, setRepository] = useState(initialValue);
  const [error, setError] = useState("");

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const value = repository.trim();
    if (!value) {
      setError("Paste a public GitHub repository URL first.");
      return;
    }
    setError("");
    router.push(`/report?repo=${encodeURIComponent(value)}`);
  }

  return (
    <form className={`analyzer-form${compact ? " analyzer-form-compact" : ""}`} onSubmit={submit}>
      <label htmlFor={compact ? "repository-compact" : "repository"}>
        <SparkIcon />
        Public GitHub repository
      </label>
      <div className="input-row">
        <input
          id={compact ? "repository-compact" : "repository"}
          name="repository"
          type="text"
          inputMode="url"
          autoComplete="url"
          placeholder="https://github.com/owner/repository"
          value={repository}
          onChange={(event) => setRepository(event.target.value)}
          aria-describedby={error ? "repository-error" : undefined}
          aria-invalid={Boolean(error)}
        />
        <button type="submit" className="button button-accent">
          Analyze my repo
          <ArrowIcon />
        </button>
      </div>
      {error ? (
        <p className="form-error" id="repository-error" role="alert">
          {error}
        </p>
      ) : (
        <p className="form-hint">No login. Public metadata only. Results are hypotheses, not market facts.</p>
      )}
    </form>
  );
}
