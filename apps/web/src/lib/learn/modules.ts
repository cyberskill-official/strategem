/**
 * Curriculum modules — pure locale content (no mixed languages).
 * Written for absolute beginners; classical names are secondary.
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
    glyph: "🪞",
    title: {
      vi: "Ai là bạn, ai là phía kia?",
      en: "You and the other side",
      zh: "你与对方",
    },
    summary: {
      vi: "Trước khi vẽ hình: câu hỏi của bạn cụ thể chưa? Ai đang «cầm» chuyện này?",
      en: "Before the map: is your question concrete? Who holds the matter?",
      zh: "画图前：问题够具体吗？谁在「拿」这件事？",
    },
    practiceHref: "/cast",
    body: {
      vi: [
        {
          type: "p",
          text: "Ứng dụng không thay bạn quyết. Nó chỉ dựng một khung để soi: bạn đang ở đâu trong chuyện, phía kia ở đâu, thời điểm nào đang mở.",
        },
        { type: "h", text: "Ba câu hỏi trước khi bấm nút" },
        {
          type: "ul",
          items: [
            "Câu hỏi của bạn có thể trả lời bằng «có / chưa / đợi» không — hay còn mơ hồ?",
            "Ai là người đang «cầm» chuyện — bạn hay phía kia?",
            "Nếu «tốt» thì trông ra sao? Nếu «chưa» thì trông ra sao?",
          ],
        },
        {
          type: "callout",
          text: "Câu mơ hồ → hình mơ hồ. Càng rõ «mình / người kia / lúc nào», gợi ý càng bám được.",
        },
        {
          type: "p",
          text: "Rồi mới chọn cánh cửa: la bàn thời điểm, cuộc trò chuyện hai phía, hoặc nhịp lớn của cả chặng. Tên cổ (Kỳ Môn, Lục Nhâm, Thái Ất) chỉ là nhãn — bạn chọn theo cảm giác câu hỏi.",
        },
      ],
      en: [
        {
          type: "p",
          text: "The app does not decide for you. It frames the field: where you stand, where the other side stands, which moment is open.",
        },
        { type: "h", text: "Three questions before you press the button" },
        {
          type: "ul",
          items: [
            "Can your question be answered with yes / not yet / wait — or is it still vague?",
            "Who holds the matter — you or the other side?",
            "What would “good” look like — and “not yet”?",
          ],
        },
        {
          type: "callout",
          text: "Vague questions yield vague maps. Clear “me / them / when” gives hints something to hold.",
        },
        {
          type: "p",
          text: "Then pick a door: timing compass, two-sided conversation, or the long rhythm of a chapter. Classical names are labels — choose by how the question feels.",
        },
      ],
      zh: [
        {
          type: "p",
          text: "应用不替你做决定。它只搭一个框：你在这件事里的位置、对方的位置、何时开局。",
        },
        { type: "h", text: "按按钮前的三个问题" },
        {
          type: "ul",
          items: [
            "你的问题能否用「是 / 还不行 / 等」回答——还是仍很模糊？",
            "谁在「拿」这件事——你还是对方？",
            "「好」是什么样？「还不行」是什么样？",
          ],
        },
        {
          type: "callout",
          text: "问得含糊，图也含糊。「我 / 对方 / 何时」越清楚，提示越站得住。",
        },
        {
          type: "p",
          text: "再选门：时机罗盘、双方对话、或一段路的大节奏。古名只是标签——按问题的感觉选。",
        },
      ],
    },
  },
  {
    slug: "doc-ban",
    order: 2,
    glyph: "🗺️",
    title: {
      vi: "Nhìn bức hình thế nào?",
      en: "How to look at the picture",
      zh: "怎么看这幅图",
    },
    summary: {
      vi: "Hình do máy vẽ — cùng giờ, cùng chỗ thì cùng hình. Đọc từ ngoài vào trong, từng lớp.",
      en: "The picture is computed — same time and place, same picture. Read outside-in, layer by layer.",
      zh: "图由机器所画——同时同地则同图。由外而内、一层一层读。",
    },
    practiceHref: "/results/demo-ky-mon-showcase",
    body: {
      vi: [
        {
          type: "p",
          text: "Bức hình là phần máy tính: cùng đầu vào, cùng kết quả. Bạn không cần thuộc tên từng ô — chỉ cần biết đọc theo lớp.",
        },
        { type: "h", text: "La bàn thời điểm (Kỳ Môn)" },
        {
          type: "ul",
          items: [
            "Chín ô như chín góc nhìn",
            "Mỗi ô có vài «nhãn» xếp chồng — đọc từ ngoài vào",
            "Đừng nhảy vội sang lời gợi ý trước khi nhìn vài ô then chốt",
          ],
        },
        { type: "h", text: "Cuộc trò chuyện (Lục Nhâm)" },
        {
          type: "ul",
          items: [
            "Hai lớp: đất và trời — như hai phía đối thoại",
            "Bốn «khóa» rồi ba «chặng» — mạch câu chuyện",
            "Nhìn mạch trước, chi tiết sau",
          ],
        },
        { type: "h", text: "Nhịp lớn (Thái Ất)" },
        {
          type: "ul",
          items: [
            "Nhìn hướng lớn của cả chặng",
            "Vòng quanh các vị trí",
            "Phù hợp câu hỏi dài hơi (tháng / năm / hướng đi)",
          ],
        },
        {
          type: "callout",
          text: "Luyện mắt: mở bàn mẫu, chỉ trỏ từng lớp trước khi đọc gợi ý.",
        },
      ],
      en: [
        {
          type: "p",
          text: "The picture is the computed layer: same inputs, same result. You need not memorize every cell — only how to read in layers.",
        },
        { type: "h", text: "Timing compass (Qi Men)" },
        {
          type: "ul",
          items: [
            "Nine cells like nine angles",
            "Each cell stacks labels — read outside-in",
            "Don’t leap to prose before key cells",
          ],
        },
        { type: "h", text: "Conversation (Liu Ren)" },
        {
          type: "ul",
          items: [
            "Two layers: earth and heaven — like two sides talking",
            "Four keys then three steps — the story line",
            "Follow the line first, details second",
          ],
        },
        { type: "h", text: "Long rhythm (Tai Yi)" },
        {
          type: "ul",
          items: [
            "The big direction of a chapter",
            "Positions around a ring",
            "Best for longer questions (months / years / path)",
          ],
        },
        {
          type: "callout",
          text: "Train the eye: open a sample board and name each layer before reading the hints.",
        },
      ],
      zh: [
        {
          type: "p",
          text: "图是计算层：同输入、同结果。不必背每个格——只要会分层读。",
        },
        { type: "h", text: "时机罗盘（奇门）" },
        {
          type: "ul",
          items: [
            "九格像九个角度",
            "每格叠着标签——由外而内读",
            "关键格看清前，别急跳到提示",
          ],
        },
        { type: "h", text: "对话（六壬）" },
        {
          type: "ul",
          items: [
            "两层：地与天——像双方对话",
            "四课而后三传——叙事线",
            "先跟线，后看细节",
          ],
        },
        { type: "h", text: "大节奏（太乙）" },
        {
          type: "ul",
          items: [
            "一段路的大方向",
            "环上的位置",
            "适合长问（月 / 年 / 方向）",
          ],
        },
        {
          type: "callout",
          text: "练眼：打开示例盘，先点名各层，再读提示。",
        },
      ],
    },
  },
  {
    slug: "cach-cuc",
    order: 3,
    glyph: "✨",
    title: {
      vi: "Điểm sáng và chỗ dựa",
      en: "Highlights and sources",
      zh: "亮点与出处",
    },
    summary: {
      vi: "Mỗi điểm nổi bật có tên và nguồn. Đọc như gợi ý — không như lời phán.",
      en: "Every highlight has a name and a source. Read as hints — not verdicts.",
      zh: "每个亮点有名称与出处。当提示读——不当判决。",
    },
    practiceHref: "/cast",
    body: {
      vi: [
        {
          type: "p",
          text: "Trên hình có những «điểm nổi bật» đã được đặt tên. Cát–hung chỉ là một trục; câu hỏi của bạn mới quyết ý nghĩa.",
        },
        { type: "h", text: "Khi thấy một điểm nổi" },
        {
          type: "ul",
          items: [
            "Tên là gì — và bạn hiểu nôm na ra sao?",
            "Nằm chỗ nào trên hình?",
            "Cát / hung / trung — luôn có chữ, không chỉ màu",
            "Có nguồn trích dẫn không?",
          ],
        },
        {
          type: "callout",
          text: "Gợi ý có thể chưa hoàn hảo. Luôn xem nguồn và nhãn trước khi dùng để quyết.",
        },
        {
          type: "p",
          text: "Luyện: vẽ một hình thật, ghi ba câu — (1) điểm nào nổi, (2) vì sao liên quan câu hỏi, (3) điều gì bạn vẫn chưa biết.",
        },
      ],
      en: [
        {
          type: "p",
          text: "The picture names certain highlights. Polarity is one axis; your question decides meaning.",
        },
        { type: "h", text: "When one highlight stands out" },
        {
          type: "ul",
          items: [
            "What is its name — and in plain words?",
            "Where does it sit on the picture?",
            "Auspicious / inauspicious / neutral — text, not color alone",
            "Is there a source citation?",
          ],
        },
        {
          type: "callout",
          text: "Hints may be imperfect. Always check sources and labels before deciding.",
        },
        {
          type: "p",
          text: "Practice: draw a live picture, write three lines — (1) what stands out, (2) why it touches the question, (3) what you still do not know.",
        },
      ],
      zh: [
        {
          type: "p",
          text: "图上会标出一些「亮点」。吉凶只是一轴；你的问题决定含义。",
        },
        { type: "h", text: "看到一个亮点时" },
        {
          type: "ul",
          items: [
            "叫什么——白话怎么说？",
            "在图上的哪里？",
            "吉 / 凶 / 中——要有文字，不只靠颜色",
            "有没有出处？",
          ],
        },
        {
          type: "callout",
          text: "提示可能不完美。决策前务必看出处与标签。",
        },
        {
          type: "p",
          text: "练习：画一盘真图，写三句——（1）哪些亮点突出，（2）为何关乎所问，（3）你仍不知道什么。",
        },
      ],
    },
  },
];

export function getModule(slug: string): LearnModule | undefined {
  return LEARN_MODULES.find((m) => m.slug === slug);
}
