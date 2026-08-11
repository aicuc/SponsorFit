import type { Metadata } from "next";
import { Suspense } from "react";

import { ReportClient } from "@/components/report-client";

export const metadata: Metadata = {
  title: "Repository preview",
  description: "A shareable SponsorFit customer and paid-offer hypothesis.",
};

export default function ReportPage() {
  return (
    <Suspense fallback={<div className="report-state section-frame"><p>Loading repository preview…</p></div>}>
      <ReportClient />
    </Suspense>
  );
}
