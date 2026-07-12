import { SchoolFlagsForm } from "../../../src/components/manage/school-flags-form";

/** Management flow — school flags — FR-WEB-007. */
export default function ManageSettingsPage() {
  return (
    <div style={{ maxWidth: 960, margin: "0 auto", padding: 16 }}>
      <h1>School flags</h1>
      <SchoolFlagsForm />
    </div>
  );
}
