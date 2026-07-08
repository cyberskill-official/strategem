# Tài liệu 5 — Nền tảng dùng chung

> Bộ tài liệu Tam Thức (三式) của CyberSkill — Tập 5/7
> Phiên bản 1.0 · Slogan: "Turn Your Will Into Real" — Hiện Thực Hoá Ý Chí
> Nội dung mang tính tham khảo tri thức và giáo dục di sản, không phải lời khuyên y tế, pháp lý, hay tài chính.

Tài liệu này đặc tả lõi lịch pháp và thiên văn mà cả ba hệ Tam Thức đều gọi tới. Đây là tập nhiều thuật toán dùng lại nhất: tính hai bốn tiết khí từ kinh độ mặt trời, đổi giờ đồng hồ sang chân thái dương thời, dựng bốn trụ can chi, và các bảng độn can, tuần không, vượng suy. Ba engine chuyên sâu ở tập 2, 3, 4 đều xây trên lõi này.

## Thông tin tài liệu

| Trường | Nội dung |
|---|---|
| Vai trò | Lõi lịch pháp và thiên văn dùng chung cho Lục Nhâm, Kỳ Môn, Thái Ất |
| Thành phần | Tiết khí, chân thái dương thời, bốn trụ can chi, độn can, tuần không, vượng suy |
| Độ chính xác | Mốc tiết khí sai số dưới một phút; giờ chân thái dương sai số dưới một phút |
| Thư viện tham chiếu | Thuật toán Meeus và VSOP87 rút gọn; đối chiếu sxwnl và tyme4py |
| Nguyên tắc | Mọi khác biệt trường phái để thành cờ; mỗi lá số đóng dấu cấu hình lịch pháp đã dùng |

## Mục lục

1. Vì sao cần một lõi lịch pháp chung
2. Hai bốn tiết khí từ kinh độ mặt trời
3. Chân thái dương thời
4. Bốn trụ can chi
5. Tuần không, vượng suy, và trường sinh
6. Đặc tả module lịch pháp và cấu hình

---

## 1. Vì sao cần một lõi lịch pháp chung

### 1.1 Ba hệ chung một nền thời gian

Ba hệ Tam Thức khác nhau ở cách lập bàn và cách luận, nhưng chung một nền thời gian. Cả ba đều cần biết can chi của thời điểm, đều cần biết đang ở tiết khí nào, và với các phép theo giờ, đều cần giờ chính xác theo mặt trời thật. Nếu mỗi hệ tự tính lịch riêng, sẽ có ba bản dễ lệch nhau và khó bảo trì. Vì vậy thiết kế đúng là tách lõi lịch pháp thành một module chung, ba engine gọi vào.

Lõi này trả lời bốn câu hỏi nền. Thời điểm này rơi vào tiết khí nào và tam nguyên nào. Bốn trụ can chi của năm tháng ngày giờ là gì. Giờ theo mặt trời thật, sau khi hiệu chỉnh kinh độ và phương trình thời gian, là mấy giờ. Và các trạng thái phái sinh như tuần không, vượng suy, trường sinh của can chi là gì. Bốn nhóm này đủ cho cả ba hệ dựng bàn.

### 1.2 Những chỗ trường phái khác nhau

Ngay ở lõi lịch pháp cũng có chỗ các phái làm khác nhau, và phải để thành cờ. Có nên dùng chân thái dương thời hay dùng giờ đồng hồ, và lấy kinh độ nào. Ranh giới giờ Tý đặt ở hai ba giờ hay nửa đêm, và xử lý dạ Tý ra sao. Trường sinh mười hai cung theo phái âm dương thuận nghịch hay phái ngũ hành cùng sinh. Những khác biệt này nhỏ nhưng đổi kết quả, nên engine không được chọn cứng, mà cho cấu hình và ghi rõ vào lá số.

Vì ba engine cùng gọi lõi này, một lỗi ở đây lan ra cả ba hệ cùng lúc. Một mốc tiết khí lệch một ngày sẽ làm sai định cục Kỳ Môn, sai nguyệt tướng Lục Nhâm, và sai độn của Thái Ất. Một ranh giới giờ Tý sai sẽ đổi giờ chiêm của cả ba. Vì vậy lõi lịch pháp cần độ chính xác cao nhất, bộ kiểm thử dày nhất, và phải đối chiếu với nhiều nguồn thiên văn độc lập.

### 1.3 Thư viện tham chiếu và độ chính xác

Về thuật toán, tài liệu này dùng phương pháp của Jean Meeus trong Astronomical Algorithms cho kinh độ mặt trời và tiết khí, đủ chính xác tới cỡ giây tới một phút. Muốn chính xác hơn thì dùng chuỗi VSOP87 đầy đủ, đạt dưới một giây cung. Về thư viện đối chiếu, sxwnl tức Thọ Tinh Thiên Văn Lịch của Hứa Kiếm Vĩ dùng VSOP87 rút gọn và là chuẩn thực tế cho tiết khí; tyme4py nhập thuật toán tiết khí từ đó. Engine của ta đối chiếu mốc tiết khí và bốn trụ với các thư viện này trên tập nhiều năm.

---

## 2. Hai bốn tiết khí từ kinh độ mặt trời

### 2.1 Tiết khí là các mốc kinh độ mặt trời

Hai bốn tiết khí không phải các mốc chia đều theo ngày, mà chia đều theo kinh độ biểu kiến của mặt trời trên hoàng đạo. Mỗi tiết cách nhau mười lăm độ. Xuân Phân ở không độ, Thanh Minh mười lăm độ, cứ thế tới Đông Chí hai trăm bảy mươi độ, và Kinh Trập ba trăm bốn mươi lăm độ. Vì mặt trời đi không đều trên hoàng đạo, khoảng cách ngày giữa các tiết hơi khác nhau, nên phải tính theo kinh độ chứ không đếm ngày.

Hai bốn mốc chia làm hai loại xen kẽ, và sự phân biệt này quan trọng cho các hệ. Mười hai tiết (節) ở các mốc lẻ điều khiển ranh giới trụ tháng: tháng Dần bắt đầu ở Lập Xuân, và tương tự. Mười hai trung khí (中氣) ở các mốc chẵn điều khiển việc đổi nguyệt tướng trong Lục Nhâm. Engine cần phân biệt rõ hai loại này khi tính trụ tháng và nguyệt tướng.

### 2.2 Thuật toán Meeus tính kinh độ mặt trời

Kinh độ biểu kiến của mặt trời tính theo phương pháp Meeus gồm mấy bước. Trước hết đổi thời điểm sang thế kỷ Julian tính từ mốc J2000. Rồi tính kinh độ trung bình và cận điểm trung bình của mặt trời theo đa thức bậc thấp. Rồi cộng phương trình tâm sai để ra kinh độ thực, và cuối cùng hiệu chỉnh chương động và quang sai để ra kinh độ biểu kiến. Các hệ số cụ thể lấy từ chương hai lăm và hai bảy của Astronomical Algorithms.

```
# jde = ngay Julian theo thoi gian dong luc (TT)
def kinh_do_mat_troi(jde):
    T  = (jde - 2451545.0) / 36525.0
    L0 = (280.46646 + 36000.76983*T + 0.0003032*T*T) % 360   # kinh do trung binh
    M  = 357.52911 + 35999.05029*T - 0.0001537*T*T           # can diem trung binh
    Mr = radians(M)
    C  = ((1.914602 - 0.004817*T - 0.000014*T*T)*sin(Mr)
        + (0.019993 - 0.000101*T)*sin(2*Mr)
        + 0.000289*sin(3*Mr))                                # phuong trinh tam sai
    theta = L0 + C
    omega = radians(125.04 - 1934.136*T)
    lam = theta - 0.00569 - 0.00478*sin(omega)               # kinh do bieu kien
    return lam % 360
```

### 2.3 Nghịch đảo tìm thời điểm tiết khí và hiệu chỉnh delta T

Để tìm thời điểm bắt đầu một tiết khí, ta cần bài toán ngược: biết kinh độ mục tiêu, tìm thời điểm mà kinh độ mặt trời bằng đúng giá trị đó. Cách làm là lấy một giá trị khởi đầu từ đa thức điểm phân điểm chí của Meeus chương hai bảy, rồi lặp Newton hoặc cát tuyến: mỗi vòng cộng vào thời điểm một lượng tỉ lệ với sai lệch kinh độ còn lại. Ba đến năm vòng là hội tụ tới dưới một giây.

Thuật toán Meeus chạy trên thời gian động lực, còn giờ dân dụng là giờ thế giới, hai thang lệch nhau một lượng gọi là delta T. Phải cộng hiệu chỉnh này, nếu không mốc tiết khí có thể lệch tới vài phút, đủ để đẩy một tiết qua ranh giới ngày trong ca biên. Dùng đa thức Espenak và Meeus của NASA: cho giai đoạn hai nghìn linh năm tới hai nghìn không trăm năm mươi, delta T bằng sáu hai phẩy chín hai cộng không phẩy ba hai lần t cộng không phẩy không không năm năm chín lần t bình phương, với t là năm trừ hai nghìn. Delta T khoảng sáu bảy giây năm hai nghìn mười, chín ba giây năm hai nghìn năm mươi, và tăng theo thời gian.

Về độ chính xác, phương pháp Meeus bậc thấp cho mốc tiết khí đúng tới cỡ giây tới một phút, đủ dùng cho lập bàn. Muốn chuẩn hơn thì dùng VSOP87 đầy đủ. Điểm cần nhớ khi lập trình là luôn tách bạch thời gian động lực và giờ dân dụng, cộng delta T đúng chiều, và dùng đa thức delta T phù hợp với thời đại cho các năm rất xa quá khứ hay tương lai.

---

## 3. Chân thái dương thời

### 3.1 Ba thành phần của giờ mặt trời thật

Chân thái dương thời (真太陽時) là giờ theo vị trí thật của mặt trời tại nơi quan sát, khác giờ đồng hồ vốn là giờ trung bình theo múi. Ba hệ Tam Thức khi lập bàn theo giờ cần giờ mặt trời thật, vì ranh giới giờ trong tử vi phương Đông đặt theo mặt trời chứ không theo đồng hồ. Giờ mặt trời thật bằng giờ đồng hồ trừ hiệu chỉnh kinh độ cộng phương trình thời gian.

### 3.2 Phương trình thời gian

Phương trình thời gian (均時差) là chênh lệch giữa giờ mặt trời thật và giờ mặt trời trung bình, sinh ra do quỹ đạo trái đất hình elip và do trục nghiêng. Nó biến thiên trong năm, có hai cực trị. Công thức đơn giản của Meeus cho phương trình thời gian theo ngày trong năm là một tổ hợp các hàm sin và cos của góc ngày. Công thức chính xác hơn dùng độ lệch tâm và độ nghiêng hoàng đạo. Hai cực trị rơi vào khoảng cộng mười bốn phút hai mươi hai giây ngày mười một tháng hai, và trừ mười sáu phút hai mươi ba giây ngày bốn tháng mười một.

### 3.3 Hiệu chỉnh kinh độ cho Việt Nam

Hiệu chỉnh kinh độ bù cho việc một múi giờ trải trên nhiều kinh độ nhưng dùng chung một giờ chuẩn theo kinh tuyến giữa múi. Cứ lệch một độ kinh so với kinh tuyến chuẩn thì giờ mặt trời lệch bốn phút. Việt Nam ở múi giờ cộng bảy, kinh tuyến chuẩn là một trăm linh năm độ Đông. Công thức hiệu chỉnh là bốn nhân với hiệu giữa kinh độ nơi quan sát và một trăm linh năm, tính bằng phút.

Thành phố Hồ Chí Minh ở một trăm linh sáu phẩy bảy độ Đông, nên cộng khoảng sáu phẩy tám phút; Hà Nội ở một trăm linh năm phẩy tám lăm độ, cộng khoảng ba phẩy bốn phút. Cộng thêm phương trình thời gian tới cỡ mười sáu phút, tổng lệch có thể tới hơn hai mươi phút. Gần ranh giới một giờ, lệch chừng ấy đủ đẩy thời điểm sang giờ kế, đổi giờ chiêm của Lục Nhâm, đổi thời can thời chi cho trực phù trực sử Kỳ Môn, đổi thời kế Thái Ất. Vì các phái khác nhau, để thành cờ dùng chân thái dương thời và cờ kinh độ.

---

## 4. Bốn trụ can chi

Bốn trụ can chi (四柱干支) của năm, tháng, ngày, giờ là dữ kiện lịch nền cho cả ba hệ. Mỗi trụ gồm một thiên can và một địa chi. Bốn trụ tính theo bốn quy tắc riêng, mỗi quy tắc có ranh giới và bảng độn riêng. Đây là phần dễ sai nhất ở lõi lịch pháp, nên tài liệu trình bày từng trụ với luật rõ ràng.

### 4.1 Trụ năm và ranh giới Lập Xuân

Trụ năm đổi tại Lập Xuân, tức khi mặt trời tới ba trăm mười lăm độ, không phải Tết âm lịch cũng không phải ngày một tháng một dương lịch. Đây là điểm hay nhầm. Can của năm bằng năm dương lịch trừ bốn rồi chia lấy dư cho mười; chi bằng năm trừ bốn chia lấy dư cho mười hai. Mốc là năm một nghìn chín trăm tám mươi bốn là năm Giáp Tý. Với thời điểm trước Lập Xuân trong năm dương lịch, phải lùi về can chi của năm trước.

### 4.2 Trụ tháng và Ngũ Hổ Độn

Trụ tháng có chi cố định theo tháng âm dương: tháng Dần là tháng giêng bắt đầu từ Lập Xuân, tháng Mão từ Kinh Trập, và tương tự theo mười hai tiết. Ranh giới tháng theo tiết chứ không theo trung khí. Can của tháng suy từ can của năm bằng phép Ngũ Hổ Độn (五虎遁), đặt tên vì tháng Dần cầm tinh con hổ.

Ca quyết: Giáp Kỷ chi niên Bính tác thủ, Ất Canh chi tuế Mậu vi đầu, Bính Tân tất định tầm Canh khởi, Đinh Nhâm Nhâm vị thuận hành lưu, Mậu Quý hà phương phát, Giáp Dần chi thượng hảo truy cầu.

| Can năm | Can tháng Dần (giêng) |
|---|---|
| 甲 hoặc 己 | 丙寅 Bính Dần |
| 乙 hoặc 庚 | 戊寅 Mậu Dần |
| 丙 hoặc 辛 | 庚寅 Canh Dần |
| 丁 hoặc 壬 | 壬寅 Nhâm Dần |
| 戊 hoặc 癸 | 甲寅 Giáp Dần |

### 4.3 Trụ ngày theo số ngày Julian

Trụ ngày không có ranh giới tiết khí mà đếm liên tục. Can chi ngày bằng số ngày Julian cộng một hằng số bù rồi chia lấy dư cho sáu mươi. Cách này coi chuỗi ngày can chi là một chu kỳ sáu mươi chạy mãi không đứt từ thời cổ. Cần một mốc neo: ngày Julian hai triệu bốn trăm năm mươi mốt nghìn năm trăm bốn mươi lăm, tức trưa ngày một tháng một năm hai nghìn theo thời gian động lực, là ngày Mậu Ngọ. Dạng thực dụng lấy số ngày Julian trừ mười rồi chia lấy dư cho sáu mươi, với không là Giáp Tý, và kiểm lại với một mốc đã biết như ngày một tháng mười năm một chín bốn chín là ngày Giáp Tý.

### 4.4 Trụ giờ, Ngũ Thử Độn, và ranh giới giờ Tý

Trụ giờ có chi theo giờ chân thái dương: giờ Tý từ hai ba giờ tới một giờ, giờ Sửu từ một tới ba giờ, và tương tự. Can của giờ suy từ can của ngày bằng phép Ngũ Thử Độn (五鼠遁), đặt tên vì giờ Tý cầm tinh con chuột.

Ca quyết: Giáp Kỷ hoàn gia Giáp, Ất Canh Bính tác sơ, Bính Tân tòng Mậu khởi, Đinh Nhâm Canh Tý cư, Mậu Quý hà phương phát, Nhâm Tý thị chân đồ.

| Can ngày | Can giờ Tý |
|---|---|
| 甲 hoặc 己 | 甲子 Giáp Tý |
| 乙 hoặc 庚 | 丙子 Bính Tý |
| 丙 hoặc 辛 | 戊子 Mậu Tý |
| 丁 hoặc 壬 | 庚子 Canh Tý |
| 戊 hoặc 癸 | 壬子 Nhâm Tý |

Giờ Tý trải từ hai ba giờ tới một giờ, vắt qua nửa đêm, nên sinh vấn đề chuyển ngày. Lịch cổ điển bắt đầu ngày mới lúc hai ba giờ, tức Tý sơ, nên hai ba giờ ba mươi đã dùng trụ ngày của ngày hôm sau. Các phái Bát Tự khác nhau: phái tảo Tý thời chuyển ngày ngay tại hai ba giờ, phái dạ Tý thời giữ ngày cũ nhưng dùng can giờ theo ngày kế. Engine để cờ zi_hour_day_rollover chọn mốc hai ba giờ hay nửa đêm, và cờ late_zi_handling cho cách xử lý dạ Tý.

---

## 5. Tuần không, vượng suy, và trường sinh

Ba nhóm trạng thái phái sinh từ can chi mà cả ba hệ đều dùng khi luận: tuần không đánh dấu chi rỗng, vượng suy đánh giá sức của ngũ hành theo mùa, và trường sinh mười hai cung đánh giá pha sinh vượng của can. Cả ba đều là bảng tra từ can chi, số hoá thành dữ liệu.

### 5.1 Tuần không

Tuần không (旬空), còn gọi không vong, đánh dấu hai chi bị rỗng trong mỗi tuần giáp. Vì mười can ghép mười hai chi, mỗi tuần mười cặp còn thừa hai chi không có can, đó là hai chi tuần không. Cách tính: từ một cặp can chi, số tuần bằng hiệu giữa thứ tự can và thứ tự chi chia lấy dư cho mười; từ đó ra tuần thủ là ngày Giáp, và hai chi ngoài mười cặp của tuần đó là tuần không.

| Tuần | Tuần không | Tuần | Tuần không |
|---|---|---|---|
| 甲子 Giáp Tý tuần | 戌 亥 Tuất Hợi | 甲午 Giáp Ngọ tuần | 辰 巳 Thìn Tỵ |
| 甲戌 Giáp Tuất tuần | 申 酉 Thân Dậu | 甲辰 Giáp Thìn tuần | 寅 卯 Dần Mão |
| 甲申 Giáp Thân tuần | 午 未 Ngọ Mùi | 甲寅 Giáp Dần tuần | 子 丑 Tý Sửu |

### 5.2 Vượng tướng hưu tù tử

Vượng tướng hưu tù tử (旺相休囚死) đánh giá sức của một hành theo mùa. Quy tắc: hành cùng mùa là vượng; hành được mùa sinh ra là tướng; hành sinh ra mùa là hưu; hành khắc mùa là tù; hành bị mùa khắc là tử. Bảng dưới cho năm trạng thái theo bốn mùa và tháng cuối mùa thuộc thổ.

| Mùa (hành) | Vượng | Tướng | Hưu | Tù | Tử |
|---|---|---|---|---|---|
| Xuân (Mộc) | 木 | 火 | 水 | 金 | 土 |
| Hạ (Hỏa) | 火 | 土 | 木 | 水 | 金 |
| Thu (Kim) | 金 | 水 | 土 | 火 | 木 |
| Đông (Thủy) | 水 | 木 | 金 | 土 | 火 |
| Tứ quý (Thổ) | 土 | 金 | 火 | 木 | 水 |

### 5.3 Trường sinh mười hai cung

Trường sinh mười hai cung (長生十二宮) mô tả pha sinh vượng suy tử của một thiên can qua mười hai chi, gồm trường sinh, mộc dục, quan đới, lâm quan, đế vượng, suy, bệnh, tử, mộ, tuyệt, thai, dưỡng. Can dương đi thuận, can âm đi nghịch. Điểm khởi trường sinh của mỗi can khác nhau: Giáp khởi ở Hợi đi thuận, Ất khởi ở Ngọ đi nghịch, Bính và Mậu khởi ở Dần, Đinh và Kỷ khởi ở Dậu, Canh khởi ở Tỵ, Tân khởi ở Tý, Nhâm khởi ở Thân, Quý khởi ở Mão.

Có hai phái tính trường sinh. Phái âm dương thuận nghịch như trên, mỗi can một điểm khởi. Phái ngũ hành cùng sinh tử gộp can theo hành, thủy và thổ cùng cung. Lục Nhâm thường dùng ngũ hành trường sinh, tức Mộc sinh ở Hợi, Hỏa sinh ở Dần, Kim sinh ở Tỵ, Thủy và Thổ sinh ở Thân. Vì hai phái cho kết quả khác nhau, engine để một cờ chọn phái, và mỗi hệ khai báo phái mặc định của mình.

---

## 6. Đặc tả module lịch pháp và cấu hình

### 6.1 Giao diện module

Module nhận thời điểm dương lịch, kinh độ nơi quan sát, và tập cờ lịch pháp. Nó trả về: bốn trụ can chi; tiết khí và tam nguyên hiện hành cùng thời điểm bắt đầu tiết; giờ chân thái dương đã hiệu chỉnh; và các trạng thái phái sinh gồm tuần không, vượng suy, trường sinh khi được yêu cầu. Ba engine Lục Nhâm, Kỳ Môn, Thái Ất đều lấy đầu vào từ đối tượng này, không tự tính lịch riêng.

```json
{
  "dau_vao": {
    "datetime": "2004-01-01T10:30:00",
    "tz": "+07:00", "kinh_do": 106.7
  },
  "chan_thai_duong": {
    "ap_dung": true,
    "hieu_chinh_kinh_do_phut": 6.8,
    "phuong_trinh_thoi_gian_phut": -3.5,
    "gio_that": "2004-01-01T10:33:18"
  },
  "tu_tru": {
    "nam":"癸未", "thang":"甲子",
    "ngay":"...", "gio":"..."
  },
  "tiet_khi": {
    "hien_hanh":"冬至",
    "bat_dau":"2003-12-22T...",
    "tam_nguyen":"..."
  },
  "phai_sinh": {
    "tuan_khong":["申","酉"],
    "vuong_suy":"..."
  },
  "co_lich_phap": {
    "use_true_solar_time": true,
    "longitude": 106.7,
    "zi_hour_day_rollover": "23:00",
    "late_zi_handling": "...",
    "truong_sinh_phai": "ngu_hanh",
    "delta_t_model": "espenak_meeus"
  }
}
```

### 6.2 Tập cờ lịch pháp

Lõi lịch pháp có tập cờ riêng, tách với cờ trường phái của từng hệ. Các cờ chính: use_true_solar_time bật tắt chân thái dương thời; longitude cho kinh độ hiệu chỉnh; zi_hour_day_rollover chọn mốc chuyển ngày; late_zi_handling xử lý dạ Tý; truong_sinh_phai chọn phái trường sinh; delta_t_model chọn mô hình delta T. Mỗi lá số của mọi hệ đóng dấu cả tập cờ lịch pháp này, vì nó ảnh hưởng tận gốc đầu vào.

| Cờ | Giá trị | Mặc định |
|---|---|---|
| use_true_solar_time | true, false | true |
| longitude | kinh độ thập phân | theo nơi |
| zi_hour_day_rollover | 23:00, 00:00 | 23:00 |
| late_zi_handling | tao_zi, da_zi | tao_zi |
| truong_sinh_phai | am_duong, ngu_hanh | theo hệ |
| delta_t_model | espenak_meeus, khác | espenak_meeus |

Tiêu chí nghiệm thu lõi lịch pháp. Lõi đạt yêu cầu khi mốc hai bốn tiết khí khớp thư viện sxwnl trong sai số một phút trên tập nhiều thập niên, khi bốn trụ can chi khớp tyme4py trên tập ngày dài gồm các ca biên quanh Lập Xuân và quanh nửa đêm, khi giờ chân thái dương khớp tính tay tại các mốc cực trị phương trình thời gian, và khi các bảng tuần không vượng suy trường sinh khớp tra thủ công cho từng phái. Vì lõi này nuôi cả ba hệ, bộ kiểm thử của nó phải là dày nhất trong dự án.

---

Nền tảng dùng chung là lõi kỹ thuật đỡ cả ba hệ Tam Thức: hai bốn tiết khí tính từ kinh độ mặt trời theo Meeus và VSOP87, chân thái dương thời với phương trình thời gian và hiệu chỉnh kinh độ, bốn trụ can chi với các phép độn và ranh giới, cùng tuần không vượng suy trường sinh. Vì mọi engine đều gọi lõi này, nó cần độ chính xác cao nhất và kiểm thử dày nhất, và mọi khác biệt phái đều để thành cờ đóng dấu vào lá số. Tập 6 chuyển sang kiến trúc kỹ thuật của cả nền tảng: engine, knowledge graph, tầng RAG và LLM, và lộ trình số hoá. Hiện Thực Hoá Ý Chí.

> Tài liệu 5/7 trong bộ Tam Thức của CyberSkill. Phiên bản 1.0. Nội dung mang tính tham khảo tri thức và giáo dục di sản, không phải lời khuyên y tế, pháp lý, hay tài chính. Các thuật toán thiên văn và bảng lịch pháp cần đối chiếu ít nhất hai thư viện độc lập, kiểm kỹ ca biên tiết khí và ranh giới giờ, trước khi khoá vào bản phát hành. Các giá trị thiết kế theo CyberSkill Global Design System v1.3.0.
