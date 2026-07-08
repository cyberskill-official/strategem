# Tài liệu 6 — Kiến trúc kỹ thuật và kế hoạch số hoá

> Bộ tài liệu Tam Thức (三式) của CyberSkill — Tập 6/7
> Phiên bản 1.0 · Slogan: "Turn Your Will Into Real" — Hiện Thực Hoá Ý Chí
> Nội dung mang tính tham khảo tri thức và giáo dục di sản, không phải lời khuyên y tế, pháp lý, hay tài chính.

Tài liệu này gom bốn tập trước thành một kiến trúc phần mềm và một kế hoạch xây dựng. Điểm cốt lõi của thiết kế là tách bạch engine tất định lập bàn khỏi tầng AI diễn giải: engine chạy thuật toán thuần và phải khớp công cụ tham chiếu, còn tầng AI chỉ diễn giải lá số dựa trên văn bản cổ được truy hồi và trích dẫn. Ranh giới giữa hai phần là lá số dạng JSON.

## Thông tin tài liệu

| Trường | Nội dung |
|---|---|
| Nguyên tắc lõi | Engine tất định tách khỏi tầng AI; ranh giới là lá số JSON |
| Chống ảo giác | Diễn giải bắt buộc truy hồi và trích nguồn văn bản cổ, có người kiểm |
| Biểu diễn tri thức | Knowledge graph các thực thể và luật tương tác của ba hệ |
| Mở rộng trường phái | Mọi khác biệt phái là cờ cấu hình, không viết cứng |
| Nghiệm thu | Lập bàn khớp oracle tham chiếu; mốc tiết khí sai dưới một phút |

## Mục lục

1. Kiến trúc phân tầng
2. Engine tất định lập bàn
3. Knowledge graph biểu diễn tri thức
4. Tầng AI diễn giải và RAG
5. Tech stack và khối mã nguồn mở
6. Lộ trình xây dựng theo giai đoạn

---

## 1. Kiến trúc phân tầng

### 1.1 Năm tầng của nền tảng

Nền tảng Tam Thức chia thành năm tầng, từ giao diện người dùng xuống dữ liệu. Cách phân tầng này giữ cho mỗi phần một trách nhiệm rõ, và cho phép thay từng phần mà không phá phần khác. Tầng trên cùng là giao diện web và di động. Dưới nó là tầng API và điều phối. Giữa là lõi tính toán, chia hai nhánh song song: engine tất định lập bàn và tầng AI diễn giải. Dưới cùng là tầng dữ liệu gồm knowledge graph, cơ sở dữ liệu vector, kho văn bản cổ, và cache lá số.

Điểm đáng chú ý trong sơ đồ là lõi tính toán chia hai nhánh đặt cạnh nhau. Nhánh trái là engine tất định, chứa lõi lịch pháp và ba engine lập bàn cùng phần nhận diện cách cục. Nhánh phải là tầng AI diễn giải, chứa truy hồi văn bản cổ, LLM diễn giải, và kiểm chứng người. Hai nhánh nối nhau qua lá số JSON. Cách đặt này phản ánh nguyên tắc thiết kế quan trọng nhất của cả dự án.

### 1.2 Vì sao tách engine và AI

Tách engine tất định khỏi tầng AI là quyết định kiến trúc cốt lõi. Lập bàn là việc tất định: cùng đầu vào luôn cho cùng lá số, và lá số đó phải khớp với công cụ tham chiếu tới từng chi tiết. Nếu để LLM lo việc lập bàn, kết quả sẽ không ổn định và không kiểm chứng được. Ngược lại, diễn giải là việc cần tri thức văn bản và ngôn ngữ, hợp với LLM, nhưng phải có ràng buộc chặt để không bịa. Đặt ranh giới ở lá số JSON cho phép mỗi phần làm đúng việc của nó.

Nguyên tắc một dòng: engine không đoán nghĩa, tầng AI không tự chế số. Lập bàn là thuật toán thuần phải khớp oracle; diễn giải là ngôn ngữ phải trích nguồn văn bản cổ. Ranh giới giữa hai bên là lá số JSON. Đây là nguyên tắc chi phối toàn bộ kiến trúc, và cũng là điều giúp sản phẩm vừa chính xác vừa có trách nhiệm.

### 1.3 Mở rộng và cấu hình trường phái

Bốn tập trước đã cho thấy mỗi hệ có nhiều chỗ các phái làm khác nhau: định cục Kỳ Môn theo ba cách, âm bàn dương bàn, mốc kỷ nguyên Thái Ất, ranh giới giờ Tý ở lõi lịch pháp. Kiến trúc xử lý việc này bằng cách không viết cứng phái nào, mà đưa mọi khác biệt thành cờ cấu hình. Engine nhận một tập cờ, chạy theo cấu hình đó, và đóng dấu toàn bộ cờ đã dùng vào lá số. Nhờ vậy một lá số luôn tái lập được, và người dùng nâng cao có thể chọn phái mình theo.

---

## 2. Engine tất định lập bàn

### 2.1 Lõi lịch pháp làm nền

Engine tất định xây trên lõi lịch pháp mô tả ở tập 5. Lõi này nhận thời điểm, nơi chốn, và cờ lịch pháp, rồi trả về bốn trụ can chi, tiết khí và tam nguyên, giờ chân thái dương, cùng các trạng thái phái sinh. Ba engine lập bàn đều lấy đầu vào từ lõi này, không tự tính lịch riêng. Vì lõi lịch pháp nuôi cả ba hệ, nó là phần phải xây trước tiên và kiểm kỹ nhất.

### 2.2 Ba engine lập bàn

Trên lõi lịch pháp là ba engine lập bàn, mỗi engine theo đặc tả ở tập 2, 3, 4. Engine Lục Nhâm dựng thiên địa bàn, tứ khoá, tam truyền, an thiên tướng. Engine Kỳ Môn định cục rồi bố địa bàn thiên bàn bát môn cửu tinh bát thần, an trực phù trực sử. Engine Thái Ất tính tích niên, an Thái Ất và mười sáu thần, suy tám tướng và các toán. Ba engine độc lập nhau nhưng chung lõi lịch pháp và chung khuôn lá số JSON.

Thiết kế engine thân thiện cache. Mọi bước lập bàn đều tất định, nên kết quả cache được. Một lá số phụ thuộc đầu vào và tập cờ, nên khoá cache là tổ hợp thời điểm, nơi chốn, hệ, và cờ trường phái. Nhờ tính tất định, engine dễ kiểm thử: chỉ cần so đầu ra với oracle tham chiếu trên tập ca mẫu. Đây là lý do tách engine ra khỏi phần xác suất, vì phần tất định mới kiểm thử được chặt chẽ như vậy.

### 2.3 Nhận diện cách cục và lá số JSON

Sau khi dựng các thành phần, engine chạy bước nhận diện cách cục và khoá thể: các cách cát hung của Kỳ Môn, các khoá thể của Lục Nhâm, các cách giữa Thái Ất và tướng. Đây vẫn là bước tất định, dựa trên luật vị trí và quan hệ ngũ hành. Kết quả cuối là một lá số JSON đầy đủ, gồm mọi thành phần đã dựng, mọi cách cục nhận diện được, và tập cờ đã dùng. Lá số JSON này là đầu ra của engine và là đầu vào của tầng AI.

```json
{
  "he": "luc_nham | ky_mon | thai_at",
  "dau_vao": { },
  "lich_phap": { },
  "ban": { },
  "cach_cuc": [ ],
  "co_truong_phai": { }
}
```

Khuôn chung này cho phép tầng AI xử lý cả ba hệ theo một giao diện thống nhất: đọc trường he để biết hệ, đọc ban để biết các thành phần, đọc cach_cuc để biết cách cục, và đọc co_truong_phai để biết cấu hình. Nhờ khuôn thống nhất, thêm một hệ mới không phá vỡ tầng trên.

---

## 3. Knowledge graph biểu diễn tri thức

### 3.1 Các loại node

Tri thức Tam Thức không chỉ là các bảng tra rời, mà là một mạng thực thể có quan hệ với nhau. Cách biểu diễn hợp là knowledge graph, trong đó mỗi thực thể là một node và mỗi luật tương tác là một cạnh. Các loại node gồm thiên can, địa chi, sáu mươi giáp tý, ngũ hành, bát quái, cửu cung, thập nhị thiên tướng, cửu tinh, bát môn, bát thần, mười sáu thần, cách cục, khoá thể, và thần sát. Đây là các khối tri thức mà ba hệ dùng chung hoặc dùng riêng.

### 3.2 Các loại quan hệ

Cạnh trong đồ thị mang các loại quan hệ của tri thức Tam Thức. Nhóm quan hệ ngũ hành gồm sinh và khắc. Nhóm quan hệ địa chi gồm hình, xung, phá, hại, hợp. Nhóm quan hệ vị trí và trạng thái gồm ký cung, thừa, lâm, lạc cung, và vượng tướng hưu tù tử. Mỗi cạnh nối hai node và ghi rõ loại quan hệ, nên đồ thị vừa lưu tri thức vừa lưu luật suy diễn. Khi luận một lá số, có thể duyệt đồ thị để tìm các quan hệ giữa các thành phần.

| Nhóm | Quan hệ | Ý nghĩa |
|---|---|---|
| Ngũ hành | 生 剋 | Sinh, khắc giữa các hành |
| Địa chi | 刑 沖 破 害 合 | Hình, xung, phá, hại, hợp giữa các chi |
| Vị trí | 寄宮 落宮 臨 | Ký cung, lạc cung, lâm cung |
| Trạng thái | 乘 旺相休囚死 | Thừa thần, và sức theo mùa |

### 3.3 Lựa chọn công nghệ lưu trữ

Về công nghệ, knowledge graph lưu được bằng nhiều cách. Một cơ sở dữ liệu đồ thị chuyên như Neo4j cho truy vấn đường đi và quan hệ mạnh. Một biểu diễn RDF theo chuẩn web ngữ nghĩa cho khả năng suy diễn và liên kết dữ liệu. Một property graph tổng quát cho linh hoạt. Lựa chọn tuỳ quy mô và nhu cầu truy vấn, nhưng nguyên tắc chung là node là thực thể và cạnh là luật tương tác, giữ tri thức ở dạng máy duyệt được thay vì chôn trong mã.

Knowledge graph có hai vai. Với engine, nó là nguồn luật ngũ hành và quan hệ chi để nhận diện cách cục, thay vì viết cứng từng luật trong mã. Với tầng AI, nó là một nửa của truy hồi lai: khi diễn giải một lá số, hệ vừa truy hồi văn bản cổ theo ngữ nghĩa, vừa duyệt đồ thị để lấy quan hệ giữa các thành phần. Hai nguồn này bổ sung nhau, giúp diễn giải vừa có gốc văn bản vừa có gốc luật.

---

## 4. Tầng AI diễn giải và RAG

### 4.1 Ranh giới engine và AI qua JSON

Tầng AI diễn giải nhận lá số JSON từ engine và sinh ra lời luận cho người dùng. Điểm mấu chốt là tầng AI không bao giờ tự tính lại lá số, mà chỉ đọc lá số đã có và diễn giải nó. Mọi con số, mọi vị trí, mọi cách cục đều do engine tất định cung cấp. Việc của AI là đọc các dữ kiện đó, truy hồi văn bản cổ liên quan, và viết lời luận dựa trên văn bản đó.

### 4.2 RAG trên văn ngôn văn

Diễn giải dựa trên truy hồi tăng cường, tức RAG, trên kho văn bản cổ. Đây là phần khó vì văn bản gốc là văn ngôn văn, ngôn ngữ cổ khác tiếng Hán hiện đại và khác tiếng Việt. Chiến lược gồm mấy phần. Chia nhỏ văn bản theo đơn vị tự nhiên của thư tịch: theo điều, theo pháp, theo khoá, theo câu. Nhúng đa ngữ để một truy vấn tiếng Việt tìm được văn bản chữ Hán. Lưu song song ba lớp: nguyên văn chữ Hán, bản bạch thoại, và bản dịch. Và truy hồi lai, kết hợp knowledge graph với vector.

Mở rộng ngữ nghĩa thuật ngữ cổ. Một khó khăn riêng của văn ngôn văn là một thuật ngữ có nhiều tầng nghĩa: bản nghĩa gốc, nghĩa dẫn thân mở rộng, nghĩa giả tá mượn âm, và nghĩa theo điển tích. Khi truy hồi, hệ cần mở rộng truy vấn qua các tầng nghĩa này, nếu không sẽ bỏ sót văn bản liên quan. Đây là lý do lưu song song nguyên văn, bạch thoại, và dịch: mỗi lớp bắt một phần ngữ nghĩa, và cùng nhau cho truy hồi đủ.

| Phần | Cách làm |
|---|---|
| Chia nhỏ | Theo điều, pháp, khoá, câu, đúng đơn vị tự nhiên của thư tịch |
| Nhúng đa ngữ | Một không gian nhúng cho cả Hán, Việt, Anh để truy vấn xuyên ngôn ngữ |
| Lưu ba lớp | Nguyên văn chữ Hán, bản bạch thoại, bản dịch, giữ song song |
| Truy hồi lai | Kết hợp duyệt knowledge graph và tìm vector ngữ nghĩa |

### 4.3 Chống ảo giác và người trong vòng lặp

Vì đây là lĩnh vực dễ bịa và dễ bị hiểu sai, tầng AI có ba lớp chống ảo giác. Bắt buộc trích nguồn: mọi lời luận phải dẫn về văn bản cổ cụ thể đã truy hồi, không có nguồn thì không khẳng định. Truy hồi tăng cường: LLM chỉ diễn giải trên văn bản được đưa vào ngữ cảnh, không dựa vào trí nhớ tự do. Người trong vòng lặp: với các phán đoán quan trọng, có bước người kiểm trước khi tới người dùng. Kèm theo là nhãn AIDisclosure cho biết đây là nội dung AI, và thẻ trích dẫn cho biết nguồn.

Không có ba lớp trên, một mô hình ngôn ngữ sẽ sinh lời luận nghe hợp lý nhưng không có gốc, trộn lẫn tri thức thật với bịa đặt, và người dùng không phân biệt được. Với một lĩnh vực di sản như Tam Thức, điều đó vừa sai về tri thức vừa hại về niềm tin. Ba lớp trích nguồn, truy hồi, và người kiểm biến diễn giải từ phán đoán tự do thành phát biểu có căn cứ truy vết được. Đây là điều kiện để sản phẩm có trách nhiệm, không phải tính năng thêm.

---

## 5. Tech stack và khối mã nguồn mở

### 5.1 Các lớp công nghệ

Tech stack theo đúng các tầng kiến trúc. Engine tính toán viết bằng Python hoặc TypeScript, tận dụng các thư viện lịch có sẵn cho phần can chi và tiết khí. Tri thức lưu trên một cơ sở dữ liệu đồ thị cho knowledge graph. Văn bản cổ và nhúng lưu trên một cơ sở dữ liệu vector. Tầng AI dùng một mô hình ngôn ngữ làm lớp cố vấn, bọc trong khung RAG. Giao diện là web cộng di động. Toàn hệ thiết kế để engine cache được và các biến thể trường phái cấu hình bằng cờ.

| Lớp | Công nghệ | Vai trò |
|---|---|---|
| Engine | Python hoặc TypeScript | Lõi lịch pháp và ba engine lập bàn, tất định, cache được |
| Đồ thị | Neo4j, RDF, hoặc property graph | Knowledge graph các thực thể và luật tương tác |
| Vector | Cơ sở dữ liệu vector | Nhúng và truy hồi văn bản cổ theo ngữ nghĩa |
| AI | LLM trong khung RAG | Diễn giải lá số có trích nguồn, có người kiểm |
| Giao diện | Web và di động | Lập bàn tương tác, thư viện song ngữ, bài học |

### 5.2 Khối mã nguồn mở để đánh giá

Có nhiều thư viện mã nguồn mở làm nền cho phần lịch và phần lập bàn, nên đánh giá và tái dùng thay vì viết lại. Cho phần lịch và can chi tiết khí, đáng xem lunar-python và các bản cùng dòng lunar-javascript lunar-php, tyme4py, sxwnl tức Thọ Tinh Thiên Văn Lịch, cnlunar, và bazica. Cho phần lập bàn ba hệ, có các kho trên GitHub cho Kỳ Môn, Lục Nhâm, Thái Ất mà ta đã dùng làm oracle đối chiếu ở các tập trước, như kinqimen, kinliuren, kintaiyi, cùng các công cụ như Nguyên Hanh Lợi Trinh và china95.

Lưu ý giấy phép. Khi tái dùng mã nguồn mở, phải xét giấy phép của từng thư viện. Một số cho dùng thương mại tự do, một số buộc chia sẻ mã nguồn phái sinh, một số hạn chế. Với sản phẩm thương mại của CyberSkill, cần rà giấy phép trước khi nhúng, và ghi rõ nguồn cùng công lao. Các kho lập bàn dùng làm oracle đối chiếu thì vai trò là chuẩn kiểm thử, khác với thư viện nhúng vào sản phẩm, nên cách xử lý giấy phép cũng khác.

| Vai trò | Thư viện hoặc công cụ |
|---|---|
| Lịch và can chi | lunar-python · lunar-javascript · lunar-php · tyme4py · cnlunar · bazica |
| Thiên văn tiết khí | sxwnl 寿星天文历 (VSOP87 rút gọn) |
| Oracle Kỳ Môn | kinqimen · 元亨利貞 · china95 |
| Oracle Lục Nhâm | kinliuren |
| Oracle Thái Ất | kintaiyi |

---

## 6. Lộ trình xây dựng theo giai đoạn

### 6.1 Năm giai đoạn

Lộ trình xây theo năm giai đoạn, mỗi giai đoạn cho một sản phẩm dùng được và làm nền cho giai đoạn sau. Thứ tự này theo đúng thứ tự phụ thuộc kỹ thuật: nền lịch trước, rồi một hệ, rồi ba hệ, rồi tầng AI, rồi nền đào tạo.

Giai đoạn một, MVP nền lịch: xây lõi lịch pháp: can chi, tiết khí, chân thái dương thời. Đối chiếu sxwnl và tyme4py. Đây là nền mọi hệ đứng trên.

Giai đoạn hai, một hệ chuyên sâu: làm engine Lục Nhâm trước, vì nó là hệ nền của ba hệ. Lập bàn khớp oracle, nhận diện tứ khoá tam truyền, an thiên tướng.

Giai đoạn ba, tích hợp ba hệ: thêm engine Kỳ Môn và Thái Ất. Hợp nhất tập cờ trường phái, chuẩn hoá khuôn lá số JSON, và cache lá số cho cả ba.

Giai đoạn bốn, tầng AI diễn giải: dựng kho văn bản cổ, làm RAG với trích nguồn, thêm LLM diễn giải và bước người kiểm. Gắn nhãn AIDisclosure và thẻ trích dẫn.

Giai đoạn năm, nền đào tạo: biến app thành công cụ dạy: bài học tương tác, luyện lập bàn, thư viện cổ song ngữ, và lộ trình học có chứng chỉ.

### 6.2 Tiêu chí nghiệm thu và bài toán khó

Mỗi giai đoạn có tiêu chí nghiệm thu định lượng. Về lập bàn, đầu ra engine phải khớp công cụ tham chiếu như Nguyên Hanh Lợi Trinh và china95 trên một tập ca kiểm đủ lớn. Về thiên văn, mốc tiết khí phải sai dưới một phút so với đài thiên văn. Về diễn giải, mọi lời luận phải có trích dẫn truy vết được. Các tiêu chí này biến tiến độ thành cái đo được, không phải cảm tính.

| Bài toán | Cách tiếp cận |
|---|---|
| Độ chính xác tiết khí | Meeus và VSOP87 rút gọn, hiệu chỉnh delta T, đối chiếu sxwnl |
| Chân thái dương thời | Hiệu chỉnh kinh độ và phương trình thời gian, cờ bật tắt |
| Bất đồng trường phái | Mọi khác biệt thành cờ cấu hình, đóng dấu vào lá số |
| Diễn giải trung thành | RAG bắt buộc trích nguồn, người trong vòng lặp, nhãn AIDisclosure |

---

Kiến trúc nền tảng Tam Thức dựng quanh một nguyên tắc: engine tất định lập bàn tách khỏi tầng AI diễn giải, ranh giới là lá số JSON. Engine chạy lõi lịch pháp và ba engine lập bàn, phải khớp oracle tham chiếu. Tri thức lưu trên knowledge graph các thực thể và luật. Diễn giải dùng RAG trên văn bản cổ, bắt buộc trích nguồn và có người kiểm. Mọi khác biệt phái là cờ. Lộ trình đi từ nền lịch tới một hệ, ba hệ, tầng AI, và nền đào tạo, mỗi bước có tiêu chí nghiệm thu đo được. Tập 7 khép bộ tài liệu bằng phần sản phẩm, tư vấn chiến lược, đào tạo, và giao diện theo Design System. Hiện Thực Hoá Ý Chí.

> Tài liệu 6/7 trong bộ Tam Thức của CyberSkill. Phiên bản 1.0. Nội dung mang tính tham khảo tri thức và giáo dục di sản, không phải lời khuyên y tế, pháp lý, hay tài chính. Các lựa chọn công nghệ và thư viện cần rà giấy phép và đánh giá thực nghiệm trước khi đưa vào sản phẩm. Nguyên tắc tách engine tất định khỏi tầng AI diễn giải, và ràng buộc trích nguồn cho diễn giải, là điều kiện bắt buộc để sản phẩm chính xác và có trách nhiệm. Các giá trị thiết kế theo CyberSkill Global Design System v1.3.0.
