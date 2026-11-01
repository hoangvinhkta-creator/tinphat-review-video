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

Hook ≤ 12 chữ, đi vào thẳng vấn đề, ví dụ "Tạm biệt cảnh ban công giăng kín đồ ngày mưa nồm!".

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
| **1. Hook + giới thiệu** | 8–10 s | Nỗi đau, rồi tên máy kèm 1 lợi ích lớn và con số quan trọng nhất | Toàn cảnh, tiến dần vào máy |
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

## Lời đọc (copy nguyên khối để làm voice)
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
- Giọng trẻ, sáng, nhanh vừa (1.05–1.1×), nhấn ở con số và ở "TÍN PHÁT".
- Xuất MP3/WAV, **không chèn nhạc**. Đọc đúng y lời trên; nếu sửa lời khi thu thì gửi lại lời đã sửa.
```
