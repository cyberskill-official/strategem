import { ResultsPanel, type QueryResponseView } from "../../../src/components/results/results-panel";

/** Demo fixture until API fetch by queryId lands (FR-API-004). */
function demoResponse(queryId: string): QueryResponseView {
  return {
    query_id: queryId,
    charts: {
      qimen: {
        he: "ky_mon",
        ban: {
          dinh_cuc: { so_cuc: 1, duong_don: true },
          dia_ban: ["戊", "己", "庚", "辛", "壬", "癸", "丁", "丙", "乙"],
          thien_ban: ["戊", "己", "庚", "辛", "壬", "癸", "丁", "丙", "乙"],
          cuu_tinh: Array(9).fill("ThienBong"),
          bat_mon: ["Huu", "Tu", "Thuong", "Do", null, "Khai", "Kinh", "Sinh", "Canh"],
          bat_than: Array(9).fill("TrucPhu"),
        },
        cach_cuc: [
          {
            id: "qimen_thanh_long_hoi_dau",
            name: "青龍返首",
            cung: 1,
            polarity: "cat",
          },
        ],
      },
    },
    patterns: [
      {
        id: "qimen_thanh_long_hoi_dau",
        name: "青龍返首",
        cung: 1,
        polarity: "cat",
      },
    ],
    interpretation: {
      beginner: "A cautious educational reading of the chart patterns.",
      expert: "Technical notes grounded in the retrieved classical units.",
      recommendations: ["Reflect on timing using the cited classical guidance."],
      citations: [
        {
          citation_id: "c1",
          source: "Yên Ba Điếu Tẩu Ca",
          locator: "1.1",
          han: "青龍返首",
          bach_thoai: "Thanh long hồi đầu",
          dich: "Azure Dragon turns head — auspicious for major affairs.",
        },
      ],
      requires_human_review: false,
      confidence: 0.7,
    },
    ai_disclosure: {
      model: "stub-llm",
      limits: "Heritage education / decision support; not fortune-telling.",
      review_status: "not_required",
      retrieved_citation_ids: ["c1"],
    },
  };
}

export default async function ResultsPage({
  params,
}: {
  params: Promise<{ queryId: string }>;
}) {
  const { queryId } = await params;
  const response = demoResponse(queryId);
  return (
    <div style={{ maxWidth: 960, margin: "0 auto" }}>
      <h1 style={{ fontSize: "var(--text-xl)" }}>Results · {queryId}</h1>
      <ResultsPanel response={response} />
    </div>
  );
}
