import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import { AnalyzerForm } from "@/components/analyzer-form";
import { ArrowIcon, GithubIcon } from "@/components/icons";
import { CASE_STUDIES, getCaseStudy } from "@/lib/cases";

interface CasePageProps {
  params: Promise<{ slug: string }>;
}

export function generateStaticParams() {
  return CASE_STUDIES.map((study) => ({ slug: study.slug }));
}

export async function generateMetadata({ params }: CasePageProps): Promise<Metadata> {
  const { slug } = await params;
  const study = getCaseStudy(slug);
  if (!study) return {};
  return {
    title: `${study.repository} case`,
    description: `A SponsorFit customer and paid-offer hypothesis for ${study.repository}.`,
  };
}

export default async function CasePage({ params }: CasePageProps) {
  const { slug } = await params;
  const study = getCaseStudy(slug);
  if (!study) notFound();
  const index = CASE_STUDIES.findIndex((item) => item.slug === study.slug);

  return (
    <article className={`case-detail case-${study.accent}`}>
      <header className="case-detail-hero section-frame">
        <div className="case-detail-topline">
          <Link href="/#cases">← All field notes</Link>
          <span>CASE 0{index + 1} / 05</span>
        </div>
        <div className="case-detail-title">
          <div>
            <p className="kicker">{study.category}</p>
            <h1>{study.repository}</h1>
          </div>
          <a className="round-link" href={study.repositoryUrl} target="_blank" rel="noreferrer" aria-label={`Open ${study.repository} on GitHub`}>
            <GithubIcon />
          </a>
        </div>
        <p className="case-outcome">{study.outcome}</p>
      </header>

      <div className="case-analysis section-frame">
        <aside className="evidence-panel">
          <p className="label label-observed">Observed</p>
          <h2>Repository signals</h2>
          <ul>
            {study.observed.map((item) => <li key={item}>{item}</li>)}
          </ul>
          <p className="evidence-note">These signals describe the public project. They do not prove demand.</p>
        </aside>

        <div className="hypothesis-stack">
          <section className="hypothesis-block">
            <div className="hypothesis-index">01</div>
            <div><p className="label label-hypothesis">Hypothesis</p><h2>Happiest sponsor</h2><p className="big-answer">{study.customer}</p></div>
          </section>
          <section className="hypothesis-block">
            <div className="hypothesis-index">02</div>
            <div><p className="label label-hypothesis">Hypothesis</p><h2>Paid boundary</h2><p className="big-answer">{study.offer}</p></div>
          </section>
          <section className="hypothesis-block">
            <div className="hypothesis-index">03</div>
            <div><p className="label label-inferred">Inferred</p><h2>Next validation move</h2><p className="big-answer">{study.nextMove}</p></div>
          </section>
        </div>
      </div>

      <section className="case-lesson section-frame">
        <span>THE TAKEAWAY</span>
        <blockquote>“{study.lesson}”</blockquote>
      </section>

      <section className="case-try section-frame">
        <div><p className="kicker">Now inspect your project</p><h2>What is your repository already telling you?</h2></div>
        <AnalyzerForm compact />
        <a className="text-link" href="https://github.com/aicuc/SponsorFit" target="_blank" rel="noreferrer">
          Star SponsorFit <ArrowIcon />
        </a>
      </section>
    </article>
  );
}
