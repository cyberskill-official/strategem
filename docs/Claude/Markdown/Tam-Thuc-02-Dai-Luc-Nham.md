# Tài liệu 2 — Đại Lục Nhâm chuyên sâu

> Bộ tài liệu Tam Thức (三式) của CyberSkill — Tập 2/7
> Phiên bản 1.0 · Slogan: "Turn Your Will Into Real" — Hiện Thực Hoá Ý Chí
> Nội dung mang tính tham khảo tri thức và giáo dục di sản, không phải lời khuyên y tế, pháp lý, hay tài chính.

Tài liệu này đặc tả đầy đủ hệ Đại Lục Nhâm (大六壬) ở mức đủ để lập trình một engine khởi khoá tất định và để một người học nắm trọn quy trình lập bàn. Nội dung đi từ cấu trúc thiên địa bàn, qua thuật toán bốn khoá ba truyền và cây quyết định chín tông môn, tới mười hai thiên tướng, hệ khoá thể, và cách luận giải.

## Thông tin tài liệu

| Trường | Nội dung |
|---|---|
| Hệ | Đại Lục Nhâm (大六壬) — chủ Nhân, luận sự việc cụ thể |
| Vai trò kỹ thuật | Engine hệ đầu tiên nên xây, sau lõi lịch pháp tập 5 |
| Đầu vào engine | Thời điểm đã chuẩn hoá (tứ trụ, giờ chiêm) và nguyệt tướng theo trung khí |
| Đầu ra engine | Bàn Lục Nhâm hoàn chỉnh dạng JSON: thiên địa bàn, tứ khoá, tam truyền, thiên tướng, lục thân, khoá thể |
| Oracle đối chiếu | Thư viện mã nguồn mở kinliuren, và bản 元亨利貞, để kiểm thử khớp 100 phần trăm trên tập lớn |

## Mục lục

1. Tổng quan hệ Lục Nhâm và luồng khởi khoá
2. Thiên địa bàn và nguyệt tướng
3. Tứ khoá
4. Chín tông môn và tam truyền
5. Mười hai thiên tướng
6. Hệ khoá thể và lục thân
7. Phương pháp luận giải
8. Đặc tả engine và schema JSON

---

## 1. Tổng quan hệ Lục Nhâm và luồng khởi khoá

### 1.1 Lục Nhâm giải quyết bài toán gì

Đại Lục Nhâm trả lời câu hỏi về một sự việc cụ thể của con người: một vụ việc thành hay bại, một chuyến đi thuận hay trắc trở, một cuộc thương lượng được hay mất, một người vắng mặt bao giờ về. Trong ba hệ Tam Thức, Lục Nhâm cho độ phân giải chi tiết cao nhất về diễn tiến đầu cuối của một sự việc đơn lẻ, nên là hệ có lượng câu hỏi tiềm năng rộng nhất và dễ tiếp cận nhất với người dùng phổ thông.

Tên gọi lục nhâm gắn với sáu can Nhâm trong lục thập hoa giáp, gồm Nhâm Thân (壬申), Nhâm Ngọ (壬午), Nhâm Thìn (壬辰), Nhâm Dần (壬寅), Nhâm Tý (壬子), Nhâm Tuất (壬戌). Can Nhâm thuộc Thủy, và trong quan niệm cổ, Thủy đứng đầu ngũ hành theo câu thiên nhất sinh thủy (天一生水), nên hệ lấy Nhâm làm tên.

### 1.2 Luồng khởi khoá nhìn tổng thể

Toàn bộ quá trình lập một bàn Lục Nhâm, gọi là khởi khoá (起課), là một chuỗi bước tất định. Cho cùng một thời điểm và cùng dữ kiện, chuỗi này luôn cho ra đúng một bàn. Đây là tính chất cốt lõi khiến khâu lập bàn viết được thành thuật toán kiểm chứng, tách hẳn khỏi khâu luận giải.

Năm bước khởi khoá:

1. Xác định can chi ngày, giờ chiêm, và nguyệt tướng theo trung khí.
2. Đặt nguyệt tướng lên cung địa bàn của giờ chiêm để quay thiên bàn, gọi là nguyệt tướng gia thời.
3. Lập bốn khoá từ can ngày và chi ngày.
4. Chạy cây quyết định chín tông môn để rút ra ba truyền.
5. An mười hai thiên tướng khởi từ quý nhân.

Sau năm bước này là bàn hoàn chỉnh, sẵn sàng cho luận giải. Điểm cần nhớ trước là thứ tự: nguyệt tướng và giờ chiêm cho ra thiên bàn, thiên bàn cho ra bốn khoá, bốn khoá qua chín tông môn cho ra ba truyền, cuối cùng phủ thiên tướng lên trên. Sai ở bước sớm sẽ làm sai mọi bước sau, nên engine phải kiểm thử từng bước độc lập.

### 1.3 Thư tịch nền và thư viện đối chiếu

Về thư tịch, bộ tổng hợp có thẩm quyền nhất là Lục Nhâm Đại Toàn (六壬大全), bản trong Khâm định Tứ khố toàn thư, chứa Khoá kinh, Tất pháp phú, và phần luận mười hai tướng. Các bộ quan trọng khác gồm Đại Lục Nhâm chỉ nam (大六壬指南) của Trần Công Hiến, Lục Nhâm thần khoá kim khẩu quyết (六壬神課金口訣), Tất pháp phú (畢法賦) gồm một trăm pháp đoán, và Lục Nhâm đoán án (六壬斷案) của Thiệu Ngạn Hoà. Ở Việt Nam có các bản dịch như Bí tàng Đại Lục Nhâm đại toàn và Lục Nhâm đại toàn hai tập.

Về thư viện mã nguồn mở làm oracle đối chiếu, quan trọng nhất là kinliuren, một package Python lập bàn Đại Lục Nhâm. Cần lưu ý kinliuren không tự tính can chi diễn hoá theo năm tháng ngày giờ, nên phải ghép nó với một thư viện lịch như tyme4py để có đủ tứ trụ. Khi engine của ta lập một bàn, ta so bốn khoá, ba truyền, và thiên tướng với kinliuren trên tập ít nhất năm trăm ca mẫu để bắt lỗi. Tiêu chí nghiệm thu là khớp một trăm phần trăm.

Trong ba hệ, Lục Nhâm có luật tường minh nhất và ít tranh cãi trường phái nhất. Chín tông môn là một chuỗi if/else chặt chẽ, khoá thể là các vị từ kiểm tra trên bàn đã lập. Vì vậy đây là hệ dễ kiểm thử nhất và là lựa chọn hợp lý cho engine hệ đầu tiên sau khi lõi lịch pháp ở tập 5 đã vững.

---

## 2. Thiên địa bàn và nguyệt tướng

### 2.1 Địa bàn cố định và thiên bàn xoay

Bàn Lục Nhâm gồm hai lớp mười hai chi lồng nhau. Địa bàn (地盤) là lớp ngoài, cố định, mười hai chi xếp theo thứ tự cố định quanh vòng. Thiên bàn (天盤) là lớp trong, xoay được, cũng mười hai chi nhưng vị trí thay đổi theo thời điểm. Toàn bộ thông tin của một lần chiêm nằm ở chỗ thiên bàn xoay bao nhiêu so với địa bàn, tức chi nào của thiên bàn nằm đè lên chi nào của địa bàn.

Quy ước vẽ theo la bàn truyền thống: Tý ở dưới, Ngọ ở trên, Mão bên trái, Dậu bên phải, các chi còn lại xếp theo chiều kim đồng hồ. Trong cài đặt phần mềm, cả hai bàn chỉ là hai mảng mười hai phần tử, và phép xoay thiên bàn là một phép cộng mô-đun mười hai. Với cung địa bàn thứ X, chi thiên bàn nằm trên nó bằng nguyệt tướng cộng X trừ giờ chiêm, tính theo mô-đun mười hai.

### 2.2 Nguyệt tướng đổi theo trung khí

Nguyệt tướng (月將) là vị trí biểu kiến của mặt trời trên vòng hoàng đạo, quy về một trong mười hai chi. Điểm dễ nhầm nhất và phải nhấn mạnh cho lập trình: nguyệt tướng đổi tại trung khí (中氣), không đổi tại tiết (節). Đây là khác biệt với ranh giới tháng can chi, vốn lấy theo tiết. Nếu engine lấy nhầm mốc đổi, nguyệt tướng sai, kéo theo cả thiên bàn sai.

Bảng nguyệt tướng theo trung khí:

| Sau trung khí | Nguyệt tướng | Tên tướng | Hoàng kinh |
|---|---|---|---|
| Vũ Thủy 雨水 | 亥 Hợi | 登明 Đăng Minh | 330–360° |
| Xuân Phân 春分 | 戌 Tuất | 河魁 Hà Khôi | 0–30° |
| Cốc Vũ 穀雨 | 酉 Dậu | 從魁 Tòng Khôi | 30–60° |
| Tiểu Mãn 小滿 | 申 Thân | 傳送 Truyền Tống | 60–90° |
| Hạ Chí 夏至 | 未 Mùi | 小吉 Tiểu Cát | 90–120° |
| Đại Thử 大暑 | 午 Ngọ | 勝光 Thắng Quang | 120–150° |
| Xử Thử 處暑 | 巳 Tỵ | 太乙 Thái Ất | 150–180° |
| Thu Phân 秋分 | 辰 Thìn | 天罡 Thiên Cương | 180–210° |
| Sương Giáng 霜降 | 卯 Mão | 太衝 Thái Xung | 210–240° |
| Tiểu Tuyết 小雪 | 寅 Dần | 功曹 Công Tào | 240–270° |
| Đông Chí 冬至 | 丑 Sửu | 大吉 Đại Cát | 270–300° |
| Đại Hàn 大寒 | 子 Tý | 神后 Thần Hậu | 300–330° |

Ranh giới tháng can chi lấy theo mười hai tiết như Lập Xuân, Kinh Trập. Nhưng nguyệt tướng lấy theo mười hai trung khí như Vũ Thủy, Xuân Phân. Hai hệ mốc lệch nhau khoảng nửa tháng. Engine phải dùng đúng trung khí cho nguyệt tướng, và việc tính chính xác thời điểm trung khí thuộc lõi lịch pháp tập 5, dựa trên hoàng kinh mặt trời tính bằng thuật toán thiên văn.

### 2.3 Nguyệt tướng gia thời

Nguyệt tướng gia thời (月將加時) là phép quay thiên bàn. Cách làm: đặt chi nguyệt tướng lên cung địa bàn ứng với giờ chiêm, rồi điền mười một chi còn lại của thiên bàn theo thứ tự chi, thuận chiều. Sau khi đặt xong, mỗi cung địa bàn có một chi thiên bàn nằm trên. Đây là trạng thái gốc để lập bốn khoá.

```
# dia_ban[i] = chi co dinh tai cung i (i = 0..11, theo thu tu Ty..Hoi)
# yue_jiang = chi nguyet tuong; zhan_shi = chi gio chiem
def quay_thien_ban(yue_jiang, zhan_shi):
    off = (index(yue_jiang) - index(zhan_shi)) % 12
    thien_ban = [None]*12
    for i in range(12):
        # chi thien ban nam tren cung dia ban i
        thien_ban[i] = CHI[(i + off) % 12]
    return thien_ban
```

### 2.4 Thiên can ký cung

Vì bàn chỉ có mười hai chi mà can ngày là thiên can, cần một quy tắc gửi can vào một cung chi để can tham gia lập khoá. Đó là thiên can ký cung (天干寄宮). Bốn chi chính Tý Ngọ Mão Dậu không chứa can nào. Quy tắc ký cung cố định như bảng dưới.

| Can | Ký cung | Can | Ký cung |
|---|---|---|---|
| 甲 Giáp | 寅 Dần | 己 Kỷ | 未 Mùi |
| 乙 Ất | 辰 Thìn | 庚 Canh | 申 Thân |
| 丙 Bính | 巳 Tỵ | 辛 Tân | 戌 Tuất |
| 丁 Đinh | 未 Mùi | 壬 Nhâm | 亥 Hợi |
| 戊 Mậu | 巳 Tỵ | 癸 Quý | 丑 Sửu |

Ca quyết: Giáp khoá tại Dần, Ất khoá Thìn, Bính Mậu khoá Tỵ, Đinh Kỷ khoá Mùi, Canh khoá Thân, Tân khoá Tuất, Nhâm khoá Hợi, Quý khoá Sửu. Bốn chính thần Tý Ngọ Mão Dậu không chứa can.

---

## 3. Tứ khoá

### 3.1 Cách lập bốn khoá

Tứ khoá (四課) là bốn cột, mỗi cột gồm một chi hạ thần ở dưới và một chi thượng thần ở trên. Bốn khoá lập từ can ngày và chi ngày theo quy tắc cố định, dùng thiên bàn vừa quay. Quy ước đọc từ phải sang trái, khoá một ở ngoài cùng bên phải.

Bốn bước lập tứ khoá:

1. Khoá một, lấy can ngày ký cung làm hạ thần, chi thiên bàn nằm trên cung đó làm thượng thần.
2. Khoá hai, lấy thượng thần của khoá một, tìm nó trên địa bàn, chi thiên bàn nằm trên đó làm thượng thần mới.
3. Khoá ba, lấy chi ngày làm hạ thần, chi thiên bàn nằm trên làm thượng thần.
4. Khoá bốn, lấy thượng thần của khoá ba làm hạ thần, chi thiên bàn nằm trên làm thượng thần.

### 3.2 Thượng khắc hạ và hạ khắc thượng

Quan hệ giữa thượng thần và hạ thần trong mỗi khoá quyết định vai trò của khoá đó khi lập ba truyền. Có hai quan hệ then chốt. Thượng thần khắc hạ thần gọi là khắc (克). Hạ thần khắc thượng thần gọi là tặc (賊). Xét khắc và tặc trên cả bốn khoá là bước vào cây quyết định chín tông môn. Quan hệ khắc lấy theo ngũ hành sinh khắc, tính trên hành của hai chi.

### 3.3 Ví dụ lập tứ khoá

Lấy ví dụ nguyệt tướng Hợi, giờ Tý, ngày Giáp Tý. Nguyệt tướng gia thời đặt Hợi lên cung Tý. Can ngày Giáp ký cung Dần. Bốn khoá lập ra như sau, đọc phải sang trái.

| Khoá | Hạ thần | Thượng thần | Nguồn hạ thần |
|---|---|---|---|
| Khoá 1 | 甲 (寄寅) | 丑 | Can Giáp ký cung Dần |
| Khoá 2 | 丑 | 子 | Thượng thần khoá 1 |
| Khoá 3 | 子 | 亥 | Chi ngày Tý |
| Khoá 4 | 亥 | 戌 | Thượng thần khoá 3 |

Trong ví dụ này thiên bàn quay sao cho trên Dần là Sửu, trên Sửu là Tý, trên Tý là Hợi, trên Hợi là Tuất. Bốn khoá vì thế là Sửu trên Giáp, Tý trên Sửu, Hợi trên Tý, Tuất trên Hợi.

---

## 4. Chín tông môn và tam truyền

Chín tông môn (九宗門) là chín phương pháp lập ba truyền, tức chín nhánh của một cây quyết định. Từ bốn khoá, engine chạy cây này theo đúng thứ tự ưu tiên để chọn một phép, rồi phép đó cho ra sơ truyền, trung truyền, mạt truyền. Đây là phần logic phức tạp nhất của engine Lục Nhâm, nhưng vì luật tường minh nên cài đặt được thành một chuỗi if/else chặt chẽ.

### 4.1 Cây quyết định chín tông môn

Ba truyền luôn bắt đầu bằng một chi thượng thần, gọi là sơ truyền. Trung truyền là chi thiên bàn nằm trên sơ truyền, mạt truyền là chi thiên bàn nằm trên trung truyền. Đây là quan hệ tương nhân, nên khi đã có sơ truyền thì trung và mạt suy ra tự động. Việc của chín tông môn là chọn đúng sơ truyền.

### 4.2 Bốn nhóm phép chính

Tặc khắc pháp (賊克法). Khi chỉ có một quan hệ tặc hoặc chỉ một quan hệ khắc trong bốn khoá. Nếu chỉ một tặc, lấy chi bị tặc làm sơ truyền, thành khoá Trọng Thẩm (重審). Nếu chỉ một khắc, lấy chi khắc làm sơ truyền, thành khoá Nguyên Thủ (元首). Đây là hai khoá thể cơ bản và phổ biến nhất.

Tỷ dụng pháp (比用法). Khi có từ hai khắc hoặc tặc trở lên, chọn thần tỷ, tức thần cùng âm dương với can ngày. Nếu đúng một thần tỷ khớp, lấy làm sơ truyền, thành khoá Tri Nhất (知一).

Thiệp hại pháp (涉害法). Khi nhiều khắc mà các thần đều tỷ hoặc đều bất tỷ, không phân được bằng tỷ dụng. Khi đó mỗi thần trở về bản gia, đếm số khắc đi qua trên đường về, thần đi qua nhiều khắc nhất làm sơ truyền. Nếu số khắc bằng nhau, lấy thần ở bốn mạnh Dần Thân Tỵ Hợi trước, rồi bốn trọng Tý Ngọ Mão Dậu, thành khoá Thiệp Hại.

Bốn phép vô khắc. Khi bốn khoá không có khắc cũng không có tặc, xét tiếp: nếu có khắc chéo dùng Dao Khắc pháp (遙剋); nếu tứ khoá đủ bốn chi khác nhau dùng Mão Tinh pháp (昴星); nếu chỉ ba chi khác nhau dùng Biệt Trách pháp (別責); nếu can chi đồng vị dùng Bát Chuyên pháp (八專).

### 4.3 Phục ngâm và phản ngâm

Hai trường hợp đặc biệt phải kiểm trước tất cả các phép trên. Phục ngâm (伏吟) xảy ra khi nguyệt tướng trùng giờ chiêm, khiến thiên bàn và địa bàn trùng khít, không chi nào xê dịch. Phản ngâm (返吟) xảy ra khi nguyệt tướng xung giờ chiêm, khiến thiên bàn lệch địa bàn đúng sáu cung. Hai trường hợp này có luật lập ba truyền riêng, dùng hình và xung, nên phải tách ra xử lý trước.

Cây quyết định phải chạy đúng thứ tự: kiểm phục ngâm, rồi phản ngâm, rồi mới tới xét khắc tặc để chọn giữa tặc khắc, tỷ dụng, thiệp hại, và bốn phép vô khắc. Đảo thứ tự sẽ cho ba truyền sai. Đây là chỗ engine dễ sai nhất và cần nhiều ca kiểm thử nhất, nhất là các ca biên phục ngâm, phản ngâm, và bát chuyên.

### 4.4 Pseudocode đầy đủ

```
def lap_tam_truyen(tu_khoa, thien_ban, nguyet_tuong, gio_chiem, can_ngay):
    # Buoc 0: kiem phuc ngam va phan ngam truoc tien
    if nguyet_tuong == gio_chiem:
        return phuc_ngam(tu_khoa, can_ngay)      # 伏吟
    if doi_xung(nguyet_tuong, gio_chiem):
        return phan_ngam(tu_khoa, can_ngay)      # 返吟

    # Buoc 1: liet ke quan he khac (thuong khac ha) va tac (ha khac thuong)
    kc = liet_ke_khac_tac(tu_khoa)   # moi phan tu: (khoa, loai in {KHAC, TAC})

    # Buoc 2: mot khac hoac mot tac -> tac khac phap
    if len(kc) == 1:
        if kc[0].loai == TAC:
            return so_truyen_tu(kc[0], "重審")   # Trong Tham
        else:
            return so_truyen_tu(kc[0], "元首")   # Nguyen Thu

    # Buoc 3: nhieu khac/tac -> ty dung, neu khong phan duoc -> thiep hai
    if len(kc) >= 2:
        ty = [k for k in kc if cung_am_duong(k.thuong_than, can_ngay)]
        if len(ty) == 1:
            return so_truyen_tu(ty[0], "知一")   # Ty dung -> Tri Nhat
        else:
            return thiep_hai(kc, thien_ban)       # 涉害

    # Buoc 4: vo khac vo tac -> bon phep con lai
    if co_dao_khac(tu_khoa, can_ngay):
        return dao_khac(tu_khoa, can_ngay)       # 遙剋: Cao Thi / Dan Xa
    if tu_khoa_du_bon_chi(tu_khoa):
        return mao_tinh(tu_khoa, can_ngay)       # 昴星
    if chi_ba_chi(tu_khoa):
        return biet_trach(tu_khoa, can_ngay)     # 別責
    return bat_chuyen(tu_khoa, can_ngay)         # 八專
```

Ghi chú về các nhánh vô khắc. Dao khắc dùng khi có thần khắc can ngày từ xa, cho khoá Cao Thỉ (蒿矢) hoặc Đàn Xạ (彈射). Mão tinh dùng khi tứ khoá đủ bốn chi, phân theo ngày dương lấy Hổ Thị Chuyển Bồng, ngày âm lấy Đông Xà Yểm Mục. Biệt trách dùng khi chỉ ba chi khác nhau. Bát chuyên dùng khi can và chi ngày cùng ở một cung, gồm các ngày Giáp Dần, Đinh Mùi, Kỷ Mùi, Canh Thân, Quý Sửu.

---

## 5. Mười hai thiên tướng

Sau khi có bốn khoá và ba truyền, engine phủ mười hai thiên tướng (十二天將) lên các cung. Thiên tướng cho tầng nghĩa thứ hai của bàn, bổ sung sắc thái cát hung cho từng chi. Việc an thiên tướng khởi từ quý nhân, rồi các tướng còn lại theo thứ tự cố định.

### 5.1 Khởi quý nhân và ca quyết

Quý nhân (貴人), còn gọi thiên ất quý nhân, là tướng đầu và quan trọng nhất. Vị trí quý nhân xác định theo can ngày qua ca quyết, và phân thành trú quý ban ngày và dạ quý ban đêm.

| Can ngày | Trú quý (ngày) | Dạ quý (đêm) |
|---|---|---|
| 甲 戊 庚 Giáp Mậu Canh | 丑 Sửu | 未 Mùi |
| 乙 己 Ất Kỷ | 子 Tý | 申 Thân |
| 丙 丁 Bính Đinh | 亥 Hợi | 酉 Dậu |
| 壬 癸 Nhâm Quý | 卯 Mão | 巳 Tỵ |
| 辛 Tân | 午 Ngọ | 寅 Dần |

Ca quyết gốc: Giáp Mậu Canh ngưu dương, Ất Kỷ thử hầu hương, Bính Đinh trư kê vị, Nhâm Quý thố xà tàng, lục Tân phùng mã hổ. Trú quý dùng chi thứ nhất, dạ quý dùng chi thứ hai. Có dị bản Giáp dương Mậu Canh ngưu, chuyển quý nhân của Giáp sang Mùi. Mặc định dùng Giáp Mậu Canh chung một nhóm, và để dị bản thành cờ cấu hình.

Chọn trú hay dạ theo giờ chiêm. Theo cách cổ, từ Mão đến Thân dùng trú quý, từ Dậu đến Dần dùng dạ quý, tương ứng khoảng ngày và đêm. Một số phái lấy mốc mặt trời mọc lặn thực tế. Engine nên để ngưỡng ngày đêm thành tham số, mặc định theo khoảng Mão Thân.

### 5.2 Thuận bố và nghịch bố

Sau khi an quý nhân, mười một tướng còn lại xếp theo thứ tự cố định, nhưng chiều xếp phụ thuộc vị trí quý nhân trên địa bàn. Nếu quý nhân lâm các cung Hợi Tý Sửu Dần Mão Thìn thì thuận bố, tức xếp thuận chiều. Nếu lâm các cung Tỵ Ngọ Mùi Thân Dậu Tuất thì nghịch bố, xếp ngược chiều.

Thứ tự cố định của mười hai tướng sau quý nhân là: Quý nhân, Đằng xà, Chu tước, Lục hợp, Câu trần, Thanh long, Thiên không, Bạch hổ, Thái thường, Huyền vũ, Thái âm, Thiên hậu. Cài đặt bằng một mảng cố định, an quý nhân vào cung của nó, rồi điền tiếp theo chiều đã xác định.

### 5.3 Cát tướng và hung tướng

Mười hai tướng chia thành cát và hung, dùng khi luận. Cát tướng gồm Quý nhân, Lục hợp, Thanh long, Thiên hậu, Thái âm, Thái thường. Hung tướng gồm Đằng xà, Chu tước, Câu trần, Huyền vũ, Bạch hổ. Thiên không ở giữa, thiên về bất lợi.

| Tướng | Cát hung | Loại việc chủ |
|---|---|---|
| 貴人 Quý nhân | Cát | Quý nhân giúp đỡ, quan chức, việc lớn |
| 螣蛇 Đằng xà | Hung | Kinh sợ, quái dị, việc rối |
| 朱雀 Chu tước | Hung | Văn thư, tin tức, khẩu thiệt, kiện tụng |
| 六合 Lục hợp | Cát | Hợp tác, hôn nhân, trung gian |
| 勾陳 Câu trần | Hung | Tranh chấp, ràng buộc, đình trệ |
| 青龍 Thanh long | Cát | Tài lộc, hỷ sự, thăng tiến |
| 天空 Thiên không | Bất lợi | Hư dối, trống rỗng, thất tín |
| 白虎 Bạch hổ | Hung | Tật bệnh, tang thương, đường xa, tranh đấu |
| 太常 Thái thường | Cát | Ăn uống, y phục, lễ nghi, ban thưởng |
| 玄武 Huyền vũ | Hung | Trộm cắp, mất mát, ẩn khuất, lừa dối |
| 太陰 Thái âm | Cát | Ẩn giấu, nữ nhân, riêng tư, che chở |
| 天后 Thiên hậu | Cát | Nữ nhân, tình cảm, hôn nhân, âm trợ |

---

## 6. Hệ khoá thể và lục thân

### 6.1 Khoá thể là gì

Khoá thể (課體) là tên gọi phân loại một bàn Lục Nhâm theo hình thái của nó. Sau khi lập xong bốn khoá ba truyền, bàn sẽ khớp một hoặc vài khoá thể trong khoảng sáu mươi tư khoá thể truyền thống. Mỗi khoá thể có một điều kiện định nghĩa và một hướng đoán đi kèm. Về mặt lập trình, nhận diện khoá thể là chạy một loạt vị từ kiểm tra trên bàn đã lập, giống một rule engine.

Khoá thể chia hai lớp. Lớp thứ nhất là các khoá thể gắn thẳng với phép lập ba truyền, như Nguyên Thủ từ một khắc, Trọng Thẩm từ một tặc, Tri Nhất từ tỷ dụng, Thiệp Hại, Mão Tinh, Biệt Trách, Bát Chuyên, Phục Ngâm, Phản Ngâm. Lớp thứ hai là các khoá thể nhận từ hình thái tổng thể của bàn, kiểm tra trên bốn khoá, ba truyền, thiên tướng, và thần sát.

### 6.2 Các khoá thể chính

| Khoá thể | Điều kiện nhận (rút gọn) | Hướng đoán |
|---|---|---|
| 元首 Nguyên Thủ | Một thượng khắc hạ, dùng khắc làm sơ | Việc thuận theo lẽ chính, đầu mối rõ |
| 重審 Trọng Thẩm | Một hạ khắc thượng, dùng tặc làm sơ | Việc do dưới phát, nên xét kỹ lại |
| 知一 Tri Nhất | Nhiều khắc, chọn tỷ làm sơ | Nhiều lối, chọn bên gần mình |
| 涉害 Thiệp Hại | Nhiều khắc đều tỷ hoặc đều bất tỷ | Việc nhiều trở ngại, lội qua hại |
| 三光 Tam Quang | Ba truyền và can chi đều vượng cát | Việc sáng sủa, nhiều thuận lợi |
| 三陽 Tam Dương | Cách cục dương khí thịnh | Hướng lên, tiến tới tốt |
| 龍德 Long Đức | Thanh long thừa thần cát | Có phúc trợ, hỷ sự |
| 鑄印 Chú Ấn | Cách ấn thụ thành tựu | Nhậm chức, được ấn tín, danh vị |
| 斬關 Trảm Quan | Có chi chủ vượt ải | Vượt trở ngại, xuất hành gấp |
| 閉口 Bế Khẩu | Cách khẩu bị bịt | Việc khó nói, bế tắc thông tin |
| 遊子 Du Tử | Cách người đi xa | Đi xa, xa cách, phiêu bạt |

Truyền thống liệt khoảng sáu mươi tư khoá thể. Riêng Nguyên Thủ, do điều kiện rộng, chiếm phần lớn số bàn, khoảng một trăm mười lăm trên bảy trăm hai mươi bàn ngày dương. Engine nên nhận diện tất cả các khoá thể mà bàn khớp, vì một bàn có thể mang nhiều khoá thể cùng lúc, rồi tầng luận giải chọn khoá thể nào nổi bật để dẫn dắt lời đoán. Danh sách đầy đủ và điều kiện chi tiết được số hoá thành bảng dữ liệu, đối chiếu với Lục Nhâm Đại Toàn và Tất pháp phú.

### 6.3 Lục thân và dụng thần

Lục thân (六親) là sáu quan hệ thân thuộc, gán theo quan hệ ngũ hành giữa một chi và can ngày hoặc chủ thể. Đây là cách Lục Nhâm quy loại việc và người vào bàn.

| Quan hệ với ta | Lục thân | Loại việc và người tiêu biểu |
|---|---|---|
| Sinh ra ta | 父母 Phụ mẫu | Cha mẹ, bề trên, nhà cửa, giấy tờ, chỗ dựa |
| Ta sinh ra | 子孫 Tử tôn | Con cháu, cấp dưới, phúc lộc, giải cứu |
| Khắc ta | 官鬼 Quan quỷ | Quan chức, chồng, bệnh tật, mối lo, đối thủ |
| Ta khắc | 妻財 Thê tài | Vợ, tiền của, tài sản, thứ mình nắm |
| Cùng hành với ta | 兄弟 Huynh đệ | Anh em, đồng nghiệp, đối tác ngang, cạnh tranh |

Dụng thần (用神) là chi đại diện cho điều đang hỏi, chọn theo loại việc qua lục thân. Hỏi tài lộc lấy thê tài làm dụng thần, hỏi công danh lấy quan quỷ, hỏi con cái lấy tử tôn, hỏi cha mẹ nhà cửa lấy phụ mẫu. Sau khi chọn dụng thần, người luận xét trạng thái của nó trên bàn: nó ở khoá nào, truyền nào, thừa tướng gì, vượng hay suy, có bị không vong hay hình xung không. Đây là trục chính của luận giải.

---

## 7. Phương pháp luận giải

Luận giải Lục Nhâm là đọc bàn đã lập để trả lời câu hỏi. Khác với khâu lập bàn tất định, khâu này cần tri thức, ngữ cảnh, và kinh nghiệm, nên trong kiến trúc phần mềm nó thuộc tầng diễn giải có AI hỗ trợ, luôn dựa trên bàn do engine lập và trên tri thức có nguồn.

Đọc bốn khoá trước. Khoá một hạ thần là mình, chủ thể, người hỏi. Khoá ba hạ thần là đối phương, khách thể, việc bên kia. Xét quan hệ giữa hai bên qua khắc tặc và ngũ hành cho biết thế của mình so với đối phương. Rồi đọc ba truyền theo trục thời gian: sơ truyền là phát đoan, nguyên nhân, chỗ khởi; trung truyền là quá trình, diễn biến; mạt truyền là quy kết, kết cục. Ba truyền hợp lại vẽ ra đường đi đầu giữa cuối của sự việc.

Bốn lớp thông tin khi luận:

1. Dụng thần và trạng thái của nó, tức điều đang hỏi mạnh hay yếu, được trợ hay bị khắc.
2. Ba truyền như dòng thời gian của việc.
3. Thiên tướng thừa trên các chi chủ chốt, cho sắc thái cát hung và loại việc.
4. Thần sát và các yếu tố phụ như không vong, vượng tướng hưu tù, trường sinh, hình xung phá hại hợp.

Yếu tố phụ tích hợp thông tin người hỏi. Niên mệnh là bản mệnh theo năm sinh, hành niên là vận theo tuổi, hai yếu tố này nối lá số với người cụ thể. Không vong theo tuần giáp làm suy điều nó chạm. Vượng tướng hưu tù tử theo mùa cho biết sức của mỗi chi. Hình xung phá hại hợp giữa các chi thêm sắc thái xung đột hay hoà hợp. Tất pháp phú tổng kết một trăm pháp đoán cụ thể, ví dụ pháp thứ nhất nói tiền sau dẫn theo lên dời tốt, pháp hai mươi ba nói bên cầu việc ta thì việc theo chi truyền, pháp hai mươi tư nói ta cầu việc bên thì việc theo can truyền. Những pháp này là tri thức luật hoá được, nên số hoá thành cơ sở tri thức có nguồn cho tầng diễn giải.

Ranh giới engine và AI khi luận. Bàn và mọi dữ kiện suy ra tất định từ bàn, gồm khoá thể, lục thân, không vong, vượng suy, do engine tính và phải khớp oracle. Phần diễn giải văn xuôi, ghép các lớp thông tin thành lời đoán cho câu hỏi cụ thể, do tầng AI hỗ trợ, nhưng luôn trích nguồn từ Tất pháp phú, Khoá kinh, và các bộ luận, không khẳng định chắc chắn quá mức, và luôn gắn nhãn AIDisclosure theo hệ thiết kế CyberSkill. Chi tiết cơ chế ở tập 6.

---

## 8. Đặc tả engine và schema JSON

### 8.1 Luồng engine

Engine nhận đầu vào là thời điểm đã chuẩn hoá, gồm tứ trụ và giờ chiêm, cùng nguyệt tướng tính theo trung khí và một số cờ trường phái. Nó chạy tuần tự: quay thiên bàn bằng nguyệt tướng gia thời, lập bốn khoá, chạy cây chín tông môn để rút ba truyền, an mười hai thiên tướng, tính lục thân và các yếu tố phụ, nhận diện khoá thể. Kết quả là một đối tượng JSON đầy đủ. Mọi bước đều thuần tất định, nên bàn có thể cache theo khoá gồm thời điểm làm tròn, kinh độ, và tập cờ.

```json
{
  "he": "luc_nham",
  "dau_vao": {
    "datetime": "...", "tz": "+07:00",
    "kinh_do": 106.7, "chan_thai_duong_thoi": true
  },
  "tu_tru": { "nam":"甲辰", "thang":"丙寅",
              "ngay":"甲子", "gio":"甲子" },
  "nguyet_tuong": "亥",
  "gio_chiem": "子",
  "tu_khoa": [
    ["丑", "甲"],
    ["子", "丑"],
    ["亥", "子"],
    ["戌", "亥"]
  ],
  "tam_truyen": {
    "so":"...", "trung":"...", "mat":"...",
    "phep":"賊克/元首"
  },
  "thien_tuong": [ ],
  "luc_than": [ ],
  "khoa_the": ["元首"],
  "khong_vong": ["戌", "亥"],
  "co_truong_phai": {
    "quy_nhan_variant": "giap_mau_canh",
    "chan_thai_duong_thoi": true
  }
}
```

### 8.2 Cờ trường phái

Dù Lục Nhâm ít dị bản hơn hai hệ kia, vẫn có vài chỗ khác nhau giữa các phái mà engine phải cho cấu hình và ghi rõ trong mỗi bàn. Ba cờ chính: quy tắc quý nhân, chọn giữa Giáp Mậu Canh chung nhóm hay tách Giáp; ngưỡng ngày đêm cho trú dạ quý; và cách tính vòng trường sinh, theo âm dương thuận nghịch hay theo ngũ hành đồng sinh, nơi Thủy Thổ cùng cung. Mỗi bàn xuất ra phải đóng dấu tập cờ đã dùng để kết quả tái lập được và có thể bảo vệ khi đối chiếu.

Tiêu chí nghiệm thu engine Lục Nhâm. Engine đạt yêu cầu khi khớp một trăm phần trăm với kinliuren và bản Nguyên Hanh Lợi Trinh trên ít nhất năm trăm ca mẫu, và khi mọi nhánh của chín tông môn đều có ca kiểm thử đơn vị riêng, đặc biệt các ca biên phục ngâm, phản ngâm, và bát chuyên. Đây là điều kiện chuyển pha trong lộ trình ở tập 6.

---

Đại Lục Nhâm là hệ Tam Thức có luật lập bàn tường minh nhất: nguyệt tướng gia thời cho thiên bàn, bốn khoá từ can chi ngày, chín tông môn rút ba truyền, mười hai thiên tướng phủ lên trên, rồi khoá thể và lục thân dẫn vào luận giải. Toàn bộ khâu lập bàn viết được thành engine tất định, kiểm thử bằng oracle mã nguồn mở. Đây là hệ hợp lý để xây engine đầu tiên. Tập 3 chuyển sang Kỳ Môn Độn Giáp. Hiện Thực Hoá Ý Chí.

## 9. Bảng tra mở rộng: chín pháp lập tam truyền và các khoá thể

Chương này bổ sung hai bảng tra đầy đủ hơn cho phần lập tam truyền và phân loại khoá thể, để engine và người học có tham chiếu gần trọn vẹn. Bảng đầu liệt kê chín pháp lập tam truyền cùng điều kiện áp dụng, đúng thứ tự cây quyết định. Bảng sau liệt kê các khoá thể có tên cùng điều kiện định nghĩa.

### 9.1 Chín pháp lập tam truyền

Tam truyền rút ra theo một cây quyết định: xét các điều kiện theo thứ tự, gặp điều kiện nào thoả trước thì dùng pháp đó. Thứ tự này quan trọng vì nhiều lá số thoả nhiều điều kiện, và chỉ điều kiện đầu tiên thoả mới quyết định pháp dùng.

| Thứ tự | Pháp | Điều kiện áp dụng |
|---|---|---|
| 1 | 賊剋法 Tặc khắc | Có thần trên khắc thần dưới (tặc) hoặc dưới khắc trên (khắc); lấy thần khắc làm sơ truyền |
| 2 | 比用法 Tỷ dụng | Có nhiều chỗ khắc; lấy chỗ khắc cùng âm dương với ngày can làm sơ truyền |
| 3 | 涉害法 Thiệp hại | Nhiều chỗ khắc cùng âm dương; lấy chỗ đi qua nhiều cung khắc hại nhất |
| 4 | 遙剋法 Dao khắc | Không có tặc khắc trực tiếp; lấy thần khắc nhật can từ xa, hoặc nhật can khắc từ xa |
| 5 | 昴星法 Mão tinh | Không tặc khắc, không dao khắc; dùng phép Mão tinh, lấy theo Dậu và cung tương ứng |
| 6 | 別責法 Biệt trách | Ngày không đủ bốn khoá riêng biệt; lấy theo can hợp hoặc chi tam hợp |
| 7 | 八專法 Bát chuyên | Ngày Bát chuyên, can chi cùng một nhà; lập truyền theo phép riêng bát chuyên |
| 8 | 伏吟法 Phục ngâm | Nguyệt tướng gia lên chính thời, thiên địa bàn trùng nhau; lập theo phép phục ngâm |
| 9 | 返吟法 Phản ngâm | Nguyệt tướng đối xung với thời, thiên bàn đối chiếu địa bàn; lập theo phép phản ngâm |

Chín pháp trên không phải chín lựa chọn ngang hàng, mà là một chuỗi điều kiện xét theo thứ tự. Trong engine, đây là một chuỗi rẽ nhánh: kiểm tặc khắc trước, không có thì xét dao khắc, rồi Mão tinh, và các trường hợp đặc biệt phục ngâm phản ngâm bát chuyên biệt trách xét theo dạng ngày. Mỗi nhánh cần ca kiểm thử riêng, đặc biệt ba dạng đặc biệt cuối vì chúng dễ sai nhất.

### 9.2 Các khoá thể có tên

Khoá thể là tên gọi phân loại một lá số theo hình thái tổng thể, giúp nắm nhanh tính chất cuộc hỏi. Bảng sau liệt kê các khoá thể thường gặp cùng điều kiện định nghĩa. Một lá số có thể mang nhiều tên khoá thể chồng nhau.

| Khoá thể | Điều kiện định nghĩa |
|---|---|
| 元首課 Nguyên thủ | Chỉ một chỗ khắc, dưới khắc trên, lấy làm sơ truyền; khoá thuần và thuận |
| 重審課 Trọng thẩm | Chỉ một chỗ khắc, trên khắc dưới (tặc); cần xét kỹ, việc có trở lực |
| 知一課 Tri nhất | Nhiều chỗ khắc, dùng tỷ dụng lấy một chỗ cùng âm dương; chọn một mối chính |
| 涉害課 Thiệp hại | Lập truyền theo thiệp hại; việc qua nhiều trở ngại mới thành |
| 遙剋課 Dao khắc | Lập truyền theo dao khắc; tác động từ xa, gián tiếp |
| 昴星課 Mão tinh | Lập truyền theo Mão tinh; cuộc hỏi bất định, cần nương phép riêng |
| 別責課 Biệt trách | Khoá không đủ bốn, lập theo biệt trách; việc thiếu đầu mối rõ |
| 八專課 Bát chuyên | Ngày bát chuyên can chi cùng nhà; việc trong ngoài lẫn, khó phân |
| 伏吟課 Phục ngâm | Thiên địa bàn trùng; việc ngưng trệ, ẩn phục, chưa động |
| 返吟課 Phản ngâm | Thiên bàn đối xung địa bàn; việc đảo lộn, phản phục, đổi chiều |
| 三光課 Tam quang | Ba truyền đều gặp cát tướng cát thần; cuộc sáng sủa, thuận lợi |
| 三陽課 Tam dương | Ba truyền theo thế dương tiến; việc hướng lên, phát triển |

## 10. Ví dụ lập bàn mẫu có lời giải

Chương này đi qua một ví dụ lập bàn Lục Nhâm hoàn chỉnh, từng bước, để minh hoạ toàn bộ luồng đã mô tả ở các chương trước. Ví dụ chọn một thời điểm cụ thể và dựng lá số theo đúng thứ tự engine sẽ chạy. Các con số ở đây minh hoạ phương pháp; khi lập trình, mọi bước phải đối chiếu oracle.

Dữ kiện ví dụ: giả sử cuộc hỏi vào ngày có can chi ngày là Giáp Tý, giờ hỏi là giờ Ngọ, và nguyệt tướng đang dùng là Hợi, tức tướng Đăng Minh. Đây là ba dữ kiện đầu vào cho bước lập thiên địa bàn: nhật can chi để dựng bốn khoá, giờ để gia nguyệt tướng, và nguyệt tướng để quay thiên bàn.

### 10.1 Bước một, lập thiên địa bàn

Địa bàn cố định mười hai chi theo vị trí chuẩn. Thiên bàn quay bằng cách gia nguyệt tướng lên cung giờ hỏi: đặt nguyệt tướng Hợi lên cung Ngọ, rồi các chi còn lại theo thứ tự thuận mà xếp lên các cung địa bàn. Sau khi gia xong, mỗi cung địa bàn mang một chi thiên bàn ở trên. Đây là nền để đọc bốn khoá và an thiên tướng.

Gia nguyệt tướng là phép quay thiên bàn: nguyệt tướng đặt lên cung của giờ hỏi, các chi khác theo thứ tự thuận Tý Sửu Dần Mão mà rải tiếp. Với ví dụ này, Hợi lên Ngọ nghĩa là thiên bàn lệch so với địa bàn một số cung cố định, và độ lệch đó áp cho cả mười hai chi.

### 10.2 Bước hai, dựng bốn khoá

Bốn khoá dựng từ can và chi ngày. Khoá một lấy từ nhật can, khoá hai từ thần trên khoá một, khoá ba từ nhật chi, khoá bốn từ thần trên khoá ba. Với ngày Giáp Tý: can Giáp gửi cung tương ứng, chi Tý ở cung Tý, và từ hai gốc này đọc lên thiên bàn để lấy bốn thần của bốn khoá.

| Khoá | Gốc | Cách lấy thần trên |
|---|---|---|
| Khoá 1 | Nhật can Giáp | Thần thiên bàn trên cung gửi của can Giáp |
| Khoá 2 | Thần trên khoá 1 | Thần thiên bàn trên cung của khoá 1 |
| Khoá 3 | Nhật chi Tý | Thần thiên bàn trên cung Tý |
| Khoá 4 | Thần trên khoá 3 | Thần thiên bàn trên cung của khoá 3 |

### 10.3 Bước ba, rút tam truyền

Áp cây quyết định chín pháp ở chương chín. Xét bốn khoá xem có chỗ khắc không: nếu có một chỗ dưới khắc trên hoặc trên khắc dưới, dùng tặc khắc, lấy thần khắc làm sơ truyền. Từ sơ truyền, theo thiên bàn lấy trung truyền, rồi từ trung truyền lấy mạt truyền. Ba truyền là trục thời gian của cuộc hỏi: sơ là khởi đầu, trung là diễn biến, mạt là kết cục.

Trong ví dụ, bước đầu luôn là kiểm tặc khắc. Chỉ khi không có tặc khắc mới xuống dao khắc, rồi Mão tinh, rồi các dạng đặc biệt. Việc ghi rõ pháp nào được dùng là một phần của lá số JSON, vì nó quyết định cách đọc và giúp kiểm chứng với oracle.

### 10.4 Bước bốn, an thiên tướng và đọc khoá thể

An mười hai thiên tướng lên thiên bàn, khởi từ Quý Nhân theo trú dạ và theo chi ngày, rồi rải mười một tướng còn lại theo chiều thuận nghịch tuỳ dương quý hay âm quý. Sau khi phủ thiên tướng, đọc khoá thể: xét hình thái tổng thể của lá số so với bảng khoá thể ở chương chín để gọi tên. Cuối cùng, kết hợp ba truyền, thiên tướng trên mỗi truyền, và khoá thể để luận cuộc hỏi theo phương pháp ở chương bảy.

Ví dụ này cho thấy toàn bộ luồng lập bàn Lục Nhâm là tất định: từ ba dữ kiện đầu vào, mọi bước sau đều theo luật rõ, không có chỗ tuỳ ý. Nhờ vậy engine dựng lại đúng lá số này mọi lần, và người học luyện lập bàn có thể so từng bước với đáp án. Chỉ khâu luận nghĩa cuối mới cần diễn giải, và theo kiến trúc ở tập 6, khâu đó thuộc tầng AI có trích nguồn, tách khỏi khâu lập bàn tất định này.


> Tài liệu 2/7 trong bộ Tam Thức của CyberSkill. Phiên bản 1.0. Nội dung mang tính tham khảo tri thức và giáo dục di sản, không phải lời khuyên y tế, pháp lý, hay tài chính. Thuật toán và bảng tra cần đối chiếu ít nhất hai nguồn trước khi khoá vào bản phát hành. Các giá trị thiết kế theo CyberSkill Global Design System v1.3.0.
