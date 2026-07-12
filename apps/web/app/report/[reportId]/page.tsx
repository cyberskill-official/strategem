import { ReportView } from "../../../src/components/report/report-view";
import { demoReport } from "../../../src/lib/api/report";

/** Report view screen — FR-WEB-005. Demo fixture until live fetch lands. */
export default async function ReportPage({
  params,
}: {
  params: Promise<{ reportId: string }>;
}) {
  const { reportId } = await params;
  const report = demoReport(reportId);
  return (
    <div style={{ maxWidth: 960, margin: "0 auto", padding: 16 }}>
      <ReportView report={report} />
    </div>
  );
}
