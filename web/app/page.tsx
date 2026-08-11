import Link from "next/link";

import { AnalyzerForm } from "@/components/analyzer-form";
import { ArrowIcon, GithubIcon } from "@/components/icons";
import { CASE_STUDIES } from "@/lib/cases";

const REPOSITORY_URL = "https://github.com/aicuc/SponsorFit";

export default function HomePage() {
  return (
    <>
      <section className="hero section-frame">
        <div className="hero-copy reveal reveal-1">
          <p className="kicker"><span>Open-source revenue intelligence</span><span>01 / Preview</span></p>
          <h1>
            Find the buyer
            <br />
            hiding in your <em>codebase.</em>
          </h1>
          <p className="hero-lede">
            SponsorFit reads the evidence in your repository and turns it into a customer hypothesis,
            a paid offer, and one concrete move to validate next.
          </p>
          <div className="hero-actions">
            <a className="button button-dark" href={REPOSITORY_URL} target="_blank" rel="noreferrer">
              <GithubIcon />
              Star SponsorFit
            </a>
            <a className="text-link" href="#cases">
              See real project cases <ArrowIcon />
            </a>
          </div>
        </div>

        <div className="hero-art reveal reveal-2" aria-label="A sample SponsorFit analysis card">
          <div className="art-stamp">Repository<br />signal scan</div>
          <div className="sample-card">
            <div className="sample-card-head">
              <span className="status-dot" />
              <span>ANALYSIS / PUBLIC REPO</span>
              <span>SF—001</span>
            </div>
            <p className="sample-label">Happiest sponsor</p>
            <p className="sample-answer">The team whose production workflow already depends on your project.</p>
            <div className="sample-rule" />
            <div className="sample-grid">
              <div><span>Evidence</span><strong>Repository</strong></div>
              <div><span>Demand</span><strong>Unverified</strong></div>
              <div><span>Next move</span><strong>Interview</strong></div>
            </div>
          </div>
          <span className="scribble scribble-a">Who hurts?</span>
          <span className="scribble scribble-b">What changes?</span>
        </div>

        <div className="hero-analyzer reveal reveal-3">
          <AnalyzerForm />
        </div>
      </section>

      <section className="manifesto-strip" aria-label="SponsorFit principles">
        <span>Observed facts</span>
        <i>→</i>
        <span>Explicit inference</span>
        <i>→</i>
        <span>Testable hypothesis</span>
        <i>→</i>
        <span>Real conversation</span>
      </section>

      <section className="cases section-frame" id="cases">
        <div className="section-heading">
          <div>
            <p className="kicker">02 / Field notes</p>
            <h2>Five projects.<br />Five different paths to value.</h2>
          </div>
          <p>
            A project’s paid boundary should follow the expensive job around the code—not a generic SaaS menu.
            These pre-generated cases stay available even when GitHub’s API does not.
          </p>
        </div>

        <div className="case-grid">
          {CASE_STUDIES.map((study, index) => (
            <Link className={`case-card case-${study.accent}`} href={`/cases/${study.slug}`} key={study.slug}>
              <div className="case-number">0{index + 1}</div>
              <div className="case-meta">
                <span>{study.category}</span>
                <span>Hypothesis</span>
              </div>
              <h3>{study.repository}</h3>
              <p>{study.customer}</p>
              <div className="case-link">Read the case <ArrowIcon /></div>
            </Link>
          ))}
        </div>
      </section>

      <section className="method section-frame" id="how">
        <div className="method-intro">
          <p className="kicker">03 / The method</p>
          <h2>Less fantasy.<br />More evidence.</h2>
          <p>
            The web preview is deliberately small. The full Codex Skill and Python CLI go deeper into customer
            ranking, free/paid boundaries, revenue ladders, and validation plans.
          </p>
        </div>
        <ol className="method-list">
          <li><span>01</span><div><h3>Read what exists</h3><p>Description, README, language, license, and public repository signals.</p></div></li>
          <li><span>02</span><div><h3>Separate fact from guess</h3><p>Every result is marked Observed, Inferred, or Hypothesis.</p></div></li>
          <li><span>03</span><div><h3>Name the sponsor</h3><p>Not everyone who benefits has the same pain, urgency, or budget.</p></div></li>
          <li><span>04</span><div><h3>Validate before building</h3><p>The best next feature is often a benchmark, interview, or narrow paid pilot.</p></div></li>
        </ol>
      </section>

      <section className="final-cta section-frame">
        <p className="kicker">Your repository is already saying something.</p>
        <h2>Find out who needs to hear it.</h2>
        <AnalyzerForm compact />
        <div className="cta-foot">
          <span>Free · Open source · No account</span>
          <a href={REPOSITORY_URL} target="_blank" rel="noreferrer">View source <ArrowIcon /></a>
        </div>
      </section>
    </>
  );
}
