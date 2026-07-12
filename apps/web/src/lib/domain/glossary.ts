/**
 * Domain display names — pure locale strings, never mixed.
 * Engine IDs stay ASCII; UI always maps through this table.
 */

import type { Locale } from "../../i18n/routing";

type Triple = { vi: string; en: string; zh: string };

const STAR: Record<string, Triple> = {
  ThienBong: { vi: "Thiên Bồng", en: "Heavenly Grass", zh: "天蓬" },
  ThienNhue: { vi: "Thiên Nhuế", en: "Heavenly Grain", zh: "天芮" },
  ThienXung: { vi: "Thiên Xung", en: "Heavenly Charge", zh: "天冲" },
  ThienPhu: { vi: "Thiên Phụ", en: "Heavenly Assistant", zh: "天辅" },
  ThienCam: { vi: "Thiên Cầm", en: "Heavenly Bird", zh: "天禽" },
  ThienTam: { vi: "Thiên Tâm", en: "Heavenly Heart", zh: "天心" },
  ThienTru: { vi: "Thiên Trụ", en: "Heavenly Pillar", zh: "天柱" },
  ThienNham: { vi: "Thiên Nhâm", en: "Heavenly Ren", zh: "天任" },
  ThienAnh: { vi: "Thiên Anh", en: "Heavenly Hero", zh: "天英" },
};

const DOOR: Record<string, Triple> = {
  Huu: { vi: "Hưu", en: "Rest", zh: "休" },
  Sinh: { vi: "Sinh", en: "Life", zh: "生" },
  Thuong: { vi: "Thương", en: "Harm", zh: "伤" },
  Do: { vi: "Đỗ", en: "Delusion", zh: "杜" },
  Canh: { vi: "Cảnh", en: "Scene", zh: "景" },
  Tu: { vi: "Tử", en: "Death", zh: "死" },
  Kinh: { vi: "Kinh", en: "Fear", zh: "惊" },
  Khai: { vi: "Khai", en: "Open", zh: "开" },
};

const GOD: Record<string, Triple> = {
  TrucPhu: { vi: "Trực Phù", en: "Chief Commander", zh: "直符" },
  DangXa: { vi: "Đằng Xà", en: "Teng Snake", zh: "腾蛇" },
  ThaiAm: { vi: "Thái Âm", en: "Great Yin", zh: "太阴" },
  LucHop: { vi: "Lục Hợp", en: "Six Harmony", zh: "六合" },
  BachHo: { vi: "Bạch Hổ", en: "White Tiger", zh: "白虎" },
  HuyenVu: { vi: "Huyền Vũ", en: "Dark Warrior", zh: "玄武" },
  CuuDia: { vi: "Cửu Địa", en: "Nine Earth", zh: "九地" },
  CuuThien: { vi: "Cửu Thiên", en: "Nine Heaven", zh: "九天" },
};

const PATTERN: Record<string, Triple> = {
  "門迫": { vi: "Môn Bách", en: "Door Presses", zh: "门迫" },
  "伏吟": { vi: "Phục Ngâm", en: "Hidden Chant", zh: "伏吟" },
  "反吟": { vi: "Phản Ngâm", en: "Reversed Chant", zh: "反吟" },
  "青龙返首": { vi: "Thanh Long Phản Thủ", en: "Azure Dragon Turns Head", zh: "青龙返首" },
  "白虎猖狂": { vi: "Bạch Hổ Xương Cuồng", en: "White Tiger Rampant", zh: "白虎猖狂" },
  // Engine romanized ids (legacy / alternate)
  MonBach: { vi: "Môn Bách", en: "Door Presses", zh: "门迫" },
  PhucNgam: { vi: "Phục Ngâm", en: "Hidden Chant", zh: "伏吟" },
  PhanNgam: { vi: "Phản Ngâm", en: "Reversed Chant", zh: "反吟" },
};

const OPT: Record<string, Triple> = {
  chaibu: { vi: "Sài bố", en: "Chai Bu", zh: "拆补" },
  zhirunzhuo: { vi: "Trực nhuận chước", en: "Zhi Run Zhuo", zh: "直润拙" },
  zhuan: { vi: "Chuyển bàn", en: "Rotating plate", zh: "转盘" },
  fei: { vi: "Phi bàn", en: "Flying plate", zh: "飞盘" },
  duong: { vi: "Dương", en: "Yang", zh: "阳" },
  am: { vi: "Âm", en: "Yin", zh: "阴" },
  day_night_default: { vi: "Ngày–đêm mặc định", en: "Day–night default", zh: "昼夜默认" },
  force_day: { vi: "Buộc ban ngày", en: "Force day", zh: "强制昼" },
  force_night: { vi: "Buộc ban đêm", en: "Force night", zh: "强制夜" },
  kim_kinh: { vi: "Kim Kinh", en: "Jin Jing", zh: "金经" },
  co_dien: { vi: "Cổ điển", en: "Classical", zh: "古典" },
  true: { vi: "Bật", en: "On", zh: "开" },
  false: { vi: "Tắt", en: "Off", zh: "关" },
  "23:00": { vi: "23:00", en: "23:00", zh: "23:00" },
  "00:00": { vi: "00:00", en: "00:00", zh: "00:00" },
  tao_zi: { vi: "Đảo Tý", en: "Inverted Zi", zh: "倒子" },
  strict: { vi: "Nghiêm", en: "Strict", zh: "严格" },
  ngu_hanh: { vi: "Ngũ hành", en: "Five phases", zh: "五行" },
  default: { vi: "Mặc định", en: "Default", zh: "默认" },
  espenak_meeus: { vi: "Espenak–Meeus", en: "Espenak–Meeus", zh: "Espenak–Meeus" },
  none: { vi: "Không dùng", en: "None", zh: "无" },
};

function pick(t: Triple | undefined, locale: Locale, fallback: string): string {
  if (!t) return fallback;
  return t[locale] ?? t.vi ?? fallback;
}

export function displayDomainTerm(raw: string | null | undefined, locale: Locale): string {
  if (raw == null || raw === "") return "";
  const key = String(raw);
  return (
    pick(STAR[key], locale, "") ||
    pick(DOOR[key], locale, "") ||
    pick(GOD[key], locale, "") ||
    pick(PATTERN[key], locale, "") ||
    pick(OPT[key], locale, "") ||
    key
  );
}

export function displayPatternName(name: string, locale: Locale): string {
  return pick(PATTERN[name], locale, name);
}

export function displayOption(value: string, locale: Locale): string {
  return pick(OPT[value], locale, value);
}

/** Literary pattern gloss — short line under the name. */
const PATTERN_GLOSS: Record<string, Triple> = {
  "門迫": {
    vi: "Môn đụng địa bàn — khí bị chặn, nên chậm bước.",
    en: "Door meets earth board — momentum checked; pause before advance.",
    zh: "门迫地盘——气势受阻，宜缓行。",
  },
  MonBach: {
    vi: "Môn đụng địa bàn — khí bị chặn, nên chậm bước.",
    en: "Door meets earth board — momentum checked; pause before advance.",
    zh: "门迫地盘——气势受阻，宜缓行。",
  },
  "伏吟": {
    vi: "Thiên địa đồng vị — sự việc trì trệ, cần kiên nhẫn.",
    en: "Heaven and earth coincide — affairs stall; patience is strategy.",
    zh: "天地同位——事多淹滞，宜守静。",
  },
  PhucNgam: {
    vi: "Thiên địa đồng vị — sự việc trì trệ, cần kiên nhẫn.",
    en: "Heaven and earth coincide — affairs stall; patience is strategy.",
    zh: "天地同位——事多淹滞，宜守静。",
  },
  "反吟": {
    vi: "Thiên địa đối xung — biến động lớn, cân nhắc trước khi hành.",
    en: "Heaven and earth oppose — sharp change; measure before acting.",
    zh: "天地对冲——变动剧烈，行前慎思。",
  },
  PhanNgam: {
    vi: "Thiên địa đối xung — biến động lớn, cân nhắc trước khi hành.",
    en: "Heaven and earth oppose — sharp change; measure before acting.",
    zh: "天地对冲——变动剧烈，行前慎思。",
  },
};

export function patternGloss(name: string, locale: Locale): string {
  return pick(PATTERN_GLOSS[name], locale, "");
}
