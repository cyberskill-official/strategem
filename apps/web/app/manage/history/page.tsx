import { HistoryList } from "../../../src/components/manage/history-list";
import { demoHistory } from "../../../src/lib/api/history";

/** Management flow — history — FR-WEB-007. */
export default function ManageHistoryPage() {
  const items = demoHistory();
  return (
    <div style={{ maxWidth: 960, margin: "0 auto", padding: 16 }}>
      <h1>History</h1>
      <HistoryList items={items} />
    </div>
  );
}
