/**
 * Offline / demo fixtures when API is unreachable or for empty states.
 * Shapes match live API envelopes — never invent protocol fields casually.
 */

import type { QueryResponse } from "../api/schemas";
import type { ChartRef } from "../api/history";
import type { StructuredReport } from "../api/report";

export const MOCK_QUERY_ID = "demo-ky-mon-showcase";
export const MOCK_REPORT_ID = "demo-report-showcase";

export function mockQueryResponse(): QueryResponse {
  return {
    query_id: MOCK_QUERY_ID,
    charts: {
      qimen: {
        he: "ky_mon",
        envelope_version: 1,
        ban: {
          dia_ban: ["戊", "己", "庚", "辛", "壬", "癸", "丁", "丙", "乙"],
          thien_ban: ["戊", "己", "庚", "辛", "壬", "癸", "丁", "丙", "乙"],
          cuu_tinh: [
            "ThienBong",
            "ThienNhue",
            "ThienXung",
            "ThienPhu",
            "ThienCam",
            "ThienTam",
            "ThienTru",
            "ThienNham",
            "ThienAnh",
          ],
          bat_mon: ["Huu", "Tu", "Thuong", "Do", null, "Khai", "Kinh", "Sinh", "Canh"],
          bat_than: [
            "TrucPhu",
            "DangXa",
            "ThaiAm",
            "LucHop",
            null,
            "BachHo",
            "HuyenVu",
            "CuuDia",
            "CuuThien",
          ],
          dinh_cuc: { so_cuc: 1, duong_don: true, nguyen: 1 },
        },
        cach_cuc: [
          { id: "qimen_mon_bach_2", name: "門迫", cung: 2, polarity: "hung", score: 0.5 },
          { id: "qimen_phuc_ngam", name: "伏吟", cung: null, polarity: "trung", score: 0.6 },
        ],
      },
    },
    patterns: [
      { id: "qimen_mon_bach_2", name: "門迫", cung: 2, polarity: "hung", score: 0.5 },
      { id: "qimen_phuc_ngam", name: "伏吟", cung: null, polarity: "trung", score: 0.6 },
    ],
    interpretation: {
      beginner: "",
      expert: "",
      recommendations: [],
      citations: [
        {
          citation_id: "yba_1",
          source: "Yên Bá",
          locator: "§ Môn Bách",
          han: "門迫",
          bach_thoai: "Môn gặp địa bàn khắc — khí bị chặn.",
          dich: "",
        },
      ],
      requires_human_review: false,
      confidence: 0.62,
    },
    ai_disclosure: {
      model: "rules-local",
      limits: "",
      review_status: "not_required",
      retrieved_citation_ids: ["yba_1"],
      degraded: true,
    },
  };
}

export function mockHistory(): ChartRef[] {
  return [
    {
      query_id: MOCK_QUERY_ID,
      he: "ky_mon",
      question_type: "trach_thoi",
      created_at: "2004-01-01T10:30:00+07:00",
      report_id: MOCK_REPORT_ID,
    },
    {
      query_id: "demo-luc-nham-1",
      he: "luc_nham",
      question_type: "hon_nhan",
      created_at: "2004-01-02T09:00:00+07:00",
    },
    {
      query_id: "demo-thai-at-1",
      he: "thai_at",
      question_type: "tai_van",
      created_at: "2004-01-03T14:15:00+07:00",
    },
  ];
}

export function mockReport(): StructuredReport {
  return {
    report_id: MOCK_REPORT_ID,
    query_id: MOCK_QUERY_ID,
    chart_summary: {
      he: "ky_mon",
      dau_vao: { datetime: "2004-01-01T10:30:00", tz: "+07:00", place: "Hà Nội" },
      lich_phap_summary: "Dương độn · Cục 1 · Nguyên 1",
      key_positions: ["Cung 2 · Môn Bách", "Cung 5 · trung cung", "Trực phù"],
    },
    detected_patterns: [
      {
        id: "qimen_mon_bach_2",
        name: "門迫",
        polarity: "hung",
        cung: 2,
        score: 0.5,
        citations: [],
      },
      {
        id: "qimen_phuc_ngam",
        name: "伏吟",
        polarity: "trung",
        cung: null,
        score: 0.6,
        citations: [],
      },
    ],
    interpretation: {
      beginner: "",
      expert: "",
      recommendations: [],
    },
    citations: [
      {
        source: "Yên Bá",
        locator: "§ Môn Bách",
        han: "門迫",
        bach_thoai: "Môn gặp địa bàn khắc — khí bị chặn.",
      },
    ],
    confidence: 0.62,
    ai_disclosure: {
      model: "rules-local",
      limits: "",
      review_status: "not_required",
    },
    created_at: "2004-01-01T10:35:00+07:00",
  };
}

export function isDemoId(id: string): boolean {
  return id.startsWith("demo-") || id === MOCK_QUERY_ID || id === MOCK_REPORT_ID;
}
