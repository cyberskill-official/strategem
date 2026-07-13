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
  // Liu Ren twelve generals
  ThienKhong: { vi: "Thiên Không", en: "Heaven Void", zh: "天空" },
  ThanhLong: { vi: "Thanh Long", en: "Azure Dragon", zh: "青龙" },
  CauTran: { vi: "Câu Trần", en: "Hooked Chen", zh: "勾陈" },
  ChuTuoc: { vi: "Chu Tước", en: "Vermilion Bird", zh: "朱雀" },
  QuyNhan: { vi: "Quý Nhân", en: "Noble", zh: "贵人" },
  ThienHau: { vi: "Thiên Hậu", en: "Heavenly Queen", zh: "天后" },
  ThaiThuong: { vi: "Thái Thường", en: "Grand Constant", zh: "太常" },
};

const PATTERN: Record<string, Triple> = {
  "門迫": { vi: "Môn Bách", en: "Door Presses", zh: "门迫" },
  "伏吟": { vi: "Phục Ngâm", en: "Hidden Chant", zh: "伏吟" },
  "反吟": { vi: "Phản Ngâm", en: "Reversed Chant", zh: "反吟" },
  // Traditional (engine) + simplified aliases — vernacular first in UI
  "青龍返首": { vi: "Thanh Long Phản Thủ", en: "Azure Dragon Turns Head", zh: "青龙返首" },
  "青龙返首": { vi: "Thanh Long Phản Thủ", en: "Azure Dragon Turns Head", zh: "青龙返首" },
  "飛鳥跌穴": { vi: "Phi Điểu Điệt Huyệt", en: "Bird Falls into Nest", zh: "飞鸟跌穴" },
  "青龍逃走": { vi: "Thanh Long Đào Tẩu", en: "Azure Dragon Flees", zh: "青龙逃走" },
  "白虎猖狂": { vi: "Bạch Hổ Xương Cuồng", en: "White Tiger Rampant", zh: "白虎猖狂" },
  "朱雀投江": { vi: "Chu Tước Đầu Giang", en: "Vermilion Bird Into River", zh: "朱雀投江" },
  "螣蛇夭矯": { vi: "Đằng Xà Yêu Kiểu", en: "Teng Snake Contorts", zh: "螣蛇夭矫" },
  "太白入熒": { vi: "Thái Bạch Nhập Huỳnh", en: "Venus Enters Mars", zh: "太白入荧" },
  "熒入太白": { vi: "Huỳnh Nhập Thái Bạch", en: "Mars Enters Venus", zh: "荧入太白" },
  "大格": { vi: "Đại Cách", en: "Great Barrier", zh: "大格" },
  "小格": { vi: "Tiểu Cách", en: "Lesser Barrier", zh: "小格" },
  "青龍折足": { vi: "Thanh Long Chiết Túc", en: "Dragon Broken Leg", zh: "青龙折足" },
  // LiuRen khoa the (COV-005)
  "元首": { vi: "Nguyên Thủ", en: "Chief Lesson", zh: "元首" },
  "重審": { vi: "Trọng Thẩm", en: "Re-examination", zh: "重审" },
  "知一": { vi: "Tri Nhất", en: "Know-One", zh: "知一" },
  "涉害": { vi: "Thiệp Hại", en: "Involving Harm", zh: "涉害" },
  "蒿矢": { vi: "Cao Thỉ", en: "Artemisia Arrow", zh: "蒿矢" },
  "彈射": { vi: "Đàn Xạ", en: "Slingshot", zh: "弹射" },
  "雜課": { vi: "Tạp Khóa", en: "Mixed Lesson", zh: "杂课" },
  "凝滯": { vi: "Ngưng Trệ", en: "Stagnation", zh: "凝滞" },
  // Engine romanized ids (legacy / alternate)
  MonBach: { vi: "Môn Bách", en: "Door Presses", zh: "门迫" },
  PhucNgam: { vi: "Phục Ngâm", en: "Hidden Chant", zh: "伏吟" },
  PhanNgam: { vi: "Phản Ngâm", en: "Reversed Chant", zh: "反吟" },
  TacKhac: { vi: "Tặc khắc", en: "Thief/Conquer", zh: "贼克" },
  TyDung: { vi: "Tỷ dụng", en: "Compare use", zh: "比用" },
  ThiepHai: { vi: "Thiệp hại", en: "Involving harm", zh: "涉害" },
  DaoKhac: { vi: "Diêu khắc", en: "Remote conquer", zh: "遥克" },
  MaoTinh: { vi: "Mão tinh", en: "Mao star", zh: "昴星" },
  BietTrach: { vi: "Biệt trách", en: "Separate choice", zh: "别责" },
  BatChuyen: { vi: "Bát chuyên", en: "Eight specials", zh: "八专" },
  // TaiYi cach (COV-006)
  "掩": { vi: "Yểm", en: "Cover", zh: "掩" },
  "迫": { vi: "Bách", en: "Press", zh: "迫" },
  "關": { vi: "Quan", en: "Gate", zh: "关" },
  "囚": { vi: "Tù", en: "Imprison", zh: "囚" },
  "擊": { vi: "Kích", en: "Strike", zh: "击" },
  "格": { vi: "Cách", en: "Barrier", zh: "格" },
  "對": { vi: "Đối", en: "Oppose", zh: "对" },
};

const OPT: Record<string, Triple> = {
  chaibu: { vi: "Sài bố", en: "Chai Bu", zh: "拆补" },
  zhirunzhuo: { vi: "Trực nhuận chước", en: "Zhi Run Zhuo", zh: "直润拙" },
  maoshan: { vi: "Mao Sơn", en: "Mao Shan", zh: "茅山" },
  zhuan: { vi: "Chuyển bàn", en: "Rotating plate", zh: "转盘" },
  fei: { vi: "Phi bàn", en: "Flying plate", zh: "飞盘" },
  duong: { vi: "Dương", en: "Yang", zh: "阳" },
  am: { vi: "Âm", en: "Yin", zh: "阴" },
  khon2: { vi: "Khôn nhị", en: "Kun-2", zh: "坤二" },
  giu_nguyen: { vi: "Giữ nguyên", en: "Keep original", zh: "保留原" },
  day_night_default: { vi: "Ngày–đêm mặc định", en: "Day–night default", zh: "昼夜默认" },
  force_day: { vi: "Buộc ban ngày", en: "Force day", zh: "强制昼" },
  force_night: { vi: "Buộc ban đêm", en: "Force night", zh: "强制夜" },
  giap_mau_canh: { vi: "Giáp Mậu Canh", en: "Jia Wu Geng", zh: "甲戊庚" },
  tach_giap: { vi: "Tách Giáp", en: "Split Jia", zh: "拆甲" },
  kim_kinh: { vi: "Kim Kinh", en: "Jin Jing", zh: "金经" },
  co_dien: { vi: "Cổ điển", en: "Classical", zh: "古典" },
  truoc_thai_at: { vi: "Trước Thái Ất", en: "Before Tai Yi", zh: "太乙前" },
  sau_thai_at: { vi: "Sau Thái Ất", en: "After Tai Yi", zh: "太乙后" },
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
