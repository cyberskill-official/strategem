# Tài liệu 3 — Kỳ Môn Độn Giáp chuyên sâu

> Bộ tài liệu Tam Thức (三式) của CyberSkill — Tập 3/7
> Phiên bản 1.0 · Slogan: "Turn Your Will Into Real" — Hiện Thực Hoá Ý Chí
> Nội dung mang tính tham khảo tri thức và giáo dục di sản, không phải lời khuyên y tế, pháp lý, hay tài chính.

Tài liệu này đặc tả hệ Kỳ Môn Độn Giáp (奇門遁甲) ở mức đủ để lập trình một engine lập bàn và để một người học nắm quy trình. Kỳ Môn là hệ phức tạp và nhiều trường phái nhất trong ba hệ Tam Thức, nên điểm nhấn xuyên suốt là cấu hình bằng cờ trường phái chứ không hardcode, và đóng dấu tập cờ vào mọi lá số.

## Thông tin tài liệu

| Trường | Nội dung |
|---|---|
| Hệ | Kỳ Môn Độn Giáp (奇門遁甲) — chủ Địa, luận phương vị và thời cơ |
| Vai trò kỹ thuật | Engine hệ thứ hai, nhiều dị bản nhất, cần tập cờ đầy đủ |
| Đầu vào engine | Thời điểm đã chuẩn hoá, tiết khí và tam nguyên từ lõi lịch pháp, tập cờ trường phái |
| Đầu ra engine | Lá số bốn bàn dạng JSON: địa bàn, thiên bàn, nhân bàn, thần bàn, trực phù trực sử, cách cục |
| Oracle đối chiếu | Thư viện mã nguồn mở kinqimen, kiểm cho từng tổ hợp cờ trường phái |

## Mục lục

1. Tổng quan hệ Kỳ Môn và luồng lập bàn
2. Bốn bàn và các thành phần
3. Định cục
4. Bố địa bàn
5. Trực phù, trực sử, và bốn bàn
6. Âm bàn và dương bàn
7. Cách cục và dụng thần
8. Đặc tả engine và schema JSON

---

## 1. Tổng quan hệ Kỳ Môn và luồng lập bàn

### 1.1 Kỳ Môn giải quyết bài toán gì

Kỳ Môn Độn Giáp trả lời câu hỏi về phương vị và thời cơ: nên đi hướng nào, làm việc gì vào lúc nào, bố trí thế nào để thuận lợi. Trong ba hệ Tam Thức, Kỳ Môn chủ Địa, mạnh về không gian và chiến lược hành động, nên xưa dùng nhiều trong quân sự và ngày nay dùng cho quyết định kinh doanh, chọn hướng, chọn thời điểm.

Tên gọi gồm ba phần. Kỳ (奇) là ba kỳ Ất Bính Đinh. Môn (門) là tám cửa. Độn Giáp (遁甲) là phép giấu can Giáp, coi Giáp là nguyên soái quý nên ẩn dưới sáu nghi. Ghép lại, Kỳ Môn Độn Giáp là hệ dùng ba kỳ, tám cửa, và phép giấu Giáp để đọc thế cục không gian và thời gian.

### 1.2 Vì sao Kỳ Môn nhiều trường phái

Kỳ Môn là hệ nhiều dị bản nhất trong ba hệ, và đây là điều engine phải xử lý ngay từ thiết kế. Các phái khác nhau ở nhiều chỗ: cách định cục qua siêu thần tiếp khí, cách xoay thiên bàn theo chuyển bàn hay phi bàn, và cả dòng lớn dương bàn với âm bàn khác nhau từ triết lý. Vì vậy nguyên tắc thiết kế xuyên suốt tài liệu này là không hardcode một cách rồi coi là chuẩn duy nhất, mà cho cấu hình bằng cờ, và mỗi lá số xuất ra phải đóng dấu tập cờ đã dùng.

### 1.3 Thư tịch nền và thư viện đối chiếu

Về thư tịch, bài ca nền tảng nhất là Yên Ba Điếu Tẩu Ca (煙波釣叟歌), tóm tắt toàn bộ phép Kỳ Môn thời gia trong một bài ca dài, được coi là chuẩn nhập môn. Các bộ quan trọng khác gồm Kỳ Môn Độn Giáp bí kíp đại toàn, Ngự định Kỳ Môn bảo giám, và nhiều bản chú giải bài ca Yên Ba. Về thư viện mã nguồn mở làm oracle, quan trọng nhất là kinqimen, một package Python lập lá số Kỳ Môn, dùng để đối chiếu kết quả engine trên tập lớn ca mẫu, kiểm cho từng tổ hợp cờ trường phái.

---

## 2. Bốn bàn và các thành phần

### 2.1 Cấu trúc bốn tầng trên chín cung

Bàn Kỳ Môn là bốn tầng chồng lên nhau trên nền chín cung Lạc Thư. Từ dưới lên: địa bàn giữ lục nghi tam kỳ cố định theo cục; thiên bàn mang cửu tinh và can bay theo trực phù; nhân bàn là bát môn, tám cửa; thần bàn là bát thần. Đọc một cung là đọc cả bốn tầng của cung đó cùng lúc, rồi xét quan hệ giữa các tầng và giữa các cung.

Chín cung xếp theo ma phương Lạc Thư hậu thiên, các số từ một đến chín. Tám cung ngoài ứng tám quẻ và tám hướng; trung cung số năm ở giữa. Trong cài đặt, bàn là một mảng chín cung, mỗi cung là một bản ghi bốn tầng. Trung cung có quy ước riêng: sao và can ở trung cung thường ký sang cung Khôn số hai khi luận.

### 2.2 Tam kỳ và lục nghi

Mười thiên can trong Kỳ Môn chia hai nhóm. Tam kỳ (三奇) là ba can quý: Ất là nhật kỳ, Bính là nguyệt kỳ, Đinh là tinh kỳ. Lục nghi (六儀) là sáu can còn lại Mậu Kỷ Canh Tân Nhâm Quý, mỗi nghi ẩn một Giáp theo tuần. Sáu nghi thay cho sáu tuần giáp trong bố cục, vì Giáp được giấu đi theo phép độn giáp.

### 2.3 Cửu tinh, bát môn, bát thần

Ba tầng động phủ lên địa bàn. Cửu tinh (九星) là chín sao thiên bàn: Thiên Bồng, Thiên Nhuế, Thiên Xung, Thiên Phụ, Thiên Cầm, Thiên Tâm, Thiên Trụ, Thiên Nhậm, Thiên Anh. Bát môn (八門) là tám cửa nhân bàn: Hưu, Sinh, Thương, Đỗ, Cảnh, Tử, Kinh, Khai, trong đó Khai Hưu Sinh là ba cửa cát. Bát thần (八神) là tám thần thần bàn, dẫn đầu là Trực Phù, rồi Đằng Xà, Thái Âm, Lục Hợp, và các thần khác tùy dòng dương bàn hay âm bàn.

---

## 3. Định cục

### 3.1 Dương độn và âm độn

Định cục (定局) là bước xác định lá số dùng số cục nào và theo chiều nào. Có hai chiều. Dương độn (陽遁) dùng cho nửa năm từ Đông Chí tới Mang Chủng, khi ngày dài dần, các số bố theo chiều thuận. Âm độn (陰遁) dùng cho nửa năm từ Hạ Chí tới Đại Tuyết, khi ngày ngắn dần, các số bố theo chiều nghịch. Chiều độn quyết định hướng bố sáu nghi ba kỳ và hướng xoay về sau.

### 3.2 Bảng định cục theo tiết khí và tam nguyên

Mỗi tiết khí chia ba nguyên là thượng nguyên, trung nguyên, hạ nguyên, mỗi nguyên một số cục. Bảng dưới liệt đầy đủ hai tư tiết khí với ba nguyên mỗi tiết. Cột trái là dương độn từ Đông Chí, cột phải là âm độn từ Hạ Chí.

| Tiết khí (dương độn) | Thượng | Trung | Hạ | Tiết khí (âm độn) | Thượng | Trung | Hạ |
|---|---|---|---|---|---|---|---|
| Đông Chí 冬至 | 1 | 7 | 4 | Hạ Chí 夏至 | 9 | 3 | 6 |
| Tiểu Hàn 小寒 | 2 | 8 | 5 | Tiểu Thử 小暑 | 8 | 2 | 5 |
| Đại Hàn 大寒 | 3 | 9 | 6 | Đại Thử 大暑 | 7 | 1 | 4 |
| Lập Xuân 立春 | 8 | 5 | 2 | Lập Thu 立秋 | 2 | 5 | 8 |
| Vũ Thủy 雨水 | 9 | 6 | 3 | Xử Thử 處暑 | 1 | 4 | 7 |
| Kinh Trập 驚蟄 | 1 | 7 | 4 | Bạch Lộ 白露 | 9 | 3 | 6 |
| Xuân Phân 春分 | 3 | 9 | 6 | Thu Phân 秋分 | 7 | 1 | 4 |
| Thanh Minh 清明 | 4 | 1 | 7 | Hàn Lộ 寒露 | 6 | 9 | 3 |
| Cốc Vũ 穀雨 | 5 | 2 | 8 | Sương Giáng 霜降 | 5 | 8 | 2 |
| Lập Hạ 立夏 | 4 | 1 | 7 | Lập Đông 立冬 | 6 | 9 | 3 |
| Tiểu Mãn 小滿 | 5 | 2 | 8 | Tiểu Tuyết 小雪 | 5 | 8 | 2 |
| Mang Chủng 芒種 | 6 | 3 | 9 | Đại Tuyết 大雪 | 4 | 7 | 1 |

Quy luật cấu trúc: mỗi cung trong tám cung quẻ ngoài quản ba tiết, số Lạc Thư của cung bằng số cục thượng nguyên của tiết đầu tiên. Đông Chí Khảm 1, Lập Xuân Cấn 8, Xuân Phân Chấn 3, Lập Hạ Tốn 4, Hạ Chí Ly 9, Lập Thu Khôn 2, Thu Phân Đoài 7, Lập Đông Càn 6. Thượng nguyên rồi bước dương thuận âm nghịch.

### 3.3 Phù đầu, siêu thần tiếp khí, và ba phép định cục

Phù đầu (符頭) là mốc để xác định một ngày thuộc nguyên nào. Thượng nguyên khởi từ ngày Giáp hoặc Kỷ. Ngày mang chi Tý Ngọ Mão Dậu là thượng nguyên, chi Dần Thân Tỵ Hợi là trung nguyên, chi Thìn Tuất Sửu Mùi là hạ nguyên. Cụ thể Giáp Tý, Giáp Ngọ, Kỷ Mão, Kỷ Dậu vào thượng nguyên; Giáp Dần, Giáp Thân, Kỷ Tỵ, Kỷ Hợi vào trung nguyên; Giáp Thìn, Giáp Tuất, Kỷ Sửu, Kỷ Mùi vào hạ nguyên.

Vì ba nguyên nhân năm ngày cho ba trên hai mươi bốn nhân năm bằng ba trăm sáu mươi ngày Kỳ Môn, không khớp năm dương lịch ba trăm sáu mươi lăm ngày, phù đầu bị trôi dần so với tiết khí. Phù đầu tới trước tiết gọi là siêu thần (超神), tới sau gọi là tiếp khí (接氣), cùng ngày gọi là chính thụ. Khi độ trôi lớn đến khoảng chín ngày, phải chèn một tiết khí lặp lại, gọi là trí nhuận (置閏), và chỉ chèn ở Mang Chủng hoặc Đại Tuyết.

Chính chỗ xử lý độ trôi này sinh ra ba phép định cục khác nhau, và engine phải cho chọn. Phép chiết bổ (拆補法) dùng phù đầu gần nhất không kèm tiết nhuận, đơn giản và phổ biến ở ứng dụng hiện đại. Phép trí nhuận (置閏法) chèn tiết khí lặp ở Mang Chủng và Đại Tuyết, theo truyền thống. Phép Mao Sơn đạo nhân (茅山道人法) là một cách giải khác. Cờ cấu hình dingju_method nhận một trong ba giá trị chaibu, zhirun, maoshan.

---

## 4. Bố địa bàn

### 4.1 Thứ tự sáu nghi ba kỳ

Sau khi định cục xong, bước tiếp là bố địa bàn (布地盤), tức đặt sáu nghi và ba kỳ vào chín cung theo số cục. Sáu nghi theo thứ tự Mậu Kỷ Canh Tân Nhâm Quý (戊己庚辛壬癸). Ba kỳ là Ất Bính Đinh (乙丙丁), gọi lần lượt nhật kỳ, nguyệt kỳ, tinh kỳ.

Luật bố theo chiều độn: dương độn thuận bố sáu nghi rồi nghịch bố ba kỳ; âm độn nghịch bố sáu nghi rồi thuận bố ba kỳ. Cụ thể điền theo thứ tự Mậu, Kỷ, Canh, Tân, Nhâm, Quý, rồi Đinh, Bính, Ất. Cung khởi đầu là cung mang số bằng số cục. Bước cung theo chiều độn: dương độn tiến một cung thuận theo Lạc Thư, âm độn lùi một cung nghịch.

### 4.2 Ví dụ bố địa bàn dương độn cục 1

Lấy dương độn cục một làm ví dụ. Cung khởi là cung Khảm số một. Điền Mậu vào cung một, rồi tiến thuận theo Lạc Thư: Kỷ vào cung hai Khôn, Canh vào cung ba Chấn, Tân vào cung bốn Tốn, Nhâm vào cung năm Trung, Quý vào cung sáu Càn, rồi tới ba kỳ Đinh vào cung bảy Đoài, Bính vào cung tám Cấn, Ất vào cung chín Ly.

| Cung | Số Lạc Thư | Bát quái | Nghi kỳ |
|---|---|---|---|
| Khảm | 1 | 坎 | 戊 Mậu |
| Khôn | 2 | 坤 | 己 Kỷ |
| Chấn | 3 | 震 | 庚 Canh |
| Tốn | 4 | 巽 | 辛 Tân |
| Trung | 5 | 中 | 壬 Nhâm |
| Càn | 6 | 乾 | 癸 Quý |
| Đoài | 7 | 兌 | 丁 Đinh |
| Cấn | 8 | 艮 | 丙 Bính |
| Ly | 9 | 離 | 乙 Ất |

Thứ tự điền Mậu Kỷ Canh Tân Nhâm Quý Đinh Bính Ất theo chiều thuận Lạc Thư. Âm độn đảo lại: cung khởi vẫn là số cục nhưng bước lùi, và ba kỳ thuận thay vì nghịch.

```
# cuc = so cuc (1..9); duong = True neu duong don
# LUOSHU_ORDER: chuoi cung theo Lac Thu; NGHI_KY = [Mau..Quy, Dinh, Binh, At]
def bo_dia_ban(cuc, duong):
    dia = {}
    cung = cuc                         # cung khoi = so cuc
    seq  = ["戊","己","庚","辛","壬","癸","丁","丙","乙"]
    for can in seq:
        dia[cung] = can
        if duong:
            cung = buoc_thuan_lac_thu(cung)   # tien 1 cung
        else:
            cung = buoc_nghich_lac_thu(cung)  # lui 1 cung
    return dia
```

---

## 5. Trực phù, trực sử, và bốn bàn

Đây là bước làm cho lá số Kỳ Môn sống động theo giờ. Trực phù (值符) là ngôi sao dẫn đầu, trực sử (值使) là cửa dẫn đầu. Hai ngôi này xác định theo tuần thủ của giờ, rồi thiên bàn xoay để trực phù về cung có can giờ. Bước này quyết định thế cục thời điểm, và là chỗ hai phái chuyển bàn với phi bàn tách nhau.

### 5.1 Tìm tuần thủ và định trực phù trực sử

Bốn bước. Một, từ can chi giờ tính tuần thủ, tức tuần giáp chứa giờ đó, ví dụ giờ trong tuần Giáp Tý thì tuần thủ là Giáp Tý, ẩn dưới nghi Mậu. Hai, tìm nghi tuần thủ đó trên địa bàn, xem nó ở cung nào. Ba, sao cửu tinh nằm ở cung đó là trực phù, cửa bát môn ở cung đó là trực sử. Bốn, xoay thiên bàn sao cho trực phù cùng nghi tuần thủ dời về cung đang chứa can giờ, các sao khác theo mà dời; còn trực sử thì đi theo cách đếm từ cung tuần thủ tới cung giờ.

| Tuần | Tuần thủ | Nghi ẩn |
|---|---|---|
| 甲子 Giáp Tý | 甲子 | 戊 Mậu |
| 甲戌 Giáp Tuất | 甲戌 | 己 Kỷ |
| 甲申 Giáp Thân | 甲申 | 庚 Canh |
| 甲午 Giáp Ngọ | 甲午 | 辛 Tân |
| 甲辰 Giáp Thìn | 甲辰 | 壬 Nhâm |
| 甲寅 Giáp Dần | 甲寅 | 癸 Quý |

Sáu tuần giáp mỗi tuần mười giờ. Nghi ẩn là can dương thay cho tuần giáp trong bố cục, dùng để tìm cung tuần thủ trên địa bàn.

### 5.2 Chuyển bàn và phi bàn

Có hai cách xoay thiên bàn, và đây là một trong những chỗ phân phái rõ nhất. Chuyển bàn (轉盤) coi cửu tinh như một bánh xe cứng: trực phù dời về cung can giờ, tám sao còn lại giữ nguyên thứ tự tương đối mà xoay theo. Đây là cách phổ biến nhất trong thời gia Kỳ Môn. Phi bàn (飛盤) cho mỗi sao bay theo số Lạc Thư riêng, không giữ khối cứng, tính cung rơi của trực phù bằng công thức trên số cục và vị trí can.

Chuyển bàn và phi bàn cho lá số khác nhau ở cùng một giờ, nên engine phải cho chọn qua cờ pan_method nhận giá trị chuyển hoặc phi, và ghi rõ trong lá số xuất ra. Mặc định nên là chuyển bàn vì đây là cách thời gia dùng nhiều nhất, nhưng người dùng nâng cao phải đổi được. Không được hardcode một cách rồi coi là chuẩn duy nhất.

### 5.3 Cung giữa và ký cung

Cung Trung số năm không có bát quái riêng trong nhiều thao tác, nên khi sao hay cửa rơi vào Trung cung, chúng ký sang cung Khôn số hai theo lối thường dùng. Quy tắc ký cung này cũng có dị bản giữa các phái, nên để thành một tham số nữa. Engine cần xử lý nhất quán Trung cung trong mọi bước để tránh lệch khi đối chiếu oracle.

---

## 6. Âm bàn và dương bàn

Ngoài các dị bản về phép bố và phép xoay, Kỳ Môn còn hai dòng lớn khác hẳn nhau về triết lý và cách tính, gọi là dương bàn và âm bàn. Đây không phải hai số cục mà là hai hệ thống thực hành riêng. Engine phải coi đây là một trục cấu hình cấp cao, vì chọn dòng nào sẽ đổi cả cách định cục lẫn cách luận.

### 6.1 Dương bàn cổ điển

Dương bàn (陽盤), còn gọi Kỳ Môn số lý hay thuật số, là dòng cổ điển được ghi trong đa số thư tịch. Nó dùng phép định cục qua siêu thần tiếp khí và chiết bổ hoặc trí nhuận, nặng về cách cục, tức các thế phối hợp giữa can thiên bàn và địa bàn cho ý nghĩa cát hung. Đây là dòng mà tài liệu này lấy làm mặc định, vì có nền văn bản dày và luật rõ để đối chiếu.

### 6.2 Âm bàn hiện đại

Âm bàn (陰盤), còn gọi pháp Kỳ Môn hay Kỳ Môn đạo gia, là dòng được hệ thống hoá và phổ biến gần đây, gắn với tên Vương Phượng Lân. Nó tính cục bằng cách lấy số dư khi chia cho chín, gọi là thái âm số, nhẹ về cách cục mà nặng về tượng số. Âm bàn còn hoán vị một số thần: đổi Bạch hổ thành Câu trần, đổi Huyền vũ thành Chu tước trong hệ bát thần, nên bản đồ thần khác dương bàn.

Engine đặt một cờ cấp cao yin_yang_pan nhận giá trị dương hoặc âm. Cờ này chi phối chuỗi thao tác: dương bàn đi theo định cục siêu thần tiếp khí và bảng cách cục cổ điển; âm bàn đi theo phép số dư và bảng thần đã hoán vị. Không trộn lẫn hai dòng trong một lá số. Mặc định là dương bàn, và tài liệu này đặc tả chủ yếu dương bàn; âm bàn nêu ở mức nguyên tắc để engine chừa chỗ mở rộng.

Người dùng của hai dòng thường không chấp nhận kết quả của dòng kia, vì luật khác nhau từ gốc. Nếu engine trộn hoặc mặc định ngầm một dòng mà không nói, kết quả sẽ sai với kỳ vọng của một nửa người dùng. Vì vậy mỗi lá số xuất ra phải đóng dấu rõ dòng nào, phái nào, phép nào, để người xem biết lá số này lập theo quy ước gì.

---

## 7. Cách cục và dụng thần

### 7.1 Cách cục là gì

Cách cục (格局) là các thế phối hợp đặc biệt trên lá số, cho ý nghĩa cát hung cô đọng. Nền tảng là thập can khắc ứng (十干克應), xét quan hệ giữa can thiên bàn và can địa bàn trong từng cung, thành một bảng tám mươi mốt ô. Ngoài ra còn nhiều cách gắn với sao, cửa, thần, và trạng thái nhập mộ, không vong, kích hình. Về lập trình, nhận diện cách cục là chạy một bộ vị từ trên lá số đã lập, giống rule engine, mỗi cách một luật.

### 7.2 Cát cách và hung cách

Một số cát cách tiêu biểu:

| Cách | Điều kiện | Ý nghĩa |
|---|---|---|
| 青龍返首 | 戊 + 丙 | Thanh long hồi đầu, việc lớn thành, đại cát |
| 飛鳥跌穴 | 丙 + 戊 | Chim bay sa huyệt, cơ may đến, thành tựu |
| 天遁 | 丙 + 生門 + 丁 | Thiên độn, ẩn trợ từ trời, tốt cho mưu sự |
| 地遁 | 乙 + 開門 + 己 | Địa độn, ẩn trợ từ đất, tốt cho ẩn tàng |
| 人遁 | 丁 + 休門 + 太陰 | Nhân độn, được người che chở, tốt cầu người |
| 三奇得使 | Kỳ gặp cửa hợp | Ba kỳ được dùng, thuận lợi, có quý trợ |
| 玉女守門 | Đinh thủ cửa cát | Ngọc nữ giữ cửa, tốt cho việc kín, hôn nhân |

Một số hung cách tiêu biểu:

| Cách | Điều kiện | Ý nghĩa |
|---|---|---|
| 青龍逃走 | 乙 + 辛 | Thanh long chạy trốn, mất mát, phản bội |
| 白虎猖狂 | 辛 + 乙 | Bạch hổ hung hăng, tai hoạ, tranh đấu |
| 朱雀投江 | 丁 + 癸 | Chu tước nhảy sông, tin xấu, văn thư hỏng |
| 螣蛇夭矯 | 癸 + 丁 | Đằng xà quằn quại, việc rối, kinh sợ |
| 太白入熒 | 庚 + 丙 | Thái bạch nhập huỳnh, đối phương đến, hao |
| 熒入太白 | 丙 + 庚 | Huỳnh nhập thái bạch, mình động binh, tổn |
| 大格 | 庚 + 癸 | Đại cách, trở ngại lớn, đình trệ nặng |
| 五不遇時 | Thời can khắc nhật can | Ngũ bất ngộ, mất thời, việc khó thành |

Ngoài các cách trên còn nhiều thế cần kiểm: nhập mộ, tức can rơi vào cung mộ của nó; không vong, tức chi rơi vào tuần không; môn bách, tức cửa khắc cung; lục nghi kích hình, tức nghi rơi vào cung hình; phản ngâm và phục ngâm, tức lá số rơi vào cung đối xung hay trùng cung. Mỗi thế là một vị từ, và một cung có thể mang nhiều cách cùng lúc. Danh sách đầy đủ số hoá thành bảng dữ liệu, đối chiếu với thư viện kinqimen.

### 7.3 Dụng thần theo loại việc

Dụng thần (用神) trong Kỳ Môn là ký hiệu đại diện cho người, việc, hay vật đang hỏi, chọn theo loại câu hỏi. Khác Lục Nhâm lấy dụng thần qua lục thân, Kỳ Môn gán dụng thần cho từng loại việc theo quy ước riêng, rồi xét cung chứa dụng thần đó tốt hay xấu.

| Loại việc | Dụng thần chính |
|---|---|
| Cầu tài | Nhật can là mình, thời can là tài, sinh môn là lợi, trực phù là chủ hàng, lục hợp là người môi giới, khai môn là cửa hàng |
| Sự nghiệp công danh | Khai môn là chức quan, trực phù là cấp trên |
| Hôn nhân | Ất là nữ, Canh là nam, lục hợp là mai mối và hôn sự |
| Kiện tụng | Khai môn và trực phù là phía quan, Canh là đối phương, nhật can là mình |
| Xuất hành | Xem khai hưu sinh môn và phương của chúng, cùng dịch mã |
| Bệnh tật | Thiên nhuế là sao bệnh, thiên tâm là sao thuốc và thầy |
| Cạnh tranh chủ khách | Nhật can là chủ, thời can là khách, so hai bên |
| Hợp tác | Lục hợp là quan hệ hợp tác, xét sinh khắc hai bên |

Ranh giới engine và AI khi luận Kỳ Môn. Lá số bốn bàn, trực phù trực sử, và toàn bộ cách cục nhận diện được là dữ kiện tất định, do engine tính và phải khớp oracle kinqimen. Phần diễn giải, tức chọn dụng thần theo câu hỏi rồi đọc cung của nó qua sao cửa thần và cách cục để thành lời đoán, do tầng AI hỗ trợ, luôn trích nguồn từ Yên Ba Điếu Tẩu Ca và các bộ luận, gắn nhãn AIDisclosure, và không khẳng định quá mức. Kỳ Môn nhiều phái nên tầng diễn giải phải nói rõ đang luận theo phái nào.

---

## 8. Đặc tả engine và schema JSON

### 8.1 Luồng engine

Engine nhận thời điểm đã chuẩn hoá gồm tứ trụ và giờ, cùng tiết khí và tam nguyên tính từ lõi lịch pháp, và một tập cờ trường phái. Nó chạy tuần tự: định cục ra số cục và chiều độn, bố địa bàn sáu nghi ba kỳ, tìm tuần thủ rồi định trực phù trực sử, xoay thiên bàn theo chuyển bàn hoặc phi bàn, an cửu tinh bát môn bát thần, nhận diện cách cục và các thế đặc biệt. Kết quả là một đối tượng JSON đầy đủ bốn bàn. Mọi bước tất định, nên lá số cache được theo thời điểm làm tròn, kinh độ, và tập cờ.

```json
{
  "he": "ky_mon",
  "dau_vao": {
    "datetime": "...", "tz": "+07:00",
    "kinh_do": 106.7, "chan_thai_duong_thoi": true
  },
  "tu_tru": { "nam":"...", "thang":"...",
              "ngay":"...", "gio":"甲子" },
  "dinh_cuc": {
    "tiet_khi":"冬至", "tam_nguyen":"上元",
    "duong_don":true, "so_cuc":1
  },
  "dia_ban": { },
  "thien_ban": { },
  "cuu_tinh": { },
  "bat_mon": { },
  "bat_than": { },
  "truc_phu": "天蓬",
  "truc_su": "休門",
  "cach_cuc": ["青龍返首"],
  "co_truong_phai": {
    "dingju_method": "chaibu",
    "pan_method": "zhuan",
    "yin_yang_pan": "duong"
  }
}
```

### 8.2 Tập cờ trường phái

Kỳ Môn cần tập cờ đầy đủ nhất trong ba hệ. Ba cờ cốt lõi: dingju_method chọn phép định cục trong chiết bổ, trí nhuận, hay Mao Sơn; pan_method chọn chuyển bàn hay phi bàn; yin_yang_pan chọn dương bàn hay âm bàn. Ngoài ra còn cờ cho quy tắc ký cung Trung cung, và cờ chân thái dương thời. Mỗi lá số xuất ra đóng dấu toàn bộ tập cờ, để hai người dùng khác phái vẫn hiểu lá số lập theo quy ước gì và có thể tái lập.

| Cờ | Giá trị | Mặc định |
|---|---|---|
| dingju_method | chaibu, zhirun, maoshan | chaibu |
| pan_method | zhuan, fei | zhuan |
| yin_yang_pan | duong, am | duong |
| zhong_gong_ky | khon2, giu_nguyen | khon2 |
| chan_thai_duong_thoi | true, false | true |

Tiêu chí nghiệm thu engine Kỳ Môn. Engine đạt yêu cầu khi, với mỗi tổ hợp cờ, khớp một trăm phần trăm với thư viện đối chiếu kinqimen trên tập lớn ca mẫu phủ đủ hai tư tiết khí và ba nguyên, và khi các ca biên siêu thần tiếp khí, đặt nhuận, và Trung cung đều có kiểm thử riêng. Vì Kỳ Môn nhiều phái, bộ kiểm thử phải chạy cho từng tổ hợp cờ, không chỉ một cấu hình mặc định.

---

Kỳ Môn Độn Giáp là hệ Tam Thức phức tạp và nhiều trường phái nhất: định cục qua tiết khí và tam nguyên, bố sáu nghi ba kỳ lên chín cung, dựng bốn bàn địa thiên nhân thần, tìm trực phù trực sử rồi xoay thiên bàn, cuối cùng đọc cách cục và dụng thần. Chính vì nhiều dị bản, nguyên tắc xuyên suốt là cấu hình bằng cờ chứ không hardcode, và đóng dấu tập cờ vào mọi lá số. Tập 4 chuyển sang Thái Ất Thần Số, hệ vĩ mô nhất trong ba hệ. Hiện Thực Hoá Ý Chí.

## 9. Bảng tra mở rộng: các phái định cục và năm loại Kỳ Môn

Chương này bổ sung hai bảng tra cho phần định cục và cho các loại Kỳ Môn theo đơn vị thời gian. Kỳ Môn nhiều phái hơn hai hệ kia, nên phần định cục có nhiều cách làm cạnh nhau, và engine phải cấu hình được từng cách.

### 9.1 Các phái định cục

Định cục là bước tìm số cục, dương độn một tới chín hoặc âm độn một tới chín, dựa trên tiết khí và tam nguyên. Chỗ các phái khác nhau nằm ở cách xử lý khi tiết khí và can chi ngày không khớp đều, tức các trường hợp siêu thần tiếp khí.

| Phái | Cách xử lý siêu thần tiếp khí và đặt cục |
|---|---|
| 拆補法 Sách bổ | Khi phù đầu và tiết khí lệch, tách và bù cho khớp; phái phổ biến, xử lý lệch bằng cách chia bù cục |
| 置閏法 Trí nhuận | Đặt cục nhuận khi lệch tích đủ, giống nhuận trong lịch; giữ nhịp tam nguyên bằng cục nhuận |
| 茅山道人 Mao Sơn | Theo phép Mao Sơn đạo nhân, xử lý lệch theo quy tắc riêng của phái này |
| 陰陽順逆 Âm dương thuận nghịch | Đặt cục theo chiều thuận nghịch của dương độn âm độn, không dùng nhuận, theo lối số lý |

Định cục là nơi Kỳ Môn phân phái mạnh nhất, vì các phái xử lý khác nhau chỗ tiết khí và can chi ngày lệch nhau. Trong engine, phái định cục là một cờ trường phái quan trọng, và mỗi phái cho một số cục có thể khác nhau ở các ca biên. Vì vậy bộ kiểm thử phải chạy cho từng phái, và mỗi lá số phải đóng dấu phái định cục đã dùng.

### 9.2 Năm loại Kỳ Môn theo tầm thời gian

Kỳ Môn có năm loại theo đơn vị thời gian dùng để lập cục, từ khắc tới năm. Mỗi loại hợp một tầm câu hỏi khác nhau. Loại giờ là phổ biến nhất cho câu hỏi cụ thể.

| Loại | Đơn vị | Dùng cho |
|---|---|---|
| 時家奇門 Thời gia | Giờ | Câu hỏi cụ thể theo giờ, loại phổ biến nhất |
| 日家奇門 Nhật gia | Ngày | Việc trong ngày, chọn ngày |
| 月家奇門 Nguyệt gia | Tháng | Việc trong tháng, kế hoạch tháng |
| 年家奇門 Niên gia | Năm | Việc trong năm, tầm dài |
| 刻家奇門 Khắc gia | Khắc | Việc rất ngắn, tầm khắc, ít dùng |

Ngoài phái định cục và loại thời gian, còn một cờ lớn nữa là âm bàn hay dương bàn. Dương bàn là lối thuật số truyền thống, âm bàn là lối pháp Kỳ Môn hiện đại mà nhiều app dùng. Ba trục cờ này, phái định cục, loại thời gian, và âm dương bàn, cùng nhau xác định cách một lá số Kỳ Môn được dựng.

## 10. Ví dụ lập bàn mẫu có lời giải

Chương này đi qua một ví dụ lập bàn Kỳ Môn hoàn chỉnh theo lối thời gia dương độn, từng bước, để minh hoạ luồng đã mô tả. Các con số minh hoạ phương pháp; khi lập trình phải đối chiếu oracle như kinqimen.

Dữ kiện và cấu hình ví dụ: giả sử cuộc hỏi rơi vào một tiết thuộc dương độn, tam nguyên là thượng nguyên, cho số cục là dương độn cục một. Cấu hình dùng: loại thời gia, phái định cục sách bổ, dương bàn, phương pháp chuyển bàn. Giờ hỏi cho một thời can cụ thể để xác định trực phù và trực sử.

### 10.1 Bước một, định cục

Từ tiết khí và tam nguyên, tra ra số cục. Ví dụ cho dương độn cục một: dương độn nghĩa là lục nghi tam kỳ bố theo chiều thuận, và số một là cung khởi. Đây là bước quyết định toàn bộ thế bố cục sau đó, và là chỗ phái định cục có thể cho kết quả khác nhau ở ca biên.

### 10.2 Bước hai, bố địa bàn lục nghi tam kỳ

Bố lục nghi tam kỳ vào chín cung theo thứ tự dương độn. Lục nghi là sáu can Mậu Kỷ Canh Tân Nhâm Quý, tam kỳ là Ất Bính Đinh. Với dương độn cục một, khởi từ cung một và rải theo chiều thuận qua chín cung.

| Nhóm | Can | Chiều bố |
|---|---|---|
| Lục nghi | 戊 己 庚 辛 壬 癸 | Theo thứ tự, thuận chiều dương độn từ cung khởi |
| Tam kỳ | 乙 丙 丁 | Nối tiếp sau lục nghi, cùng chiều thuận |

### 10.3 Bước ba, an trực phù trực sử

Tìm cung chứa thời can trong địa bàn, đó là gốc để xác định trực phù và trực sử. Trực phù là sao đứng đầu, đi theo thời can; trực sử là cửa đứng đầu, đi theo cùng gốc. Sau khi biết trực phù trực sử, quay chín sao thiên bàn và tám cửa tới vị trí của chúng theo thời can.

Trực phù và trực sử là bản lề nối bố cục tĩnh với thời điểm hỏi. Mọi sao và cửa quay quanh hai mốc này. Xác định sai vị trí thời can là sai toàn bộ lá số, nên đây là bước engine phải kiểm kỹ nhất sau định cục.

### 10.4 Bước bốn, an bát thần và đọc cách cục

An tám thần hoặc chín thần lên các cung, khởi từ Trực Phù thần theo chiều dương độn. Sau khi đủ bốn tầng địa bàn thiên bàn bát môn cửu tinh và tầng thần, đọc cách cục: xét các tổ hợp cát hung trên các cung so với bảng cách cục ở chương bảy, tìm dụng thần theo loại câu hỏi, và luận thế cục.

Như Lục Nhâm, toàn bộ luồng lập bàn Kỳ Môn là tất định một khi đã chốt cấu hình cờ. Điểm khác Lục Nhâm là Kỳ Môn có nhiều cờ hơn, nên cùng một thời điểm có thể cho lá số khác nhau tuỳ cấu hình, và mọi cờ phải đóng dấu vào lá số. Khâu luận nghĩa cuối thuộc tầng AI có trích nguồn, tách khỏi khâu lập bàn này.


> Tài liệu 3/7 trong bộ Tam Thức của CyberSkill. Phiên bản 1.0. Nội dung mang tính tham khảo tri thức và giáo dục di sản, không phải lời khuyên y tế, pháp lý, hay tài chính. Thuật toán và bảng tra cần đối chiếu ít nhất hai nguồn trước khi khoá vào bản phát hành, và với Kỳ Môn phải kiểm cho từng tổ hợp cờ trường phái. Các giá trị thiết kế theo CyberSkill Global Design System v1.3.0.
