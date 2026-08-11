import Link from "next/link";

export function SiteFooter() {
  return (
    <footer className="site-footer">
      <div>
        <p className="footer-wordmark">SponsorFit</p>
        <p>Evidence before business storytelling.</p>
      </div>
      <div className="footer-links">
        <a href="https://github.com/aicuc/SponsorFit" target="_blank" rel="noreferrer">
          GitHub
        </a>
        <a href="https://github.com/aicuc/SponsorFit/blob/main/README.md#install-as-a-codex-skill" target="_blank" rel="noreferrer">
          Codex Skill
        </a>
        <Link href="/#cases">Cases</Link>
      </div>
      <p className="footer-note">Open source · MIT</p>
    </footer>
  );
}
