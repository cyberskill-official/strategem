# Tài liệu 1 — Tổng quan Tam Thức và phân công ba hệ

> Bộ tài liệu Tam Thức (三式) của CyberSkill — Tập 1/7
> Phiên bản 1.0 · Slogan: "Turn Your Will Into Real" — Hiện Thực Hoá Ý Chí
> Nội dung mang tính tham khảo tri thức và giáo dục di sản, không phải lời khuyên y tế, pháp lý, hay tài chính.

Tài liệu này mở đầu bộ bảy tập về Tam Thức (三式). Nó trả lời ba câu hỏi nền tảng trước khi đi vào kỹ thuật: Tam Thức là gì, ba hệ chia việc ra sao, và vì sao một nền tảng phần mềm hiện đại nên tiếp cận cả ba như một thể thống nhất thay vì ba sản phẩm rời rạc.

## Thông tin tài liệu

| Trường | Nội dung |
|---|---|
| Bộ tài liệu | Tam Thức (三式) — hệ thống hoá để lập trình, giảng dạy, và hành nghề tư vấn chiến lược |
| Tập | 1 trên 7 — Tổng quan và phân công ba hệ |
| Đối tượng đọc | Kỹ sư phần mềm, kiến trúc sư tri thức, người học và nghiên cứu, đội sản phẩm và kinh doanh của CyberSkill |
| Ngôn ngữ | Tiếng Việt, giữ nguyên thuật ngữ Hán tự kèm phiên âm; thuật ngữ phần mềm để nguyên tiếng Anh |
| Vị trí trong bộ | Đặt nền cho các tập chuyên sâu 2 (Lục Nhâm), 3 (Kỳ Môn), 4 (Thái Ất), 5 (nền dùng chung), 6 (kiến trúc kỹ thuật), 7 (sản phẩm và lộ trình) |

Định hướng thương hiệu. Tài liệu bám hệ thiết kế CyberSkill Global Design System: màu nền tảng Umber #45210E và Ochre #F4BA17, chữ Be Vietnam Pro cho tiếng Việt và JetBrains Mono cho mã, tinh thần bốn trục giọng nói warm, direct, honest, respectful.

## Mục lục

1. Tam Thức là gì
2. Phân công ba hệ theo tam tài
3. Lịch sử và dòng truyền thừa
4. Thư tịch nền tảng
5. Nền tri thức dùng chung
6. Bản đồ tri thức và hướng số hoá
7. Khung pháp lý và đạo đức nghề
8. Cách đọc bộ tài liệu này

---

## 1. Tam Thức là gì

Tam Thức (三式) là tên gọi chung cho ba hệ chiêm nghiệm cổ điển bậc cao của truyền thống Đông Á: Đại Lục Nhâm (大六壬), Kỳ Môn Độn Giáp (奇門遁甲), và Thái Ất Thần Số (太乙神數). Trong lịch sử thư tịch, ba môn này được xếp cùng một nhóm vì chúng chia sẻ một cách làm việc: đặt câu hỏi tại một thời điểm cụ thể, lập một "bàn" biểu diễn trạng thái trời đất tại thời điểm đó, rồi đọc bàn theo một hệ quy tắc chặt chẽ để luận cát hung.

Điểm chung khiến ba hệ được gộp thành một chữ "thức" nằm ở chỗ: cả ba đều là hệ tất định. Cùng một thời điểm và cùng một câu hỏi, quy trình lập bàn cho ra đúng một kết quả, không phụ thuộc người bấm. Đây là đặc điểm quan trọng nhất đối với việc số hoá, vì nó nghĩa là toàn bộ khâu lập bàn có thể viết thành thuật toán kiểm chứng được, tách hẳn khỏi khâu diễn giải vốn cần tri thức và ngữ cảnh.

### 1.1 Định nghĩa và tên gọi

Chữ thức (式) ở đây không mang nghĩa "công thức" theo cách hiểu thông thường. Trong ngữ cảnh cổ, 式 chỉ một dụng cụ chiêm nghiệm có bàn xoay, tổ tiên của cả ba hệ. Dụng cụ đó gồm hai lớp: một đĩa tròn tượng trưng cho trời đặt trên một đế vuông tượng trưng cho đất, xoay được để mô phỏng chuyển động của các yếu tố thời gian trên nền không gian cố định. Từ đó, ba hệ dùng chung chữ thức và được gọi là Tam Thức.

- Đại Lục Nhâm (大六壬): Hệ luận nhân sự dựa trên tương tác của mười hai chi trên bàn trời và bàn đất, mười hai thiên tướng, và bốn khoá ba truyền. Tên "lục nhâm" gắn với can Nhâm (壬) thuộc Thủy và cấu trúc sáu mươi hoa giáp. Đây là hệ được dùng nhiều nhất cho câu hỏi cụ thể hằng ngày.
- Kỳ Môn Độn Giáp (奇門遁甲): Hệ luận phương vị và thời cơ hành động, phối chín cung, chín sao, tám môn, tám thần với ba kỳ sáu nghi. Tên gọi phản ánh hai ý: "kỳ môn" là các cửa và kỳ nghi tốt, "độn giáp" là phép giấu can Giáp (甲) vào sáu nghi. Đây là hệ mạnh nhất về chọn hướng và định thời điểm khởi sự.
- Thái Ất Thần Số (太乙神數): Hệ luận vận lớn theo chu kỳ dài, lấy sao Thái Ất (太乙) vận hành qua chín cung làm gốc, phối mười sáu thần, tám tướng, và các thuật toán tích niên. Đây là hệ vĩ mô nhất, hướng tới quốc sự, thời đại, và chu kỳ nhiều năm.

### 1.2 Vì sao gọi là "thức" — cỗ máy bàn xoay của trời đất

Hiểu chữ thức như một cỗ máy giúp nắm ngay bản chất kỹ thuật của cả ba hệ. Một cỗ máy Tam Thức nhận đầu vào là một thời điểm, gồm năm tháng ngày giờ đã qua xử lý lịch pháp, cùng một số tham số câu hỏi. Nó biến đầu vào đó thành một trạng thái bàn có cấu trúc, rồi áp quy tắc để rút ra kết luận. Nhìn theo ngôn ngữ phần mềm, đây chính là một hàm thuần: cùng đầu vào cho cùng đầu ra.

Sự khác biệt giữa ba hệ không nằm ở triết lý nền, vốn chung là âm dương ngũ hành và can chi, mà nằm ở cách mỗi hệ sắp xếp bàn và tập quy tắc đọc bàn. Vì lẽ đó, khi thiết kế phần mềm, phần khó không phải là ba engine riêng biệt hoàn toàn, mà là một lõi chung cõng ba lớp an bàn khác nhau đặt bên trên.

[Hình 1.1] Bốn tầng của một cỗ máy Tam Thức: Lớp lịch pháp và thiên văn (L1) → Lớp can chi và thần sát (L2) → Lớp an bàn, nơi ba hệ rẽ nhánh (L3) → Lớp luận giải chung (L4). Ba hệ khác nhau ở lớp an bàn phía trên nhưng đọc chung một lõi lịch pháp và can chi ở dưới.

### 1.3 Ba hệ trong một truyền thống

Truyền thống thư tịch xưa xếp Tam Thức vào hàng cao trong các thuật số, phân biệt với các môn phổ thông hơn như bói dịch hay tướng số. Lý do là ba hệ này đòi hỏi nền toán lịch và thiên văn thực sự: muốn lập bàn đúng phải tính được tiết khí, phải quy đổi giờ theo mặt trời thật, phải nắm hệ can chi sáu mươi. Chính rào cản kỹ thuật này vừa là lý do ba hệ ít phổ biến, vừa là cơ hội rõ ràng cho phần mềm: máy tính xử lý phần lịch pháp gần như hoàn hảo, gỡ bỏ rào cản lớn nhất giữa người học và ba hệ.

---

## 2. Phân công ba hệ theo tam tài

Cách sắp xếp kinh điển nhất để hiểu quan hệ giữa ba hệ là qua tam tài (三才): Thiên, Địa, Nhân. Mỗi hệ có sở trường ở một tầng, và ba tầng hợp lại phủ gần trọn các loại câu hỏi mà một người hay một tổ chức có thể đặt ra.

[Hình 2.1] Phân công ba hệ theo tam tài: Thái Ất chủ tầng Thiên và câu hỏi vĩ mô, Kỳ Môn chủ tầng Địa và chiến thuật hành động, Lục Nhâm chủ tầng Nhân và sự việc cụ thể.

### 2.1 Thái Ất chủ Thiên — tầng vĩ mô

Thái Ất Thần Số hướng tới những câu hỏi lớn nhất về thời gian và vận hội: chu kỳ của một thời đại, khí số của một quốc gia, xu thế dài hạn vượt khỏi tầm một cá nhân. Đơn vị thời gian mà Thái Ất làm việc thường tính bằng năm, thậm chí bằng nhiều thập niên hay dài hơn, thông qua các thuật toán tích niên cộng dồn số năm từ một mốc khởi nguyên. Với một nền tảng phần mềm, giá trị của Thái Ất nằm ở tầng phân tích chiến lược dài hạn cho tổ chức.

### 2.2 Kỳ Môn chủ Địa — tầng chiến thuật

Kỳ Môn Độn Giáp mạnh nhất ở câu hỏi hành động: nên đi hướng nào, chọn thời điểm nào để khởi sự, bố trí thế trận ra sao để đạt mục tiêu. Cốt lõi của Kỳ Môn là không gian định hướng, chín cung ứng với tám hướng và trung cung, trên đó an chín sao, tám môn, tám thần cùng ba kỳ sáu nghi. Vì gắn chặt với hành động và phương vị, Kỳ Môn có tính ứng dụng tức thời cao.

### 2.3 Lục Nhâm chủ Nhân — tầng nhân sự

Đại Lục Nhâm chuyên về việc người và sự việc cụ thể: một vụ việc sẽ thành hay bại, một chuyến đi thuận hay trắc trở, một quan hệ tiến hay lui. Bàn Lục Nhâm gồm bàn trời và bàn đất mười hai chi lồng nhau, thêm mười hai thiên tướng, rồi rút ra bốn khoá và ba truyền để đọc diễn tiến đầu cuối của sự việc. Chính vì trả lời trực tiếp câu hỏi cụ thể hằng ngày, Lục Nhâm là hệ có lượng câu hỏi tiềm năng lớn nhất và dễ tiếp cận nhất với người dùng phổ thông.

[Hình 2.2] So sánh định tính ba hệ trên sáu trục: quy mô thời gian, độ khó tính toán, chi tiết sự việc, tính chiến thuật, bề dày văn bản, ứng dụng hiện đại.

### 2.4 Ranh giới và vùng chồng lấn

Ba tầng tam tài không phải ba hộp kín. Nhiều câu hỏi thực tế nằm ở vùng giao. Một quyết định kinh doanh lớn có thể vừa cần Thái Ất để đọc bối cảnh thời kỳ, vừa cần Kỳ Môn để chọn thời điểm và hướng, vừa cần Lục Nhâm để lường một thương vụ cụ thể.

Bảng 2.1 — Phân công ba hệ theo loại câu hỏi

| Tiêu chí | Thái Ất | Kỳ Môn | Lục Nhâm |
|---|---|---|---|
| Tầng tam tài | Thiên | Địa | Nhân |
| Câu hỏi điển hình | Vận thời đại, quốc sự | Hướng nào, lúc nào khởi sự | Việc này thành hay bại |
| Đơn vị thời gian | Năm tới nhiều thập niên | Giờ, ngày, thời điểm hành động | Sự việc cụ thể trước mắt |
| Trục cấu trúc chính | Sao Thái Ất qua chín cung | Chín cung tám hướng | Mười hai chi trời đất |
| Sở trường | Bối cảnh vĩ mô | Chọn thời và hướng | Chi tiết một sự việc |

---

## 3. Lịch sử và dòng truyền thừa

### 3.1 Nguồn gốc thức bàn và cỗ máy chiêm nghiệm

Gốc chung của Tam Thức là dụng cụ thức bàn (式盤) thời cổ, loại bàn xoay hai lớp trời tròn đất vuông. Khảo cổ học đã tìm được hiện vật thức bàn và giới nghiên cứu quốc tế xem đây là tổ tiên chung của các hệ chiêm nghiệm dùng bàn. Từ dụng cụ vật lý đó, qua thời gian, các hệ quy tắc đọc bàn được hệ thống hoá và tách thành ba dòng riêng.

### 3.2 Ba hệ hình thành và định hình

Trong ba hệ, Lục Nhâm có lớp văn bản dày và ổn định sớm. Kỳ Môn định hình quanh hệ chín cung và các cách cục, gắn với truyền thống mưu lược và có nhiều dị bản về phép lập cục. Thái Ất có lớp văn bản chuyên sâu hơn về thuật toán tích niên và vận hành sao Thái Ất.

Lưu ý về dị bản: mỗi hệ đều có nhiều trường phái và dị bản quy tắc, nhất là Kỳ Môn với các phép lập cục khác nhau và Thái Ất với hơn một mốc khởi nguyên tích niên. Phần mềm phải chọn và ghi rõ theo trường phái nào, cho phép cấu hình, và tuyệt đối không trộn lẫn quy tắc của các dòng khác nhau trong cùng một lần lập bàn.

### 3.3 Đường vào Việt Nam và truyền thống bản địa

Tam Thức vào Việt Nam theo dòng chảy tri thức Hán học lâu đời và được giới nho sĩ, thầy số bản địa tiếp nhận, sử dụng, và truyền lại. Người Việt tiếp cận ba hệ chủ yếu qua văn bản chữ Hán, đồng thời hình thành lớp thuật ngữ Việt hoá quen thuộc như Lục Nhâm, Kỳ Môn, Thái Ất.

---

## 4. Thư tịch nền tảng

### 4.1 Kinh điển gốc của mỗi hệ

Mi hệ có một số bộ được xem là nền, quanh đó là lớp chú giải nhiều đời. Với Lục Nhâm, đó là các bộ luận về khoá thể, thiên tướng, và phép đoán. Với Kỳ Môn, đó là các bộ về lập cục, cách cục, và dụng thần theo loại việc. Với Thái Ất, đó là các bộ về vận hành sao Thái Ất, mười sáu thần, và thuật tích niên.

### 4.2 Nguồn văn bản số hoá và học thuật

Để số hoá, hai loại nguồn cần song hành. Thứ nhất là kho văn bản cổ đã số hoá, cho phép truy nguyên câu chữ gốc khi xây phần diễn giải và trích dẫn. Thứ hai là nghiên cứu học thuật hiện đại, quan trọng để đặt ba hệ vào khung lịch sử và khoa học đáng tin.

Nguyên tắc trích dẫn và bản quyền: khi xây phần diễn giải dựa trên văn bản cổ, hệ thống trích nguồn rõ ràng và chỉ dùng đoạn ngắn cần thiết, không tái tạo trọn vẹn tác phẩm còn bản quyền.

### 4.3 Thư viện mã nguồn mở để đối chiếu

Mt tài sản quý cho việc lập trình là các thư viện mã nguồn mở đã cài đặt thuật toán lập bàn cho từng hệ. Chúng đóng vai trò bộ đối chiếu: khi engine của ta lập một bàn, ta so kết quả với các thư viện độc lập này trên một tập lớn ca kiểm thử để bắt lỗi.

Bảng 4.1 — Ba nhóm nguồn và vai trò trong hệ thống

| Nhóm nguồn | Nội dung | Vai trò trong hệ thống |
|---|---|---|
| Kinh điển gốc | Bộ nền và chú giải mỗi hệ | Cơ sở cho quy tắc lập bàn và nội dung diễn giải |
| Văn bản số hoá | Kho văn bản cổ đã số hoá | Truy nguyên câu chữ, trích dẫn có nguồn |
| Nghiên cứu học thuật | Công trình lịch sử và thiên văn | Đặt ba hệ vào khung đáng tin, hiệu đính |
| Thư viện mã nguồn mở | Cài đặt lập bàn và lịch pháp | Oracle đối chiếu kết quả, phần lõi lịch |

---

## 5. Nền tri thức dùng chung

Đây là chương bản lề nối phần tổng quan với phần kỹ thuật. Dù ba hệ khác nhau ở cách an bàn, chúng đứng trên cùng một nền lịch pháp và can chi. Nhận ra và tách đúng nền chung này là quyết định kiến trúc quan trọng nhất của cả dự án.

### 5.1 Bốn tầng của một cỗ máy Tam Thức

Mt cỗ máy Tam Thức có thể chia thành bốn tầng xếp chồng:

- L1 — Lịch pháp và thiên văn: từ một mốc thời gian dương lịch, tính ra tiết khí, quy đổi giờ theo mặt trời thật tại kinh độ cụ thể, hiệu chỉnh các sai số thời gian.
- L2 — Can chi và thần sát: từ thời điểm đã chuẩn hoá, lập bốn trụ can chi, xác định tuần không, vượng tướng hưu tù tử, vòng trường sinh.
- L3 — An bàn (ba hệ rẽ nhánh): Lục Nhâm lập bàn trời đất và thiên tướng rồi rút khoá truyền; Kỳ Môn lập địa bàn thiên bàn rồi an sao môn thần theo cục; Thái Ất an sao Thái Ất và các thần tướng theo tích niên.
- L4 — Luận giải: ba hệ lại gần nhau vì cùng dùng ngôn ngữ cát hung, dụng thần, cách cục, sinh khắc ngũ hành.

Hai tầng L1 và L2 hoàn toàn dùng chung cho cả ba hệ.

### 5.2 Vì sao dùng chung một lõi lịch pháp

Có ba lý do khiến việc dùng chung lõi lịch pháp không chỉ tiện mà gần như bắt buộc. Thứ nhất là tính đúng đắn: tính tiết khí và giờ mặt trời thật là phần khó và dễ sai nhất, nên tập trung làm thật kỹ một lần rồi cả ba hệ hưởng lợi. Thứ hai là tính nhất quán: nếu ba hệ dùng ba cách tính lịch khác nhau, cùng một thời điểm có thể cho ra trụ can chi lệch nhau. Thứ ba là chi phí bảo trì: một lõi lịch chung được kiểm thử nghiêm ngặt sẽ rẻ hơn nhiều so với ba bản song song.

Quyết định nền tảng: toàn bộ phần lịch pháp và can chi được gom vào một lõi dùng chung, làm thành tập tài liệu 5 riêng và là hạng mục xây trước tiên trong lộ trình kỹ thuật.

---

## 6. Bản đồ tri thức và hướng số hoá

### 6.1 Từ văn bản cổ tới cấu trúc dữ liệu

Tri thức Tam Thức trong văn bản cổ ở dạng văn xuôi cô đọng, nhiều quy tắc điều kiện, nhiều bảng tra. Để máy dùng được, phải chuyển ba loại tri thức sang ba dạng dữ liệu:

- Bảng tra (tháng tướng, ký cung của can, định cục theo tiết khí) trở thành bảng dữ liệu tra cứu trực tiếp.
- Quy tắc điều kiện (cách xác định quý nhân, cách chọn dụng thần) trở thành logic engine viết bằng mã.
- Nội dung diễn giải (ý nghĩa một cách cục, lời đoán một khoá thể) trở thành cơ sở tri thức có cấu trúc, gắn nguồn.

### 6.2 Ranh giới giữa engine tất định và diễn giải

Đây là ranh giới thiết kế cốt lõi của cả nền tảng. Khâu lập bàn là tất định và phải do engine mã hoá xử lý, cho kết quả đúng và tái lập được, không giao cho mô hình ngôn ngữ tự do sinh ra. Khâu diễn giải cần ngôn ngữ tự nhiên, ngữ cảnh, và tri thức, là nơi mô hình ngôn ngữ hỗ trợ tốt, nhưng luôn dựa trên bàn do engine lập và trên cơ sở tri thức có nguồn, kèm nhãn minh bạch rằng đây là nội dung do AI hỗ trợ tạo.

Nguyên tắc bất di: engine tất định lập bàn, AI hỗ trợ diễn giải. Bàn phải kiểm chứng được từng bước và khớp với các thư viện đối chiếu. Diễn giải phải trích nguồn, không khẳng định chắc chắn quá mức, và luôn gắn nhãn AIDisclosure theo hệ thiết kế CyberSkill.

---

### 6.4 Bảng đối chiếu ba hệ

Bảng sau đặt ba hệ cạnh nhau theo các trục chính, để nắm nhanh điểm giống và khác trước khi vào ba tập chuyên sâu. Ba hệ chung nền can chi và ngũ hành, nhưng khác nhau ở đầu vào, thành phần lập bàn, tầm câu hỏi, và văn bản nền.

| Trục | Đại Lục Nhâm | Kỳ Môn Độn Giáp | Thái Ất Thần Số |
|---|---|---|---|
| Ngôi tam tài | Nhân | Địa | Thiên |
| Đầu vào chính | Giờ hỏi và can chi ngày | Giờ và tiết khí | Năm và tích niên |
| Nền lập bàn | Thiên địa bàn, gia nguyệt tướng | Cửu cung, định cục | Vòng cung, an Thái Ất |
| Thành phần chính | Tứ khoá, tam truyền, thiên tướng | Lục nghi tam kỳ, bát môn, cửu tinh, bát thần | Mười sáu thần, tám tướng, chủ khách toán |
| Tầm câu hỏi | Việc cụ thể, theo giờ | Chọn thời chọn hướng, bố cục | Vĩ mô, chu kỳ dài |
| Cờ trường phái chính | Quý nhân, trường sinh | Định cục, âm dương bàn, loại thời gian | Mốc kỷ nguyên tích niên |
| Văn bản nền | Đại Lục Nhâm đại toàn, Tất pháp phú | Yên Ba Điếu Tẩu ca, Độn Giáp diễn nghĩa | Thái Ất Kim Kính thức kinh, Thái Ất thống tông bảo giám |
| Oracle đối chiếu | kinliuren | kinqimen, china95 | kintaiyi |

Bảng này là bản đồ nhanh cho cả bộ. Điểm chung ở dòng nền: cả ba đứng trên can chi và ngũ hành ở tập 5. Điểm khác ở đầu vào và tầm: Lục Nhâm và Kỳ Môn lấy giờ nên hợp câu hỏi cụ thể, Thái Ất lấy năm nên hợp câu hỏi vĩ mô. Mỗi hệ có cờ trường phái riêng cần đóng dấu vào lá số, và có oracle riêng để kiểm engine. Ba tập chuyên sâu tiếp theo khai triển từng cột của bảng này.


## 7. Khung pháp lý và đạo đức nghề

Mt sản phẩm chạm tới chiêm nghiệm và tư vấn cần đặt nền pháp lý và đạo đức ngay từ đầu. Về pháp lý tại Việt Nam, hoạt động liên quan tới chiêm nghiệm chịu sự điều chỉnh của pháp luật và cần được định vị đúng: sản phẩm hướng tới giáo dục di sản, tra cứu tri thức, và hỗ trợ ra quyết định có tính tham khảo, không cổ vũ mê tín hay hứa hẹn kết quả. Về bảo vệ dữ liệu, câu hỏi chiêm nghiệm của người dùng là dữ liệu cá nhân nhạy cảm, nên hệ thống áp chuẩn bảo vệ dữ liệu chặt chẽ.

Ranh giới nội dung bắt buộc: sản phẩm không đưa ra lời khuyên y tế, pháp lý, hay tài chính núp dưới hình thức chiêm nghiệm, và luôn nói rõ tính chất tham khảo của diễn giải. Với người dùng ở trạng thái dễ tổn thương, hệ thống ưu tiên an toàn và hướng tới nguồn trợ giúp phù hợp thay vì phán quyết.

Về đạo đức nghề, tinh thần bốn trục giọng nói của CyberSkill dẫn đường: warm là tôn trọng và đồng cảm với người hỏi, direct là nói thẳng và rõ, honest là không thổi phồng và không giả vờ chắc chắn, respectful là tôn trọng cả người dùng lẫn di sản tri thức.

---

## 8. Cách đọc bộ tài liệu này

Bộ tài liệu gồm bảy tập, chia hai khối. Khối nội dung hệ gồm tập 1 tổng quan này, và ba tập chuyên sâu 2, 3, 4 lần lượt cho Lục Nhâm, Kỳ Môn, Thái Ất. Khối nền tảng và sản phẩm gồm tập 5 lõi lịch pháp và can chi dùng chung, tập 6 kiến trúc kỹ thuật và kế hoạch số hoá, tập 7 sản phẩm, ứng dụng tư vấn chiến lược, đào tạo, và lộ trình.

Bảng 8.1 — Bảy tập và cách dùng theo vai trò

| Tập | Tiêu đề | Dành cho ai đọc trước |
|---|---|---|
| 1 | Tổng quan Tam Thức và phân công ba hệ | Tất cả các vai trò |
| 2 | Đại Lục Nhâm chuyên sâu | Kỹ sư engine, người học Lục Nhâm |
| 3 | Kỳ Môn Độn Giáp chuyên sâu | Kỹ sư engine, người học Kỳ Môn |
| 4 | Thái Ất Thần Số chuyên sâu | Kỹ sư engine, người học Thái Ất |
| 5 | Nền dùng chung — lịch pháp và can chi | Kỹ sư lõi, cần xây trước tiên |
| 6 | Kiến trúc kỹ thuật và kế hoạch số hoá | Kiến trúc sư, kỹ sư tri thức |
| 7 | Sản phẩm, tư vấn, đào tạo, lộ trình | Đội sản phẩm và kinh doanh |

Gợi ý thứ tự đọc theo vai trò:

- Kỹ sư lõi: tập 1 → tập 5 → tập 6.
- Kỹ sư engine một hệ: tập 1 → tập 5 → tập chuyên sâu của hệ đó.
- Đội sản phẩm và kinh doanh: tập 1 → tập 7.
- Người học và nghiên cứu: tập 1 → tập chuyên sâu quan tâm, quay lại tập 5 khi cần.

Về thứ tự xây dựng, lõi lịch pháp ở tập 5 làm trước, vì cả ba hệ đứng trên nó và sai số ở đây lan lên tất cả. Sau lõi, Lục Nhâm là ứng viên hợp lý cho engine hệ đầu tiên nhờ nhu cầu rộng và mỗi lần dùng khép kín.

---

Khép lại tập 1: Tam Thức là ba hệ chiêm nghiệm tất định đứng chung một nền lịch pháp và can chi, chia việc theo tam tài Thiên Địa Nhân. Nhận ra nền chung đó và tách đúng ranh giới giữa engine tất định và diễn giải là hai quyết định định hình cả nền tảng.

Hiện Thực Hoá Ý Chí.

---

*Tài liệu 1/7 trong bộ Tam Thức của CyberSkill. Phiên bản 1.0. Các giá trị thiết kế theo CyberSkill Global Design System v1.3.0.*
