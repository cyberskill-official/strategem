/**
 * Curriculum modules — pure locale content (no mixed languages).
 */

export type LessonBlock =
  | { type: "p"; text: string }
  | { type: "h"; text: string }
  | { type: "ul"; items: string[] }
  | { type: "callout"; text: string };

export type LearnModule = {
  slug: string;
  order: number;
  title: Record<"vi" | "en" | "zh", string>;
  summary: Record<"vi" | "en" | "zh", string>;
  glyph: string;
  body: Record<"vi" | "en" | "zh", LessonBlock[]>;
  practiceHref: string;
};

export const LEARN_MODULES: LearnModule[] = [
  {
    slug: "chu-khach",
    order: 1,
    glyph: "主",
    title: {
      vi: "Khung chủ–khách",
      en: "Host–guest frame",
      zh: "主客框架",
    },
    summary: {
      vi: "Ai hỏi, ai ứng; thế và thời. Học đặt câu hỏi để bàn trả lời được.",
      en: "Who asks, who responds; stance and time. Questions the board can answer.",
      zh: "谁问谁应；势与时。学会提出盘能回答的问题。",
    },
    practiceHref: "/cast",
    body: {
      vi: [
        {
          type: "p",
          text: "Tam Thức không thay bạn quyết định. Nó dựng một khung để soi: ai là chủ, ai là khách, thời điểm nào đang mở.",
        },
        { type: "h", text: "Ba câu trước khi lập quẻ" },
        {
          type: "ul",
          items: [
            "Câu hỏi cụ thể đến mức nào? (thời điểm, phương hướng, đối tác)",
            "Ai là chủ sự — bạn hay bên kia?",
            "Thắng trông như thế nào, thua trông như thế nào?",
          ],
        },
        {
          type: "callout",
          text: "Câu mơ hồ cho ra bàn mơ hồ. Càng rõ chủ–khách, cách cục càng có chỗ bám.",
        },
        {
          type: "p",
          text: "Khi đã có câu, chọn hệ: Kỳ Môn cho cục cung–môn–thần; Lục Nhâm cho tứ khóa–tam truyền; Thái Ất cho vận số lớn.",
        },
      ],
      en: [
        {
          type: "p",
          text: "The Three Arts do not decide for you. They frame the field: who is host, who is guest, which hour is open.",
        },
        { type: "h", text: "Three questions before casting" },
        {
          type: "ul",
          items: [
            "How concrete is the question? (timing, direction, counterpart)",
            "Who holds the matter — you or the other side?",
            "What would winning look like — and losing?",
          ],
        },
        {
          type: "callout",
          text: "Vague questions yield vague boards. Clear host–guest gives patterns something to hold.",
        },
        {
          type: "p",
          text: "Then choose the art: Qi Men for palace–door–deity, Liu Ren for keys and transmissions, Tai Yi for longer cycles.",
        },
      ],
      zh: [
        {
          type: "p",
          text: "三式并不替你裁决。它建立读势之框：谁为主、谁为客、何时开局。",
        },
        { type: "h", text: "起盘前三问" },
        {
          type: "ul",
          items: [
            "问题有多具体？（时点、方位、对象）",
            "用事者是谁——你还是对方？",
            "胜与负各是什么样子？",
          ],
        },
        {
          type: "callout",
          text: "问得含糊，盘也含糊。主客清楚，格局才有所依附。",
        },
        {
          type: "p",
          text: "然后择术：奇门看宫门神，六壬看四课三传，太乙看大运。",
        },
      ],
    },
  },
  {
    slug: "doc-ban",
    order: 2,
    glyph: "盤",
    title: {
      vi: "Đọc ban đồ",
      en: "Reading the board",
      zh: "读盘",
    },
    summary: {
      vi: "Từ can đến cách: cửu cung, tứ khóa, cung Thái Ất — từng lớp một.",
      en: "Stem to pattern: nine palaces, four keys, Tai Yi station — layer by layer.",
      zh: "从干到局：九宫、四课、太乙所在——层层深入。",
    },
    practiceHref: "/results/demo-ky-mon-showcase",
    body: {
      vi: [
        {
          type: "p",
          text: "Ban đồ là phần máy tính định nghĩa: cùng đầu vào, cùng kết quả. Đọc từ ngoài vào trong.",
        },
        { type: "h", text: "Kỳ Môn" },
        {
          type: "ul",
          items: [
            "Cung → can → tinh → môn → thần",
            "Cách cục (môn bách, phục ngâm…) là lớp thứ hai",
            "Không nhảy vội sang diễn giải trước khi soi đủ cung then chốt",
          ],
        },
        { type: "h", text: "Lục Nhâm" },
        {
          type: "ul",
          items: [
            "Thiên địa bàn: nguyệt tướng thêm chiêm thời",
            "Tứ khóa rồi tam truyền — mạch câu chuyện",
            "Thập nhị thiên tướng phủ lên các chi",
          ],
        },
        { type: "h", text: "Thái Ất" },
        {
          type: "ul",
          items: [
            "Thái Ất đóng cung nào",
            "Thập lục thần trên vòng",
            "Chủ–khách đại tướng và các toán",
          ],
        },
        {
          type: "callout",
          text: "Luyện mắt: mở bàn mẫu, chỉ trỏ từng lớp trước khi đọc lời diễn giải.",
        },
      ],
      en: [
        {
          type: "p",
          text: "The board is the computed layer: same inputs, same result. Read outside-in.",
        },
        { type: "h", text: "Qi Men" },
        {
          type: "ul",
          items: [
            "Palace → stem → star → door → deity",
            "Patterns (door presses, hidden chant…) are the second layer",
            "Do not leap to interpretation before key palaces",
          ],
        },
        { type: "h", text: "Liu Ren" },
        {
          type: "ul",
          items: [
            "Heaven–earth board: month general on the hour",
            "Four keys then three transmissions — the story line",
            "Twelve generals over the branches",
          ],
        },
        { type: "h", text: "Tai Yi" },
        {
          type: "ul",
          items: [
            "Where Tai Yi sits",
            "Sixteen deities on the ring",
            "Host–guest generals and totals",
          ],
        },
        {
          type: "callout",
          text: "Train the eye: open a sample board and name each layer before reading the prose.",
        },
      ],
      zh: [
        {
          type: "p",
          text: "盘局是计算层：同输入、同结果。由外而内读。",
        },
        { type: "h", text: "奇门" },
        {
          type: "ul",
          items: [
            "宫 → 干 → 星 → 门 → 神",
            "格局（门迫、伏吟…）为第二层",
            "未看清关键宫前，勿急跳到解读",
          ],
        },
        { type: "h", text: "六壬" },
        {
          type: "ul",
          items: [
            "天地盘：月将加占时",
            "四课而后三传——叙事脉络",
            "十二天将覆于支上",
          ],
        },
        { type: "h", text: "太乙" },
        {
          type: "ul",
          items: [
            "太乙落何宫",
            "环上十六神",
            "主客大将与诸算",
          ],
        },
        {
          type: "callout",
          text: "练眼：打开示例盘，先点名各层，再读解说。",
        },
      ],
    },
  },
  {
    slug: "cach-cuc",
    order: 3,
    glyph: "引",
    title: {
      vi: "Cách cục và trích dẫn",
      en: "Patterns and citations",
      zh: "格局与引用",
    },
    summary: {
      vi: "Mỗi cách gắn nguồn. Đối chiếu Hán, bạch thoại và bối cảnh thực.",
      en: "Every pattern carries a source. Match classical text, vernacular, and real context.",
      zh: "每局皆有出处。对照汉文、白话与现实情境。",
    },
    practiceHref: "/cast",
    body: {
      vi: [
        {
          type: "p",
          text: "Cách cục là tín hiệu đã được đặt tên. Cát–hung chỉ là một trục; ngữ cảnh mới quyết ý nghĩa.",
        },
        { type: "h", text: "Đọc một cách cục" },
        {
          type: "ul",
          items: [
            "Tên (Hán + tên gọi địa phương)",
            "Cung / vị trí nếu có",
            "Cực tính (cát / hung / trung) — luôn kèm biểu tượng, không chỉ màu",
            "Trích dẫn nguồn khi có",
          ],
        },
        {
          type: "callout",
          text: "Đầu ra mô hình có thể suy giảm theo quy tắc. Luôn kiểm nhãn và nguồn trước khi dùng để quyết.",
        },
        {
          type: "p",
          text: "Luyện: lập một quẻ thật, ghi ba câu — (1) cách nào nổi, (2) vì sao liên quan câu hỏi, (3) điều gì bạn vẫn chưa biết.",
        },
      ],
      en: [
        {
          type: "p",
          text: "A pattern is a named signal. Polarity is one axis; context decides meaning.",
        },
        { type: "h", text: "Reading one pattern" },
        {
          type: "ul",
          items: [
            "Name (classical + local form)",
            "Palace / position if any",
            "Polarity (auspicious / inauspicious / neutral) — icon and text, never color alone",
            "Source citation when present",
          ],
        },
        {
          type: "callout",
          text: "Model output may degrade to rules. Always check the disclosure and sources before deciding.",
        },
        {
          type: "p",
          text: "Practice: cast live, write three lines — (1) which patterns stand out, (2) why they touch the question, (3) what you still do not know.",
        },
      ],
      zh: [
        {
          type: "p",
          text: "格局是被命名的信号。吉凶只是一轴；语境决定含义。",
        },
        { type: "h", text: "读一局" },
        {
          type: "ul",
          items: [
            "名称（汉文与本地称呼）",
            "宫位（若有）",
            "极性（吉 / 凶 / 中）——图标与文字并用，不只靠颜色",
            "有则看引用",
          ],
        },
        {
          type: "callout",
          text: "模型输出可能降级为规则。决策前务必检查披露与出处。",
        },
        {
          type: "p",
          text: "练习：起一盘真盘，写三句——（1）哪些格局突出，（2）为何关乎所问，（3）你仍不知道什么。",
        },
      ],
    },
  },
];

export function getModule(slug: string): LearnModule | undefined {
  return LEARN_MODULES.find((m) => m.slug === slug);
}
