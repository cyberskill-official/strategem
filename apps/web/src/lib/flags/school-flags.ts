/**
 * School flag enums + defaults — FR-WEB-007.
 * Options match engine closed enums; no school is marked "correct".
 */

export type SchoolConfig = {
  co_truong_phai: Record<string, string>;
  co_lich_phap: Record<string, string>;
};

export type FlagDef = {
  key: string;
  system: "ky_mon" | "luc_nham" | "thai_at" | "shared";
  options: string[];
  default: string;
  description: string;
};

export const SCHOOL_FLAGS_STORAGE_KEY = "tamthuc.schoolConfig.v1";

export const SCHOOL_FLAGS: FlagDef[] = [
  {
    key: "dingju_method",
    system: "ky_mon",
    // COV-003: maoshan is a supported engine dingju option (cast-cli / cyberos-qimen)
    options: ["chaibu", "zhirunzhuo", "maoshan"],
    default: "chaibu",
    description: "QiMen dinh cục method (no school is marked correct)",
  },
  {
    key: "pan_method",
    system: "ky_mon",
    options: ["zhuan", "fei"],
    default: "zhuan",
    description: "QiMen ban rotation",
  },
  {
    key: "yin_yang_pan",
    system: "ky_mon",
    options: ["duong", "am"],
    default: "duong",
    description: "QiMen am/duong pan",
  },
  {
    // COV-003: zhong gong ky placement for QiMen
    key: "zhong_gong_ky",
    system: "ky_mon",
    options: ["khon2", "giu_nguyen"],
    default: "khon2",
    description: "QiMen middle-palace ky placement",
  },
  {
    key: "khoi_quy_nhan",
    system: "luc_nham",
    options: ["day_night_default", "force_day", "force_night"],
    default: "day_night_default",
    description: "LiuRen quý nhân selection",
  },
  {
    key: "quy_nhan_variant",
    system: "luc_nham",
    options: ["giap_mau_canh", "tach_giap"],
    default: "giap_mau_canh",
    description: "LiuRen quý nhân school variant",
  },
  {
    key: "epoch",
    system: "thai_at",
    options: ["kim_kinh", "co_dien"],
    default: "kim_kinh",
    description: "TaiYi epoch",
  },
  {
    // COV-003: dem_toan counting side for TaiYi
    key: "dem_toan",
    system: "thai_at",
    options: ["truoc_thai_at", "sau_thai_at"],
    default: "truoc_thai_at",
    description: "TaiYi counting before/after Thai At",
  },
  {
    key: "use_true_solar_time",
    system: "shared",
    options: ["true", "false"],
    default: "true",
    description: "Calendar: true solar time",
  },
  {
    key: "zi_hour_day_rollover",
    system: "shared",
    options: ["23:00", "00:00"],
    default: "23:00",
    description: "Calendar: zi hour day rollover",
  },
  {
    key: "late_zi_handling",
    system: "shared",
    options: ["tao_zi", "strict"],
    default: "tao_zi",
    description: "Calendar: late zi handling",
  },
  {
    key: "truong_sinh_phai",
    system: "shared",
    options: ["ngu_hanh", "default"],
    default: "ngu_hanh",
    description: "Calendar: trường sinh school",
  },
  {
    key: "delta_t_model",
    system: "shared",
    options: ["espenak_meeus", "none"],
    default: "espenak_meeus",
    description: "Calendar: delta-T model",
  },
];

export function defaultSchoolConfig(): SchoolConfig {
  const co_truong_phai: Record<string, string> = {};
  const co_lich_phap: Record<string, string> = {};
  for (const f of SCHOOL_FLAGS) {
    if (f.system === "shared") co_lich_phap[f.key] = f.default;
    else co_truong_phai[`${f.system}.${f.key}`] = f.default;
  }
  return { co_truong_phai, co_lich_phap };
}

/** Carry flags into FR-WEB-002 cast request (UI sets; engine stamps). */
export function toCastOverrides(cfg: SchoolConfig): {
  co_truong_phai: Record<string, string>;
  co_lich_phap: Record<string, string>;
} {
  return {
    co_truong_phai: { ...cfg.co_truong_phai },
    co_lich_phap: { ...cfg.co_lich_phap },
  };
}

/** Flat co_truong_phai map engines accept (includes lich flags under co_lich_phap keys). */
export function toCastPayloadFlags(cfg: SchoolConfig): Record<string, string> {
  // Prefer short keys for known engine flags
  const out: Record<string, string> = {};
  for (const [k, v] of Object.entries(cfg.co_truong_phai)) {
    const short = k.includes(".") ? k.split(".").slice(1).join(".") : k;
    out[short] = v;
    out[k] = v;
  }
  for (const [k, v] of Object.entries(cfg.co_lich_phap)) {
    out[k] = v;
  }
  return out;
}

export function loadSchoolConfig(): SchoolConfig {
  if (typeof window === "undefined") return defaultSchoolConfig();
  try {
    const raw = localStorage.getItem(SCHOOL_FLAGS_STORAGE_KEY);
    if (!raw) return defaultSchoolConfig();
    const parsed = JSON.parse(raw) as SchoolConfig;
    if (!parsed?.co_truong_phai || !parsed?.co_lich_phap) return defaultSchoolConfig();
    return {
      co_truong_phai: { ...defaultSchoolConfig().co_truong_phai, ...parsed.co_truong_phai },
      co_lich_phap: { ...defaultSchoolConfig().co_lich_phap, ...parsed.co_lich_phap },
    };
  } catch {
    return defaultSchoolConfig();
  }
}

export function saveSchoolConfig(cfg: SchoolConfig): void {
  if (typeof window === "undefined") return;
  try {
    localStorage.setItem(SCHOOL_FLAGS_STORAGE_KEY, JSON.stringify(cfg));
  } catch {
    /* ignore */
  }
}
