import Link from "next/link";

import { GithubIcon } from "./icons";

const REPOSITORY_URL = "https://github.com/aicuc/SponsorFit";

export function SiteHeader() {
  return (
    <header className="site-header">
      <Link className="brand" href="/" aria-label="SponsorFit home">
        <span className="brand-mark" aria-hidden="true">
          <span>SF</span>
        </span>
        <span>SponsorFit</span>
      </Link>
      <nav className="site-nav" aria-label="Primary navigation">
        <Link href="/#cases">Cases</Link>
        <Link href="/#how">Method</Link>
        <a href={`${REPOSITORY_URL}#install-as-a-codex-skill`}>Install</a>
      </nav>
      <a className="button button-dark header-star" href={REPOSITORY_URL} target="_blank" rel="noreferrer">
        <GithubIcon />
        Star on GitHub
      </a>
    </header>
  );
}
