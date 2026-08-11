"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";

import type { PreviewItem, SponsorPreview } from "@/lib/types";
import { AnalyzerForm } from "./analyzer-form";
import { ArrowIcon, CopyIcon, GithubIcon } from "./icons";

function PreviewCard({ item, index }: { item: PreviewItem; index: number }) {
  return (
    <section className="preview-card">
      <div className="preview-card-head">
        <span>0{index}</span>
        <span className={`label label-${item.label.toLowerCase()}`}>{item.label}</span>
      </div>
      <p className="preview-eyebrow">{item.eyebrow}</p>
      <h2>{item.value}</h2>
      <p>{item.detail}</p>
    </section>
  );
}

export function ReportClient() {
  const searchParams = useSearchParams();
  const repository = searchParams.get("repo")?.trim() || "";
  const [preview, setPreview] = useState<SponsorPreview | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(Boolean(repository));
  const [copied, setCopied] = useState(false);

  async function load(signal?: AbortSignal) {
    setLoading(true);
    setError("");
    try {
      const response = await fetch("/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ repository }),
        signal,
      });
      const body = (await response.json()) as SponsorPreview | { error?: string };
      if (!response.ok) {
        throw new Error("error" in body && body.error ? body.error : "Analysis failed.");
      }
      setPreview(body as SponsorPreview);
    } catch (requestError: unknown) {
      if (requestError instanceof Error && requestError.name === "AbortError") return;
      setError(requestError instanceof Error ? requestError.message : "Analysis failed.");
    } finally {
      if (!signal?.aborted) setLoading(false);
    }
  }

  useEffect(() => {
    if (!repository) return;
    const controller = new AbortController();
    fetch("/api/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ repository }),
      signal: controller.signal,
    })
      .then(async (response) => {
        const body = (await response.json()) as SponsorPreview | { error?: string };
        if (!response.ok) {
          throw new Error("error" in body && body.error ? body.error : "Analysis failed.");
        }
        return body as SponsorPreview;
      })
      .then((body) => setPreview(body))
      .catch((requestError: unknown) => {
        if (requestError instanceof Error && requestError.name === "AbortError") return;
        setError(requestError instanceof Error ? requestError.message : "Analysis failed.");
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });
    return () => controller.abort();
  }, [repository]);

  async function share() {
    const shareData = {
      title: preview ? `SponsorFit preview for ${preview.repository.fullName}` : "SponsorFit preview",
      text: preview ? `Who might sponsor ${preview.repository.fullName}?` : "Find the buyer hiding in your codebase.",
      url: window.location.href,
    };
    if (navigator.share) {
      try {
        await navigator.share(shareData);
        return;
      } catch {
        return;
      }
    }
    await navigator.clipboard.writeText(window.location.href);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 2_000);
  }

  if (loading) {
    return (
      <div className="report-state section-frame" aria-live="polite">
        <div className="scan-orbit"><span>SF</span></div>
        <p className="kicker">Scanning public evidence</p>
        <h1>{repository}</h1>
        <div className="scan-lines"><i /><i /><i /></div>
        <p>Reading metadata, README signals, and project context…</p>
      </div>
    );
  }

  if (error || !preview) {
    return (
      <div className="report-error section-frame">
        <p className="kicker">Preview unavailable</p>
        <h1>The evidence trail went cold.</h1>
        <p>{error || "SponsorFit could not generate this preview."}</p>
        <AnalyzerForm compact initialValue={repository} />
        {repository && <button className="text-button" onClick={() => void load()}>Try again →</button>}
      </div>
    );
  }

  const cards = [preview.project, preview.customer, preview.offer, preview.nextMove];

  return (
    <article className="report-page">
      <header className="report-hero section-frame">
        <div className="report-topline">
          <Link href="/">← New analysis</Link>
          <span>LIGHTWEIGHT PREVIEW / {preview.archetype.toUpperCase()}</span>
        </div>
        <div className="report-title-row">
          <div>
            <p className="kicker">SponsorFit signal report</p>
            <h1>{preview.repository.fullName}</h1>
            <p>{preview.repository.description || "No repository description was found."}</p>
          </div>
          <div className="report-actions">
            <button className="button button-light" onClick={() => void share()}>
              <CopyIcon /> {copied ? "Link copied" : "Share report"}
            </button>
            <a className="button button-accent" href="https://github.com/aicuc/SponsorFit" target="_blank" rel="noreferrer">
              <GithubIcon /> Star SponsorFit
            </a>
          </div>
        </div>
        <div className="repo-facts">
          <span><b>{preview.repository.stars.toLocaleString("en-US")}</b> stars</span>
          <span><b>{preview.repository.forks.toLocaleString("en-US")}</b> forks</span>
          <span><b>{preview.repository.language || "—"}</b> language</span>
          <span><b>{preview.repository.license || "—"}</b> license</span>
          <a href={preview.repository.url} target="_blank" rel="noreferrer">Open repository ↗</a>
        </div>
      </header>

      <div className="preview-grid section-frame">
        {cards.map((item, index) => <PreviewCard item={item} index={index + 1} key={item.eyebrow} />)}
      </div>

      <aside className="caveat section-frame">
        <span>IMPORTANT</span>
        <p>{preview.caveat}</p>
      </aside>

      <section className="full-report-cta section-frame">
        <div>
          <p className="kicker">This is only the first pass</p>
          <h2>Go from a four-card preview to a complete revenue validation plan.</h2>
        </div>
        <div className="full-report-options">
          <a className="button button-dark" href="https://github.com/aicuc/SponsorFit#install-as-a-codex-skill" target="_blank" rel="noreferrer">
            Install the Codex Skill <ArrowIcon />
          </a>
          <a className="text-link" href="https://github.com/aicuc/SponsorFit#five-minute-quick-start" target="_blank" rel="noreferrer">
            Run the Python CLI <ArrowIcon />
          </a>
        </div>
      </section>
    </article>
  );
}
