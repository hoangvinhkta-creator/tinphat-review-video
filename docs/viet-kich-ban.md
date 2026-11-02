# Bước 0 — Viết kịch bản lời đọc từ link sản phẩm

Người dùng gửi **link trang sản phẩm**. Claude đọc trang, viết kịch bản lời đọc và gửi lại để họ làm voice (ElevenLabs, Vbee, FPT.AI, CapCut… hoặc tự đọc). Kèm theo là **bảng lời ↔ góc quay** để video thô ăn khớp với lời.

## ⚠️ Thương hiệu: luôn là ĐIỆN MÁY TÍN PHÁT

- Công ty là **Điện máy Tín Phát**. Kịch bản, đồ hoạ và lời kêu gọi chỉ nhắc **Điện máy TÍN PHÁT**.
- Link người dùng gửi thường là trang của **nơi khác** (Điện máy XANH, Nguyễn Kim, Thế Giới Di Động, Shopee, trang hãng…). Trang đó **chỉ là nguồn thông số**:
  - **Không bao giờ** nhắc tên trang nguồn, khẩu hiệu, chương trình khuyến mãi hay giá của họ.
  - Không chép nguyên văn câu chữ của họ. Viết lại hoàn toàn bằng giọng Tín Phát.
  - Không dùng ảnh của họ.
- Câu cuối luôn là lời mời ghé **Điện máy TÍN PHÁT** (viết hoa TÍN PHÁT để đồ hoạ tô màu nhấn).
- Trước khi gửi, soát lại: kịch bản **không** có chữ "XANH", "Nguyễn Kim", "Thế Giới Di Động", "TGDĐ", "Điện máy Chợ Lớn"… hay tên trang nguồn nào khác.

## Các bước làm

### 1. Lấy dữ liệu có chọn lọc (đừng chép cả bảng thông số)
Đọc link bằng WebFetch. Cần lấy:
- Tên đầy đủ, hãng, **mã máy**, loại sản phẩm.
- **Phần "Đặc điểm nổi bật"** và chú thích ảnh minh hoạ của hãng. Điều hãng vẽ to nhất, nhắc đầu tiên chính là điểm "ăn tiền" (ví dụ ảnh máy sấy úp ngược trên máy giặt → *tiết kiệm diện tích*).
- Gom **tên công nghệ tiếng Anh** (Reverse Tumbling, Smart Sensor, Inverter, ColourCare…) để chuyển sang tiếng Việt ở bước 2.
- Chỉ 1–2 con số đắt nhất (dung tích, số người dùng, thời gian chế độ nhanh, mức tiết kiệm điện) **đúng như trang ghi**.

Nếu trang chặn đọc hoặc toàn ảnh, xin người dùng dán phần "Đặc điểm nổi bật" vào chat. Không bịa thông số.

Rồi tạo dự án: `./vid new <hang-ma-may>`, ví dụ `./vid new electrolux-edv804h3wc` (chữ thường, không dấu, nối bằng gạch). Điền `product` trong `project.json` (name, model, specs ngắn gọn).

### 2. Dịch "tiếng thuật ngữ" sang "tiếng người Việt"
Mỗi tính năng đi qua 3 nấc: **tính năng → tác dụng thật → câu văn nói**. Người lướt TikTok/Reels nghe "công nghệ cảm biến thông minh" là lướt qua; nghe "lấy ra giũ cái là phẳng" thì dừng lại.

| Tính năng (trang ghi) | Tác dụng thật | Văn nói |
|---|---|---|
| Reverse Tumbling | Lồng đảo chiều, đồ không cuộn cục | "Quần áo được đánh tơi, không xoắn rối thành cục, lấy ra giũ nhẹ là phẳng" |
| Smart Sensor | Cảm biến độ ẩm, tự ngắt | "Máy biết 'canh' đồ vừa khô tới là tự ngắt, giữ vải bền màu" |
| Lắp úp ngược / Stackable | Chồng lên máy giặt | "Lắp úp ngược ngay trên máy giặt, gói gọn góc giặt giũ" |
| Inverter | Ít tốn điện, chạy êm | "Chạy êm ru, tháng này hoá đơn điện nhẹ hẳn" |
| Hygiene / diệt khuẩn | Hơi nóng diệt vi khuẩn | "Sấy diệt khuẩn êm dịu cho da nhạy cảm, đồ em bé cũng yên tâm" |
| Multi Air Flow (tủ lạnh) | Hơi lạnh toả đều | "Ngăn nào cũng lạnh đều, rau để cả tuần vẫn tươi" |
| Quick Wash / Sấy nhanh | Rút ngắn thời gian | "Hôm nào vội đi làm, chọn ngay chế độ nhanh 40 phút là kịp" |

**Cấm văn mẫu dịch thô** kiểu "giúp quần áo trông và cảm thấy tốt nhất" hay "mang lại trải nghiệm vượt trội". Đọc to câu lên: nghe không giống người thật nói thì viết lại.

### 3. Tìm "nỗi đau" để làm hook (giây 1–3)
Không mở bằng "Hôm nay mình review…". Mở bằng **nỗi khổ quen thuộc** khiến người Việt mua món đó, nghe là thấy "nhột":

| Loại sản phẩm | Nỗi đau gợi ý |
|---|---|
| Máy sấy | Mưa nồm, ban công chung cư giăng kín đồ, mùi ẩm mốc, đồ phơi mãi không khô |
| Máy giặt | Giặt tay mỏi lưng, đồ còn mùi, máy cũ rung ầm ầm nửa đêm |
| Tủ lạnh | Rau héo sau 2 ngày, mùi thức ăn lẫn lộn, tủ chật Tết đến không có chỗ |
| Điều hoà | Nóng 40 độ, hoá đơn điện tháng hè giật mình, phòng lạnh không đều |
| TV | Xem bóng đá giật lag, cả nhà tranh remote, màn cũ nhoè chữ |
| Nồi chiên không dầu / bếp | Chiên rán bắn dầu, khói ám bếp, ngại dọn rửa |
| Máy lọc nước / lọc khí | Nước có mùi, nấu nước đun sôi mất công, bụi mịn, con hay hắt hơi |

#### Hook phải GÂY SỐC, không được "hiền"
Người xem quyết định lướt hay ở lại trong **1,5 giây đầu**. Câu "Tạm biệt cảnh ban công giăng kín đồ ngày mưa nồm!" đúng nỗi đau nhưng **quá hiền**: nó kể lại vấn đề chứ không đánh thẳng vào người xem. Hook mạnh phải có ít nhất một trong các yếu tố: **lệnh dừng**, **hậu quả xấu cụ thể**, **câu hỏi chọc thẳng vào người xem**, **nghịch lý**, **con số đắt**.

**7 công thức** (ví dụ máy sấy, cùng một nỗi đau "mưa nồm"):

| # | Công thức | Ví dụ lời đọc | Chữ trên hình (`title`) |
|---|---|---|---|
| 1 | **Lệnh dừng**: "Đừng / Ngừng ngay … nữa!" | "Ngừng ngay việc phơi đồ ngoài ban công ngày nồm!" | pill **DỪNG LẠI** · "Phơi đồ ngày nồm?" |
| 2 | **Hậu quả xấu cụ thể** (chuyện thật hằng ngày) | "Phơi ba ngày vẫn ẩm, mặc vào là mùi chua, ngứa cả người!" | pill **CẢNH BÁO** · "Áo phơi 3 ngày / VẪN BỐC MÙI" |
| 3 | **Câu hỏi chọc thẳng** | "Nhà bạn có đang mặc quần áo… còn ẩm mỗi sáng?" | pill **BẠN CÓ ĐANG** · "mặc đồ còn ẩm?" |
| 4 | **Nghịch lý / gây tò mò** | "Không cần ban công, đồ vẫn khô thơm mỗi ngày – kể cả mưa nồm!" | pill **KHÔNG CẦN** · "ban công / VẪN KHÔ THƠM" |
| 5 | **Sai lầm phổ biến** | "Sai lầm của 9/10 nhà chung cư: phơi đồ trong nhà ngày nồm!" (chỉ dùng tỉ lệ nếu có nguồn, không thì "Sai lầm của rất nhiều nhà chung cư") | pill **SAI LẦM** · "Phơi đồ trong nhà" |
| 6 | **Con số đắt nhất** (đúng thông số trang) | "40 phút! Đúng 40 phút là cả mẻ đồ khô cong." | pill **40 PHÚT** · "ĐỒ KHÔ CONG" |
| 7 | **So sánh trước / sau** | "Trước: ban công như bãi chiến trường. Sau: một góc gọn tinh tươm." | pill **TRƯỚC / SAU** |

Hook theo ngành hàng (chọn công thức hợp, đổi lời):

| Loại | Hook mẫu |
|---|---|
| Máy giặt | "Đừng giặt tay nữa – lưng bạn sẽ cảm ơn đấy!" · "Máy cũ rung ầm ầm lúc nửa đêm? Đến lúc thay rồi!" |
| Tủ lạnh | "Rau mua hôm qua, hôm nay đã héo? Lỗi không phải ở rau!" |
| Điều hoà | "Hoá đơn tiền điện tháng 6 làm bạn giật mình? Xem cái này!" |
| TV | "Xem bóng đá mà hình giật như quay chậm? Bỏ ngay!" |
| Nồi chiên không dầu | "Ngừng chiên rán bắn dầu khắp bếp!" |
| Máy lọc nước / khí | "Nước đun sôi để nguội có thật sự sạch?" (chỉ khi trang có nói về lọc cặn, khuẩn) |

**Quy tắc hook:**
- **3 chữ đầu phải "đánh"** ("Ngừng ngay…", "Phơi ba ngày…", "40 phút!…"). Không chào hỏi, không mở bằng tên hãng.
- **≤ 14 âm tiết**, một hơi đọc. Người làm voice đọc **nhanh, gắt, có nhấn**. Giọng hiền thì cũng mất sức.
- **Nối về sản phẩm trong vòng 5 giây** (câu thứ hai nhắc ngay tên máy và lợi ích).
- **Gây sốc bằng sự thật đời thường, không bằng hù doạ sai.** Không bịa số liệu hay thống kê, không doạ bệnh tật ("gây ung thư", "nhiễm độc") khi trang không nói, không chê hãng hay cửa hàng khác.
- **Chữ trên hình** (`title`) ngắn hơn lời: pill 1–2 chữ in hoa (DỪNG LẠI, CẢNH BÁO, SAI LẦM, 40 PHÚT), 1–2 dòng ≤ 20 ký tự. Dòng cuối là chữ vàng, phần gắt nhất.
- **Luôn viết 3 phương án hook** (3 công thức khác nhau) trong `script.md` để người dùng chọn. Phương án Claude khuyên dùng đặt đầu tiên và ghi lý do.

**Âm thanh và hình đi kèm hook** (tự có, không cần viết): 0,6 giây đầu hình tối dần và tiếng rít dồn lên, rồi **BOOM** cùng chớp trắng, rung hình, tiêu đề bật vào, và lời hook vào ngay sau tiếng nổ. Vì thế hook phải **vào thẳng ý ngay từ chữ đầu**, không cần "à", "này".

### 4. Khớp lời với hình (nghe gì thì phải thấy cái đó)
Mỗi câu gắn một **góc quay**:
- Nói về **gọn, đẹp, tổng thể** → **toàn cảnh** (thấy được cả máy trong không gian).
- Nói về **bảng điều khiển, chế độ** → **cận** ngón tay bấm/xoay núm.
- Nói về **lồng, ngăn, bên trong** → **cận** mở cửa, tay chạm vào bộ phận.
- Câu **kêu gọi cuối** → lùi ra **toàn cảnh chính diện**, giữ yên 5–6 giây (màn kết nằm ở đây).

## Khung kịch bản (35–45 giây, khoảng 150–190 âm tiết)

Mẫu đã dùng thật: `examples/electrolux-edv804h3wc/input/script.txt` (44 giây, 191 âm tiết).

| Đoạn | Thời lượng | Nội dung | Góc quay |
|---|---|---|---|
| **1. Hook + giới thiệu** | 8–10 s | **Hook gây sốc** (xem 7 công thức ở trên), rồi tên máy kèm 1 lợi ích lớn và con số quan trọng nhất | Toàn cảnh, tiến dần vào máy |
| **2. Dễ dùng** | 8–10 s | Bảng điều khiển, chế độ nhanh, app. Đặt vào tình huống đời thường ("hôm nào nhà mình vội đi làm…") | Cận bảng điều khiển + ngón tay |
| **3. Công nghệ cốt lõi** | 8–10 s | 1 công nghệ đã dịch sang tiếng người, kèm 2–3 lợi ích ngắn liên tiếp | Cận bên trong máy |
| **4. Điểm cộng thêm** | 6–8 s | 1–2 tính năng phụ (cảm biến, diệt khuẩn, tiết kiệm điện, khoá trẻ em) | Cận chi tiết / nhãn |
| **5. Slogan + kêu gọi** | 6–7 s | Tên sản phẩm, rồi **slogan 3 vế** (2–3 chữ mỗi vế), rồi "ghé ngay **Điện máy TÍN PHÁT** …" | Toàn cảnh chính diện, giữ yên |

## Quy tắc câu chữ (để đọc hay và để máy căn thời gian chuẩn)

- **Văn nói, thân mật**: "nhà mình", "cực kì nhàn", "về nhé". Câu ngắn, mỗi câu một ý.
- **Dấu phẩy và dấu chấm = chỗ ngắt hơi.** Phần căn thời gian từng từ dựa vào chúng, nên đặt đúng chỗ người đọc sẽ nghỉ.
- **Con số muốn hiện trên hình thì viết bằng chữ số** (8 cân, 40 phút, 3 đến 5 người). **Không** đưa mã máy vào lời đọc, mã máy chỉ hiện trên hình.
- Đơn vị viết theo cách đọc: "8 cân" hoặc "8 ký" (không viết "8kg"), "1,5 lít".
- **Độ dài**: khoảng 4,3 âm tiết/giây, tức 150 âm tiết ≈ 35 s, 190 âm tiết ≈ 44 s. Kiểm tra bằng `./vid count projects/<tên>` và không vượt 200 âm tiết.
- Chỉ nói những gì **quay được** hoặc **đồ hoạ minh hoạ được** (đồ hoạ có icon cho: lắp chồng, gia đình, lồng quay, giọt nước/cảm biến, khiên/diệt khuẩn, đồng hồ, tuyết/làm lạnh, gió, lá/tiết kiệm điện, tia điện, wifi/app, nhiệt độ, âm thanh, lửa/nấu, màn hình, tủ lạnh, áo).
- Không hứa quá ("tốt nhất", "số 1", "tiết kiệm 50%") nếu trang không ghi.

## Lưu và gửi cho người dùng

1. `projects/<tên>/input/script.txt`: **chỉ lời đọc**, không tiêu đề, không ghi chú.
2. `projects/<tên>/script.md` theo mẫu dưới.
3. Gửi người dùng **lời đọc trong một khối dễ copy**, kèm bảng lời ↔ góc quay và ghi chú làm voice. Dừng lại chờ họ gửi voice và video thô.

```markdown
# Kịch bản — <Tên sản phẩm> (<mã máy>) · Điện máy TÍN PHÁT
~<N> giây · <S> âm tiết

## Chọn hook (câu mở đầu)
A. (khuyên dùng – lý do …) <hook A>
B. <hook B>
C. <hook C>

## Lời đọc (copy nguyên khối để làm voice – đang dùng hook A)
<toàn bộ lời đọc>

## Lời ↔ góc quay
| # | Lời | Góc quay | Đồ hoạ dự kiến |
|---|---|---|---|
| 1 | Tạm biệt cảnh ban công… | Toàn cảnh, tiến vào máy | Tiêu đề "TẠM BIỆT" + icon đồ phơi bị gạch |
| … | | | |

## Quay
- Quay dọc, 4K hoặc 1080p, chắc tay; quay liền theo thứ tự bảng; tổng ≥ voice + 2 giây.
- Phần trên cùng khung (~1/5) để trống (trần, kệ hàng), vì đồ hoạ nằm ở đó; máy ở giữa khung.

## Làm voice
- Câu hook: đọc **nhanh, gắt, nhấn mạnh 3 chữ đầu** (như đang cảnh báo); phần còn lại giọng trẻ, sáng, nhanh vừa (1.05–1.1×), nhấn ở con số và ở "TÍN PHÁT".
- Voice bắt đầu nói **ngay từ giây 0** (không để khoảng lặng đầu file); công cụ tự chừa chỗ cho tiếng nổ mở đầu.
- Xuất MP3/WAV, **không chèn nhạc**. Đọc đúng y lời trên; nếu sửa lời khi thu thì gửi lại lời đã sửa.
```
