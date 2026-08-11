import type { Metadata } from "next";
import type { ReactNode } from "react";

import { SiteFooter } from "@/components/site-footer";
import { SiteHeader } from "@/components/site-header";

import "./globals.css";

export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000"),
  title: {
    default: "SponsorFit — Find the buyer hiding in your codebase",
    template: "%s — SponsorFit",
  },
  description:
    "Turn open-source repository evidence into a customer hypothesis, paid offer, and concrete validation move.",
  openGraph: {
    title: "SponsorFit",
    description: "Find the people who would happily pay for what you already love building.",
    type: "website",
  },
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <a className="skip-link" href="#main-content">
          Skip to content
        </a>
        <div className="site-shell">
          <SiteHeader />
          <main id="main-content">{children}</main>
          <SiteFooter />
        </div>
      </body>
    </html>
  );
}
