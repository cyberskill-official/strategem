# Tài liệu 4 — Thái Ất Thần Số chuyên sâu

> Bộ tài liệu Tam Thức (三式) của CyberSkill — Tập 4/7
> Phiên bản 1.0 · Slogan: "Turn Your Will Into Real" — Hiện Thực Hoá Ý Chí
> Nội dung mang tính tham khảo tri thức và giáo dục di sản, không phải lời khuyên y tế, pháp lý, hay tài chính.

Tài liệu này đặc tả hệ Thái Ất Thần Số (太乙神數) ở mức đủ để lập trình một engine lập bàn và để một người học nắm quy trình. Thái Ất là hệ vĩ mô nhất trong Tam Thức, chủ về vận nước, chu kỳ lớn, và cục diện dài hạn, nên khác hẳn Lục Nhâm và Kỳ Môn vốn xét việc cụ thể và thời điểm gần.

## Thông tin tài liệu

| Trường | Nội dung |
|---|---|
| Hệ | Thái Ất Thần Số (太乙神數) — chủ Thiên, luận vận hội và chu kỳ lớn |
| Đặc điểm | Dùng tích niên đếm từ mốc khởi nguyên; có nhiều mốc kỷ nguyên không tương thích |
| Đầu vào engine | Năm dương lịch và mốc thời gian, cùng cờ chọn kỷ nguyên |
| Đầu ra engine | Bàn Thái Ất dạng JSON: vị trí Thái Ất, mười sáu thần, tám tướng, các toán, cách cục |
| Oracle đối chiếu | Thư viện mã nguồn mở kintaiyi, hỗ trợ bốn phép tính năm tháng ngày giờ |

## Mục lục

1. Tổng quan hệ Thái Ất và luồng lập bàn
2. Tích niên và vận hành Thái Ất
3. Mười sáu thần
4. Bát tướng và các toán
5. Bốn phép tính năm tháng ngày giờ
6. Cách cục và luận chủ khách thắng bại
7. Đặc tả engine và schema JSON

---

## 1. Tổng quan hệ Thái Ất và luồng lập bàn

### 1.1 Thái Ất giải quyết bài toán gì

Thái Ất Thần Số trả lời câu hỏi về cái lớn và cái xa: vận số một triều đại hay một quốc gia, chu kỳ thịnh suy dài hạn, thiên tai, binh biến, được mùa mất mùa. Trong ba hệ Tam Thức, Thái Ất chủ Thiên, xét khí số vĩ mô, đối lại Kỳ Môn chủ Địa xét phương vị và Lục Nhâm chủ Nhân xét việc người. Xưa Thái Ất là học vấn của triều đình, dùng để luận quốc sự, nên bị hạn chế lưu truyền trong dân gian.

Tên hệ gắn với sao Thái Ất (太乙), cũng viết Thái Nhất, ngôi sao tôn quý nhất trong quan niệm cổ, được coi là ngôi của thiên đế, chủ tể vận hành của trời đất. Thần số (神數) nghĩa là phép số thần diệu. Ghép lại, Thái Ất Thần Số là phép số lấy sao Thái Ất làm ngôi chủ để suy vận trời.

### 1.2 Vì sao Thái Ất dùng tích niên

Điểm khác biệt cốt lõi của Thái Ất so với hai hệ kia là cách tính thời gian. Lục Nhâm và Kỳ Môn dùng can chi và tiết khí của thời điểm chiêm, tức thông tin lịch trong một năm. Thái Ất thì dùng tích niên (積年), một số đếm năm liên tục tính từ một mốc khởi nguyên rất xa trong quá khứ tới năm đang xét. Chính con số tích niên này, qua các phép chia lấy dư, quyết định vị trí Thái Ất và toàn bộ lá số.

Vì tích niên đếm từ một mốc khởi nguyên, mà các thư tịch dùng mốc khác nhau, nên cùng một năm dương lịch có thể cho tích niên khác nhau tùy nguồn. Hai mốc phổ biến lệch nhau tới sáu mươi năm, đủ để đổi cả lá số. Engine bắt buộc phải cho chọn kỷ nguyên qua một cờ, và mỗi lá số xuất ra phải đóng dấu rõ đã dùng kỷ nguyên nào, nếu không kết quả không tái lập và không bảo vệ được.

### 1.3 Thư tịch nền và thư viện đối chiếu

Thư tịch nền quan trọng nhất là Thái Ất Kim Kính Thức Kinh (太乙金鏡式經) của Vương Hy Minh đời Đường, bộ sớm và có thẩm quyền về phép Thái Ất. Các bộ khác gồm Thái Ất Thống Tông Bảo Giám (太乙統宗寶鑑), và phần Thái Ất trong Cổ Kim Đồ Thư Tập Thành, quyển Nghệ Thuật Điển. Tống sử Nghệ văn chí có chép nhiều sách Thái Ất nay đã thất truyền. Đây là hệ có văn bản khó và ít bản dịch nhất trong ba hệ.

Thư viện đối chiếu là kintaiyi, package Python lập bàn Thái Ất, hỗ trợ bốn phép niên nguyệt nhật thời kế. Engine của ta khi lập bàn sẽ so vị trí Thái Ất, mười sáu thần, tám tướng, và các toán với kintaiyi, cùng một nguồn thứ hai, trên tập ca mẫu phủ nhiều năm, đối chiếu theo từng kỷ nguyên. Vì tích niên là số rất lớn, phải kiểm kỹ phép chia lấy dư và cách quy về cung.

---

## 2. Tích niên và vận hành Thái Ất

### 2.1 Tích niên và mốc kỷ nguyên

Tích niên là nền của mọi phép Thái Ất. Cách tính thực dụng phổ biến trong các engine hiện đại lấy tích niên bằng mười triệu một trăm năm mươi ba nghìn chín trăm mười bảy cộng với năm dương lịch. Con số cộng thêm này chính là khoảng cách từ mốc khởi nguyên tới năm không của lịch hiện đại, theo hệ Kim Kính và Thống Tông. Một hệ khác lấy mốc lệch đi sáu mươi năm, cho ra tích niên khác.

Engine đặt một cờ epoch chọn giữa các mốc kỷ nguyên. Mặc định nên dùng hệ Kim Kính và Thống Tông, tức tích niên bằng mười triệu một trăm năm mươi ba nghìn chín trăm mười bảy cộng năm CE, vì đây là hệ có nền văn bản dày nhất. Mốc cổ điển một triệu chín trăm ba mươi bảy nghìn hai trăm tám mươi mốt tại năm bảy trăm hai mươi tư sau công nguyên được để làm lựa chọn. Mỗi lá số đóng dấu kỷ nguyên đã dùng.

### 2.2 Ba phép rút gọn dư số

Từ tích niên, ba phép chia lấy dư cho ra ba thông tin nền. Tích niên chia lấy dư cho ba trăm sáu mươi ra số nhập kỷ nguyên. Chia lấy dư cho bảy mươi hai ra số nhập cục, một số từ một đến bảy mươi hai, đây là số quan trọng nhất để định vị Thái Ất và tính các tướng. Chia lấy dư cho sáu mươi ra can chi của năm. Ba phép này là cửa vào toàn bộ lá số.

```
# nam_ce = nam duong lich; epoch chon moc khoi nguyen
def tich_nien(nam_ce, epoch="kim_kinh"):
    if epoch == "kim_kinh":
        tn = 10_153_917 + nam_ce
    elif epoch == "co_dien":
        tn = 1_937_281 + (nam_ce - 724)   # quy ve moc 724 CE
    nhap_ky_nguyen = tn % 360
    nhap_cuc       = tn % 72     # 1..72, so cuc quan trong nhat
    can_chi        = tn % 60
    return tn, nhap_ky_nguyen, nhap_cuc, can_chi
```

### 2.3 Chín cung và đường đi của Thái Ất

Thái Ất vận hành trên chín cung, nhưng theo một bố cục và luật đi riêng, khác Kỳ Môn. Bố cục chín cung của Thái Ất xoay bốn mươi lăm độ ngược chiều kim đồng hồ so với Lạc Thư thường: Càn một, Ly hai, Cấn ba, Chấn bốn, Trung năm, Đoài sáu, Khôn bảy, Khảm tám, Tốn chín. Thái Ất đi một cung mỗi ba năm, nên hai mươi bốn năm đi hết một vòng tám cung ngoài. Điểm quan trọng: Thái Ất không bao giờ vào trung cung số năm.

Thái Ất cũng có hai chiều đi. Theo cách dùng chung, sau Đông Chí đi dương độn thuận, khởi từ cung một là Càn tiến tới; sau Hạ Chí đi âm độn nghịch, khởi từ cung chín là Tốn lùi lại. Chu kỳ ba năm một cung, hai mươi bốn năm một vòng, và ba vòng bảy mươi hai năm khớp với số cục nhập từ phép chia dư cho bảy mươi hai. Đường đi này là tất định, chỉ phụ thuộc số cục.

---

## 3. Mười sáu thần

### 3.1 Vòng mười sáu thần

Mười sáu thần (十六神) là mười sáu vị trí quanh vòng, làm hệ toạ độ để an Thái Ất và tính các tướng. Khác chín cung tám hướng thường thấy, Thái Ất chia vòng thành mười sáu mốc, gồm tám chính cung ở tám hướng và tám gian thần xen giữa. Mỗi mốc có một tên thần cố định.

Thứ tự mười sáu thần đi từ cung Tý thuận chiều: Địa chủ ở Tý, Dương đức ở Sửu, Hoà đức ở Cấn, Lữ thân ở Dần, Cao tùng ở Mão, Thái dương ở Thìn, Đại quýnh ở Tốn, Đại thần ở Tỵ, Đại uy ở Ngọ, Thiên đạo ở Mùi, Đại vũ ở Khôn, Vũ đức ở Thân, Thái thốc ở Dậu, Âm chủ ở Tuất, Âm đức ở Càn, Đại nghĩa ở Hợi. Đây là dữ liệu tra cứu cố định, số hoá thành một mảng mười sáu phần tử.

### 3.2 Chính cung và gian thần

Mười sáu thần chia hai loại. Tám chính cung (正宮) nằm ở bốn hướng chính Tý Ngọ Mão Dậu và bốn hướng góc Càn Khôn Cấn Tốn, ứng tám quẻ. Tám gian thần (間神) nằm ở tám chi còn lại Dần Thân Tỵ Hợi Thìn Tuất Sửu Mùi, xen giữa các chính cung. Sự phân biệt này không chỉ là vị trí mà quyết định cách tính toán ở chương sau: chính cung có số cung riêng, gian thần thì khi tính chỉ kể là một.

| Cung | Thần | Phiên âm | Loại |
|---|---|---|---|
| 子 | 地主 | Địa chủ | Chính cung |
| 丑 | 陽德 | Dương đức | Gian thần |
| 艮 | 和德 | Hoà đức | Chính (duy) |
| 寅 | 呂申 | Lữ thân | Gian thần |
| 卯 | 高叢 | Cao tùng | Chính cung |
| 辰 | 太陽 | Thái dương | Gian thần |
| 巽 | 大炅 | Đại quýnh | Chính (duy) |
| 巳 | 大神 | Đại thần | Gian thần |
| 午 | 大威 | Đại uy | Chính cung |
| 未 | 天道 | Thiên đạo | Gian thần |
| 坤 | 大武 | Đại vũ | Chính (duy) |
| 申 | 武德 | Vũ đức | Gian thần |
| 酉 | 太簇 | Thái thốc | Chính cung |
| 戌 | 陰主 | Âm chủ | Gian thần |
| 乾 | 陰德 | Âm đức | Chính (duy) |
| 亥 | 大義 | Đại nghĩa | Gian thần |

Có dị bản tên: Lữ thân cũng viết Lữ thần, Đại vũ cũng viết Đại vũ hay Đợi vũ. Engine giữ bảng chuẩn và ghi chú dị bản, không tự đổi.

### 3.3 Vai trò khi tính toán

Phân biệt chính cung và gian thần là mấu chốt để tính đúng các tướng và các toán ở chương sau. Khi đếm quanh vòng, gian thần được kể là một bước hoặc một đơn vị, còn chính cung dùng số cung riêng của nó khi cộng toán. Sai chỗ này là lỗi thường gặp nhất khi lập trình Thái Ất. Vì vậy engine phải mã hoá rõ mỗi mốc là chính cung hay gian thần, và giữ nhất quán quy tắc đếm qua toàn bộ phép tính.

---

## 4. Bát tướng và các toán

Sau khi an Thái Ất vào cung theo số cục, bước tiếp là an tám tướng và tính các toán. Đây là phần tính toán đặc trưng nhất của Thái Ất, và là nền cho luận thắng bại chủ khách. Tám tướng đều suy ra tất định từ số cục và vị trí Thái Ất, nên viết được thành thuật toán, dù các bước đếm khá phức tạp.

### 4.1 Văn Xương và Thủy Kích

Tám tướng gồm: hai mục là Văn Xương và Thủy Kích; hai đại tướng là chủ đại tướng và khách đại tướng; hai tham tướng là chủ tham tướng và khách tham tướng; và kế thần. Trong đó Văn Xương (文昌), còn gọi chủ mục hay thiên mục, đại diện cho chủ, tức phe ta, bên phòng thủ. Thủy Kích (始擊), còn gọi khách mục hay địa mục, đại diện cho khách, tức đối phương, bên tấn công.

Cách an Văn Xương: an theo số nhập cục. Lấy số nhập cục chia luỹ tiến cho mười tám tới khi dư nhỏ hơn mười tám. Dùng số dư đó đếm thuận trên vòng mười sáu thần: dương độn khởi đếm từ Vũ đức ở Thân, âm độn khởi từ Lữ thân ở Dần. Khi đếm, dương độn đếm hai cung Càn và Khôn hai lần, âm độn đếm Cấn và Tốn hai lần. Cung đến là Văn Xương. Thủy Kích thì an qua kế thần, dùng phép kế thần gia Cấn rồi chuyển cung.

### 4.2 Kế thần

Kế thần (計神) là ngôi trung gian để an Thủy Kích, an theo chi của năm. Dương độn khởi Lữ thân ở Dần rồi đi thuận theo mười hai chi; âm độn khởi từ Thân đi nghịch. Kế thần vừa là một trong tám tướng, vừa là mốc để suy Thủy Kích, nên phải tính trước Thủy Kích.

### 4.3 Chủ toán và khách toán

Chủ toán và khách toán là hai con số cốt lõi để luận thắng bại. Chủ toán (主算) tính từ cung Văn Xương, khách toán (客算) tính từ cung Thủy Kích. Cách tính giống nhau: đếm thuận quanh vòng, cộng dồn số cung của các chính cung đi qua, gian thần thì kể là một, dừng lại ở cung ngay trước cung Thái Ất. Tổng cộng được là toán của phe đó.

Có nguồn thứ cấp nói đếm tới cung sau Thái Ất, nhưng bản Thống Tông cổ điển nói dừng ở cung trước Thái Ất. Đây là điểm dễ sai và gây lệch kết quả, nên engine mặc định theo bản cổ điển dừng trước, và để một cờ cho phép đổi. Cùng với đó, chính cung dùng số cung của nó, còn gian thần khi cộng vào tổng chỉ kể là một, không dùng số cung. Hai quy tắc này phải nhất quán.

### 4.4 Đại tướng và tham tướng

Từ chủ toán và khách toán suy ra vị trí đại tướng và tham tướng. Cung đại tướng lấy theo toán: nếu toán trong khoảng một đến chín, mười một đến mười chín, và tương tự, thì bỏ hàng chục lấy hàng đơn vị làm cung; nếu toán đúng bằng mười, hai mươi, ba mươi, bốn mươi thì chia cho chín lấy dư làm cung. Cung tham tướng lấy bằng số cung của đại tướng nhân ba rồi quy về cung. Đây là các phép số học thuần tuý, cài đặt trực tiếp.

Ngoài vị trí, mỗi toán còn cho biết trường hay đoản. Toán từ mười một trở lên là trường số (長), ứng cái bền lâu và có xu hướng thắng. Toán từ chín trở xuống là đoản số (短), ứng cái nhanh gấp và có xu hướng bại. Trường đoản của chủ toán và khách toán là một trong bốn tiêu chí luận thắng bại ở chương sáu.

---

## 5. Bốn phép tính năm tháng ngày giờ

Thái Ất không chỉ lập một bàn cho năm, mà có bốn cấp lập bàn theo năm, tháng, ngày, giờ, gọi là niên kế, nguyệt kế, nhật kế, thời kế. Bốn phép này cho phép Thái Ất luận từ vận lớn dài hạn tới cục diện của một thời điểm cụ thể. Mỗi phép có công thức tích riêng, nhưng đều quy về số cục nhập qua phép chia lấy dư cho bảy mươi hai.

### 5.1 Niên kế

Niên kế (年計) là phép lập bàn theo năm, nền của cả hệ. Tích niên bằng mười triệu một trăm năm mươi ba nghìn chín trăm mười bảy cộng năm dương lịch. Số cục bằng tích niên chia lấy dư cho bảy mươi hai. Can chi bằng tích niên chia lấy dư cho sáu mươi. Ví dụ năm hai nghìn linh bốn, tích niên là mười triệu một trăm năm mươi lăm nghìn chín trăm hai mươi mốt, chia lấy dư cho sáu mươi ra hai mươi mốt là Giáp Thân, chia lấy dư cho bảy mươi hai ra ba mươi ba là dương độn cục ba mươi ba.

### 5.2 Nguyệt kế, nhật kế, thời kế

| Phép | Tích | Số cục |
|---|---|---|
| Niên kế 年計 | Tích niên = 10.153.917 + năm CE | Tích niên mod 72 |
| Nguyệt kế 月計 | Tích nguyệt = tích niên × 12 (chỉnh tháng nhuận riêng) | Tích nguyệt mod 72 |
| Nhật kế 日計 | Lấy Đông Chí làm mốc; tích nhật = năm tích Giáp Tý × 365,2425 | Tích nhật mod 72 cộng 1, rồi tiến theo ngày |
| Thời kế 時計 | Tích thời = tích nhật × 12 | Tích thời mod 72 cộng 1, rồi tiến theo giờ |

Một giờ là một cục, sáu ngày là bảy mươi hai cục khép một vòng. Nhật kế và thời kế lấy Đông Chí làm điểm neo, sau Đông Chí đi dương độn thuận, sau Hạ Chí đi âm độn nghịch. Phép nguyệt kế xử lý tháng nhuận qua thuật cầu tích nguyệt riêng.

Bốn phép cho bốn độ phân giải: niên kế luận vận nhiều năm, nguyệt kế luận trong năm, nhật kế luận theo ngày, thời kế luận theo giờ. Khi hỏi một sự việc, người dùng chọn cấp phù hợp với tầm của câu hỏi. Engine cần cài cả bốn, và vì tích của nhật kế thời kế phụ thuộc số ngày từ Đông Chí, phải nối với lõi lịch pháp tập 5 để tính chính xác thời điểm Đông Chí mỗi năm.

---

## 6. Cách cục và luận chủ khách thắng bại

### 6.1 Các cách giữa Thái Ất và tướng

Cách cục trong Thái Ất xét quan hệ vị trí giữa Thái Ất và các tướng trên vòng cung. Khi một tướng rơi vào cùng cung, cung kề, hay cung đối xung với Thái Ất, sinh ra các cách có tên và ý nghĩa riêng. Đây là các vị từ vị trí, cài đặt bằng cách so cung của tướng với cung của Thái Ất.

| Cách | Định nghĩa | Bên |
|---|---|---|
| 掩 Yểm | Khách mục hoặc khách tướng cùng cung Thái Ất | Khách |
| 迫 Bách | Tướng ở cung ngay trước hoặc sau Thái Ất | Chủ và khác |
| 關 Quan | Chủ mục hoặc chủ tướng cùng cung Thái Ất; hoặc hai tướng cùng bên chung cung | Chủ |
| 囚 Tù | Chủ hoặc khách đại tướng cùng cung Thái Ất | Đại tướng |
| 擊 Kích | Thủy Kích kề Thái Ất; cung trước là ngoại kích, cung sau là nội kích | Khách |
| 格 Cách | Tướng hoặc khách mục ở cung đối xung Thái Ất | Đối xung |
| 對 Đối | Thái Ất và tướng ở hai cung xung nhau | Đối xung |

Bản Thống Tông Bảo Giám quyển sáu tóm: cùng cung gọi Quan gọi Tù, cùng cung với khách gọi Yểm, cung trước sau một cung gọi Bách, cung xung gọi Cách. Còn có cách phức hợp như Đề hiệp, Tứ quách cố, Tứ quách đỗ khi nhiều tướng cùng lâm thế yểm bách kích.

### 6.2 Bốn tiêu chí luận thắng bại

Luận thắng bại chủ khách là mục đích chính khi dùng Thái Ất cho việc tranh chấp, thi đấu, hay đối kháng. Thái Ất đại diện sự việc, Văn Xương là chủ tức phe ta, Thủy Kích là khách tức đối phương. Bốn tiêu chí kết hợp cho ra phán đoán bên nào thắng.

Hoà và bất hoà: so chủ toán với khách toán, xét hai bên có hoà hợp hay khắc nghịch. Toán của bên nào lớn hơn thường ứng bên đó có thế hơn.

Trường và đoản toán: trường toán từ mười một trở lên ứng cái bền lâu, có xu hướng thắng. Đoản toán từ chín trở xuống ứng cái nhanh gấp, có xu hướng bại. So trường đoản của chủ và khách.

Tam tài: xét thiên địa nhân có đủ không. Đủ ba là cát, khuyết một là hung. Tam tài trong Thái Ất là ba lớp thông tin về trời, đất, người trong lá số.

Cách cục: xét các cách yểm bách quan tù kích cách đối ở trên. Chủ bị tù bị bách là bất lợi cho ta; khách bị yểm bị kích là bất lợi cho đối phương.

### 6.3 Tam tài và trường đoản toán

Tam tài và trường đoản toán là hai tiêu chí định lượng nhất, nên engine tính được và trình bày rõ. Tam tài kiểm ba lớp thiên địa nhân có mặt đủ trên lá số, trả về đủ hay khuyết. Trường đoản so hai toán với ngưỡng mười một và chín, trả về nhãn trường hoặc đoản cho mỗi bên. Kết quả của cả bốn tiêu chí là dữ kiện tất định, còn việc tổng hợp thành lời đoán thắng bại cụ thể thuộc tầng diễn giải.

Ranh giới engine và AI khi luận Thái Ất. Vị trí Thái Ất, mười sáu thần, tám tướng, các toán, và mọi cách cục nhận diện được là dữ kiện tất định, do engine tính và phải khớp oracle kintaiyi. Phần diễn giải, tức đọc hoà bất hoà, trường đoản, tam tài, và các cách để thành phán đoán về vận hội hay thắng bại, do tầng AI hỗ trợ, luôn trích nguồn từ Kim Kính Thức Kinh và Thống Tông Bảo Giám, gắn nhãn AIDisclosure, và không khẳng định quá mức. Vì Thái Ất luận cái lớn như quốc sự, tầng diễn giải phải thận trọng và nói rõ giới hạn.

---

## 7. Đặc tả engine và schema JSON

### 7.1 Luồng engine

Engine nhận năm dương lịch và mốc thời gian, một cờ chọn kỷ nguyên, và một cờ chọn cấp thời gian trong niên nguyệt nhật thời. Nó chạy tuần tự: tính tích theo cấp đã chọn, rút số cục qua phép chia lấy dư cho bảy mươi hai, an Thái Ất vào cung theo số cục và chiều độn, an mười sáu thần lên vòng, tính kế thần rồi an Văn Xương và Thủy Kích, tính chủ toán khách toán, suy đại tướng tham tướng, nhận diện cách cục, và tính tam tài trường đoản. Kết quả là một đối tượng JSON đầy đủ. Mọi bước tất định, nên bàn cache được theo năm, cấp, kỷ nguyên.

```json
{
  "he": "thai_at",
  "dau_vao": {
    "nam_ce": 2004, "cap": "nien_ke",
    "epoch": "kim_kinh"
  },
  "tich": {
    "tich_nien": 10155921,
    "nhap_cuc": 33, "can_chi": "甲申",
    "duong_don": true
  },
  "thai_at_cung": 1,
  "thap_luc_than": { },
  "bat_tuong": {
    "van_xuong":"...", "thuy_kich":"...",
    "chu_dai_tuong":"...", "khach_dai_tuong":"...",
    "chu_tham_tuong":"...", "khach_tham_tuong":"...",
    "ke_than":"..."
  },
  "cac_toan": {
    "chu_toan":0, "khach_toan":0,
    "chu_truong_doan":"truong", "khach_truong_doan":"doan"
  },
  "cach_cuc": ["掩", "格"],
  "tam_tai": "du",
  "co_truong_phai": {
    "epoch": "kim_kinh",
    "dem_toan": "truoc_thai_at"
  }
}
```

### 7.2 Tập cờ trường phái

Thái Ất có hai cờ then chốt. Cờ epoch chọn mốc kỷ nguyên, đổi tích niên và do đó đổi cả lá số, mặc định Kim Kính. Cờ dem_toan chọn quy tắc đếm toán dừng trước hay sau cung Thái Ất, mặc định dừng trước theo bản cổ điển. Ngoài ra có cờ chọn cấp thời gian niên nguyệt nhật thời, và cờ xử lý dị bản tên thần. Mỗi lá số đóng dấu toàn bộ tập cờ để tái lập và bảo vệ được.

Tiêu chí nghiệm thu engine Thái Ất. Engine đạt yêu cầu khi, với mỗi kỷ nguyên và mỗi cấp thời gian, khớp một trăm phần trăm với thư viện kintaiyi trên tập ca mẫu phủ nhiều năm và nhiều mốc, và khi các phép chia lấy dư trên số tích niên lớn đều có kiểm thử riêng, đặc biệt các ca biên quanh mốc đổi độn và mốc Đông Chí. Vì tích niên là số rất lớn, phải kiểm kỹ tràn số và độ chính xác.

---

Thái Ất Thần Số là hệ Tam Thức vĩ mô nhất: dùng tích niên đếm từ mốc khởi nguyên, qua phép chia lấy dư ra số cục, an Thái Ất trên chín cung và mười sáu thần, suy tám tướng và các toán, rồi luận thắng bại chủ khách qua hoà bất hoà, trường đoản, tam tài, và cách cục. Vì có nhiều mốc kỷ nguyên và bốn cấp thời gian, engine phải cho chọn và đóng dấu vào mọi lá số. Đến đây ba hệ chuyên sâu đã đủ. Tập 5 quay lại nền dùng chung của cả ba hệ, phần lõi lịch pháp và thiên văn. Hiện Thực Hoá Ý Chí.

## 8. Bảng tra mở rộng: chủ khách toán và các điều kiện Thái Ất

Chương này bổ sung ba bảng tra cho phần tính toán và luận đoán Thái Ất, vốn là hệ có nhiều thành phần suy tính nhất trong ba hệ.

### 8.1 Chủ toán, khách toán, và các tướng

Thái Ất luận thắng bại chủ yếu qua so sánh sức chủ và khách, tính bằng các phép toán và đọc qua các tướng. Chủ là bên mình hoặc bên trong, khách là bên đối hoặc bên ngoài.

| Thành phần | Vai trò |
|---|---|
| 主算 Chủ toán | Số tính sức bên chủ, nền để so thắng bại |
| 客算 Khách toán | Số tính sức bên khách, đối chiếu với chủ toán |
| 主大將 Chủ đại tướng | Tướng lớn bên chủ, chủ lực của chủ |
| 客大將 Khách đại tướng | Tướng lớn bên khách, chủ lực của khách |
| 主參將 Chủ tham tướng | Tướng phụ bên chủ, hỗ trợ chủ đại tướng |
| 客參將 Khách tham tướng | Tướng phụ bên khách, hỗ trợ khách đại tướng |

### 8.2 Các thần mục và sao chính

Ngoài chủ khách toán, Thái Ất còn nhiều thần mục và sao dùng trong luận đoán.

| Thành phần | Vai trò |
|---|---|
| 計神 Kế thần | Thần chủ mưu tính, một mốc quan trọng trong bố cục |
| 始擊 Thủy kích | Điểm khởi kích, chủ động thái ban đầu |
| 定目 Định mục | Mục tiêu đã định, mốc để đọc thế |
| 文昌 Văn xương | Sao văn, chủ văn vận và mưu lược |
| 主目 客目 Chủ mục khách mục | Mắt của chủ và của khách, điểm nhìn hai bên |
| 五福 Ngũ phúc | Sao phúc, chủ điều lành |
| 大遊 小遊 Đại du tiểu du | Hai sao du hành, di chuyển theo chu kỳ khác nhau |
| 天乙 地乙 Thiên ất địa ất | Hai ất trên và dưới, cặp mốc trời đất |
| 四神 飛符 Tứ thần phi phù | Bốn thần và phi phù, các thành phần động phụ trợ |

### 8.3 Các điều kiện đặc biệt

Thái Ất có một số điều kiện đặc biệt mô tả thế đứng của Thái Ất và các tướng so với cung, ảnh hưởng lớn tới luận đoán.

| Điều kiện | Ý nghĩa |
|---|---|
| 掩 Yểm | Che, một thành phần bị che khuất, thế bị hạn chế |
| 迫 Bức | Ép, bị dồn sát, thế bức bách |
| 關 Quan | Ải, bị chặn ở cửa ải, khó thông |
| 囚 Tù | Giam, bị giam hãm, thế bế tắc |
| 擊 Kích | Đánh, bị kích hoặc chủ kích, thế đối kháng |

Năm điều kiện yểm bức quan tù kích không phải thành phần đặt thêm, mà là các trạng thái đọc ra từ vị trí tương đối của Thái Ất và các tướng trên cung. Trong engine, sau khi an xong mọi thành phần, một bước kiểm tra các điều kiện này bằng luật vị trí, rồi ghi vào lá số.

## 9. Ví dụ lập bàn mẫu có lời giải

Chương này đi qua một ví dụ lập bàn Thái Ất theo lối tính năm, từng bước. Thái Ất khác hai hệ kia ở chỗ nền là tích niên, một con số đếm năm từ mốc kỷ nguyên, nên bước đầu là tính tích niên. Các con số minh hoạ phương pháp; khi lập trình phải đối chiếu oracle như kintaiyi.

Dữ kiện và cấu hình ví dụ: giả sử cần lập Thái Ất tính năm cho một năm cụ thể. Cấu hình dùng: phép tính năm, mốc kỷ nguyên theo một hệ tích niên đã chọn, và cờ kỷ nguyên đóng dấu vào lá số. Đầu vào chính là năm cần xem, từ đó suy tích niên.

### 9.1 Bước một, tính tích niên

Tích niên là số năm đếm từ mốc kỷ nguyên tới năm cần xem. Lấy năm cần xem trừ đi năm mốc kỷ nguyên theo hệ đã chọn, ra tích niên. Con số này là nền cho mọi bước sau, vì vị trí Thái Ất và các thành phần đều suy từ tích niên qua các phép chia lấy dư.

Mọi thứ trong Thái Ất tính năm đều suy từ tích niên, nên tích niên phải đúng trước đã. Nhưng tích niên phụ thuộc mốc kỷ nguyên, mà các phái dùng mốc khác nhau. Vì thế cờ kỷ nguyên là một cờ trường phái bắt buộc của Thái Ất, ngang tầm quan trọng với phái định cục của Kỳ Môn.

### 9.2 Bước hai, an Thái Ất vào cung

Từ tích niên, qua các phép chia lấy dư theo chu kỳ, suy ra cung mà Thái Ất đóng trong một vòng cung nhất định. Thái Ất đi trong các cung theo một trật tự cố định, bỏ qua cung giữa theo quy tắc riêng. Sau bước này, biết Thái Ất ở đâu, làm mốc để an các thành phần còn lại.

### 9.3 Bước ba, suy các tướng và toán

Từ vị trí Thái Ất, suy vị trí các thành phần: mười sáu thần, tám tướng gồm các cặp chủ khách đại tướng và tham tướng, kế thần, thủy kích, văn xương, và các sao du. Rồi tính chủ toán và khách toán bằng các phép đếm cung theo luật. Hai con số toán này là trục chính để so thắng bại chủ khách.

| Thứ tự | Thành phần suy ra |
|---|---|
| 1 | Vị trí Thái Ất trong cung, từ tích niên |
| 2 | Mười sáu thần và tám tướng chủ khách |
| 3 | Kế thần, thủy kích, văn xương, định mục |
| 4 | Chủ toán và khách toán, tính bằng đếm cung |
| 5 | Các điều kiện yểm bức quan tù kích |

### 9.4 Bước bốn, luận chủ khách thắng bại

So chủ toán và khách toán, xét các tướng chủ khách mạnh yếu, và xét các điều kiện đặc biệt, để luận thế thắng bại giữa hai bên. Trong bối cảnh hiện đại, chủ là bên mình, khách là bên đối, và kết quả luận cho một cách nhìn có cấu trúc về tương quan hai bên ở tầm rộng và dài.

Như hai hệ kia, toàn bộ luồng lập bàn Thái Ất là tất định một khi đã chốt mốc kỷ nguyên. Điểm đặc trưng của Thái Ất là phần suy tính nặng và nền là tích niên thay vì giờ, nên cờ kỷ nguyên là bắt buộc. Khâu luận thắng bại cuối thuộc tầng AI có trích nguồn, tách khỏi khâu tính toán tất định này.


> Tài liệu 4/7 trong bộ Tam Thức của CyberSkill. Phiên bản 1.0. Nội dung mang tính tham khảo tri thức và giáo dục di sản, không phải lời khuyên y tế, pháp lý, hay tài chính. Thái Ất luận cái lớn như vận nước nên phần diễn giải càng phải thận trọng và trích nguồn. Thuật toán và bảng tra cần đối chiếu ít nhất hai nguồn, và kiểm cho từng kỷ nguyên, trước khi khoá vào bản phát hành. Các giá trị thiết kế theo CyberSkill Global Design System v1.3.0.
