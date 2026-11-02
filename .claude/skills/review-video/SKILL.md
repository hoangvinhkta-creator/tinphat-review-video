---
name: review-video
description: Dựng video review sản phẩm khung dọc 9:16 cho Điện Máy Tín Phát. Bước 0 viết kịch bản lời đọc từ link sản phẩm; bước dựng lấy video thô + voice + kịch bản và ra mp4 có đồ hoạ động trong vùng an toàn TikTok/Reels/Shorts, logo chìm, hiệu ứng âm thanh, nhạc nền tự nhỏ khi có lời. Dùng khi người dùng gửi link sản phẩm, nhờ viết kịch bản review, hoặc gửi video + voice để dựng.
---

# Video review sản phẩm — Điện Máy Tín Phát

Mọi lệnh chạy từ thư mục gốc của repo. Lệnh chính: `./vid …` (`--help` để xem tất cả).
Nếu máy chưa cài đủ, chạy `./vid check` và làm theo hướng dẫn in ra (xem README.md).

Quy trình có **hai giai đoạn**, giữa hai giai đoạn là lúc người dùng đi làm voice và quay video.

---

## Giai đoạn A: người dùng gửi link sản phẩm → viết kịch bản

Đọc và làm theo **`docs/viet-kich-ban.md`**.

> ⚠️ Công ty là **Điện máy Tín Phát**. Link thường lấy từ trang khác (Điện máy XANH, Nguyễn Kim, TGDĐ, trang hãng…): chỉ dùng làm nguồn thông số, **không bao giờ** nhắc tên trang đó, giá hay khuyến mãi của họ. Kịch bản và đồ hoạ chỉ nói "Điện máy TÍN PHÁT".

Tóm tắt (4 bước tư duy: lọc dữ liệu → dịch thuật ngữ sang lợi ích nói → hook bằng nỗi đau → khớp lời với góc quay):
1. Đọc link bằng WebFetch, lấy tên, hãng, mã máy và 4–6 tính năng nổi bật. Không tự bịa thông số.
2. `./vid new <hang-ma-may>`, rồi điền `product` vào `projects/<tên>/project.json`.
3. Viết kịch bản 5 đoạn (hook, dễ dùng, công nghệ, điểm cộng, slogan 3 vế + "ghé ngay Điện máy TÍN PHÁT"), khoảng 150–190 âm tiết. **Hook phải gây sốc** (7 công thức trong docs). Luôn đưa **3 phương án hook** để người dùng chọn. Kiểm tra độ dài: `./vid count projects/<tên>`.
4. Lưu `input/script.txt` (chỉ lời đọc) và `script.md` (kịch bản + cảnh cần quay + ghi chú voice).
5. Soát lại: không có tên trang nguồn hay đối thủ, câu cuối mời ghé Điện máy TÍN PHÁT, không văn mẫu dịch thô.
6. Gửi người dùng **kịch bản trong một khối dễ copy**, kèm bảng lời ↔ góc quay. Dừng lại chờ họ gửi voice và video.

Nếu người dùng muốn sửa kịch bản, sửa `input/script.txt` và `script.md`, rồi gửi lại bản mới.

---

## Giai đoạn B: người dùng gửi video thô + voice → dựng video

### B1. Đặt file vào dự án
`projects/<tên>/input/` cần có:
- `video.mov` hoặc `.mp4`: video thô **quay dọc** (HDR của iPhone được, công cụ tự chuyển màu)
- `voice.mp3` hoặc `.wav`: lời đọc, không có nhạc
- `script.txt`: **đúng y lời trong voice**. Nếu người dùng đã đổi lời khi thu thì hỏi lại lời cuối cùng; nếu họ đưa kịch bản kèm ghi chú (mã sản phẩm, đặc điểm nổi bật…) thì chỉ giữ phần lời đọc.

Đổi tên file người dùng đưa thành đúng các tên trên (copy, không sửa file gốc). Chưa có dự án (bỏ qua giai đoạn A) thì `new` trước và điền `product`.

### B2. Chuẩn bị + căn lời
```bash
./vid projects/<tên> prep      # video nền 1080x1920 30fps + voice.wav
./vid projects/<tên> align     # thời gian từng từ → in bảng cụm lời
./vid projects/<tên> contact   # out/contact.png: mỗi giây 1 khung + lưới vùng an toàn
```
- `align` in dòng "ghép được X/Y dấu câu". Nếu tỉ lệ thấp, script.txt có lẽ không khớp voice: hỏi lại người dùng.
- **Dùng Read xem `out/contact.png`** để biết cảnh nào ở giây nào và phần trên khung có trống không.

### B3. Viết `projects/<tên>/scenes.json`
Đồ hoạ là một danh sách thành phần, mỗi thành phần gắn với **từ trong lời đọc**. Mẫu đầy đủ, đã dựng thật: `examples/electrolux-edv804h3wc/scenes.json`.

**Nguyên tắc**
- Mỗi câu hoặc ý chính có **một** thành phần. Thành phần sau tự thay thành phần trước (cùng hàng).
- Chữ trên đồ hoạ **ngắn**: dòng lớn ≤ 16 ký tự, dòng phụ ≤ 26 ký tự. Lấy từ khoá của lời đọc, viết hoa dòng lớn.
- Con số (8 kg, 40', 3–5 người) cho **nảy đúng lúc đọc** (badge.at, valueAt…).
- Mở đầu dùng `title` (phải là thành phần **đầu tiên**, `"at": 0`): khi bật cú mở đầu, tiêu đề tự xuất hiện đúng lúc **BOOM** (chớp trắng + rung + bật vào). Chữ tiêu đề **gắt**: pill 1–2 chữ in hoa (DỪNG LẠI / CẢNH BÁO / SAI LẦM / 40 PHÚT), 1–2 dòng ≤ 20 ký tự, dòng cuối vàng là phần gắt nhất. Kết thúc luôn là `endcard`. Trước endcard nên có `bigwords` cho slogan 3 vế.
- Đồ hoạ nằm ở phần trên khung (y 268–700). Mọi vị trí đã nằm trong vùng an toàn; chỉ `callout.point` là bạn tự chọn: đặt vào chi tiết máy nhìn thấy trên `contact.png` lúc đó, trong khoảng x 80–920, y ≤ 1240.

**Cách ghi thời điểm** (`at`, `until`, `subAt`, `valueAt`…):
- `"chiếc"`: lần đọc đầu tiên của từ, tìm **từ mốc của thành phần trước trở đi** (với các mốc bên trong một thành phần thì tìm từ `at` của nó)
- `"phẳng#2"`: lần thứ 2 · `"sấy nhanh"`: cụm nhiều từ · `"phút@end"`: lúc đọc xong từ · `"Máy-0.2"` / `"8+0.3"`: lệch giây · `12.5`: số giây
- Không tìm thấy từ thì bước `events` báo lỗi kèm tên từ. Sửa cho đúng chữ trong script.txt (có dấu, không phân biệt hoa thường).
- `until` thường **bỏ trống**: thành phần tự tắt khi thành phần kế tiếp cùng hàng (hoặc hàng trên) xuất hiện. Chỉ ghi khi muốn tắt sớm, ví dụ trước một câu chuyển ý không có đồ hoạ.

**Các loại thành phần**

| type | Dùng cho | Trường |
|---|---|---|
| `title` | Câu hook mở đầu | `pill` (nhãn đỏ), `lines` [1–2 dòng, dòng cuối vàng], `icon`?, `strike`? (từ: gạch chéo icon) |
| `namecard` | Tên máy | `label` (MÁY SẤY), `name`, `model`, `badge` {`value`, `unit`, `at`} |
| `chip` | Thông số phụ dưới thẻ tên (hàng 2) | `icon`, `label`, `value`, `valueAt` |
| `callout` | Chỉ vào chi tiết trên máy | `small`, `big`, `point` [x, y] |
| `timer` | Thời gian / chế độ nhanh (vòng tròn bên phải) | `value` ("40'"), `label`, `fillFrom`, `fillTo`, `valueAt` |
| `feature` | Tính năng có icon động | `icon`, `small`, `big`, `sub`, `subAt`, `stamp`?, `stampAt`?, `accent` (red / green / navy) |
| `checklist` | 2–4 lợi ích liên tiếp | `items` [{`text`, `at`}] |
| `bigwords` | Slogan 3 vế | `header`, `words` [{`text`, `at`, `color`: yellow / red}] |
| `endcard` | Màn kết (logo + ĐIỆN MÁY TÍN PHÁT) | `highlightAt` (thường "TÍN"), `sub` (tên máy · mã), `small` ("Ghé ngay") |

Trường chung: `at` (bắt buộc), `until`, `row` (1 = trên cùng, 2 = dưới thẻ hàng 1; `chip` mặc định 2).

**Icon động** (`icon`): `clothesline` (đồ phơi + mưa) · `stack` (máy lật chồng lên máy, cho lắp chồng / tiết kiệm diện tích) · `family` · `drum` (lồng quay, đảo chiều tại `subAt`) · `drop` (giọt nước cạn dần từ `subAt` tới `stampAt`, cho cảm biến độ ẩm / sấy khô) · `shield` (khiên + tích tại `subAt`, cho diệt khuẩn / an toàn / bảo hành) · `clock` · `snow` (làm lạnh, đông đá) · `wind` (gió, quạt, lọc khí) · `leaf` (tiết kiệm điện, eco) · `bolt` (công suất, điện năng) · `wifi` (app, điều khiển từ xa) · `thermo` (nhiệt độ) · `star` · `sparkle` · `sound` (âm thanh, độ ồn) · `check` · `home` · `fire` (nấu, nướng, sưởi) · `screen` (TV, màn hình) · `fridge` · `shirt` (quần áo sạch, phẳng).
Cần icon mới: thêm hàm vào `ICONS` trong `engine/overlay.html` (vẽ canvas trong ô khoảng 150px quanh cx, cy; chỉ phụ thuộc `t`, không dùng Math.random).

Hiệu ứng âm thanh **tự sinh theo scenes.json** (bật khi thẻ hiện, chuông khi số nảy, tích tắc khi đồng hồ chạy…), không cần khai báo.

### B4. Kiểm tra rồi cho người dùng duyệt
```bash
./vid projects/<tên> events            # báo lỗi scenes.json, in mốc từng thành phần
./vid projects/<tên> stills --safe     # ảnh tĩnh có lưới vùng an toàn (tự chọn khoảnh khắc)
./vid projects/<tên> stills 1.9,12.3,42.5   # ảnh duyệt cho người dùng (không lưới)
```
**Dùng Read xem `out/stills/stills_safe.png`** và kiểm tra:
- Không chữ nào chồng lên nhau hay tràn khỏi thẻ.
- Không có gì đè lên chi tiết đang được giới thiệu.
- Mọi thứ nằm trong khung xanh.

Sửa scenes.json rồi xem lại. Xong thì gửi người dùng `out/stills/stills.png` để duyệt **trước khi** dựng cả video (dựng mất vài phút).

### B5. Dựng + trộn tiếng + xuất
```bash
./vid projects/<tên> render   # hình (khoảng 2–4 phút cho 45 s)
./vid projects/<tên> audio    # hiệu ứng + nhạc nền (tự tổng hợp, không vướng bản quyền)
./vid projects/<tên> mix      # trộn: nhạc tự nhỏ khi có lời, chuẩn -14 LUFS, đo độ rõ lời
./vid projects/<tên> final    # → out/<tên>.mp4 + out/scan.png
```
(`all` chạy liền events → stills → render → audio → mix → final.)
- `mix` in "giọng hơn nền …". Thấp nhất phải ≥ 9 dB (mục tiêu 11+); nếu chưa đạt, công cụ tự hạ nhạc 2 dB và trộn lại.
- **Dùng Read xem `out/scan.png`** (mỗi ô 0,5 s) để soát lần cuối, rồi báo người dùng đường dẫn `out/<tên>.mp4`.

### Tuỳ chỉnh thường gặp (project.json)
| Yêu cầu | Sửa |
|---|---|
| Có phụ đề karaoke (Hepta Slab, chữ nảy) | `"subtitles": true`, `"subtitleKeywords": [từ tô đỏ]` |
| Nhạc to / nhỏ hơn | `music.level_db` (mặc định -6; mỗi bước ±2) |
| Hiệu ứng to / nhỏ hơn | `sfx.level_db` (mặc định -12) |
| Nhạc khác | `music.seed` (biến tấu), `music.key` (-5…+6), `music.bpm` (100–128) |
| Bỏ nhạc (tự ghép nhạc TikTok/CapCut) | `music.enabled: false` |
| Logo chìm đậm hơn | `watermark.opacity` (0.10 → 0.15) |
| Giữ màn kết lâu hơn | `tail` (giây sau khi hết lời, mặc định 1.2) |
| Cú mở đầu (rít → BOOM + chớp trắng + rung) | `intro`: `enabled` (mặc định bật), `lead` (giây trước lời, 0.6), `level_db` (độ to tiếng nổ, -3), `flash`, `shake`. Đổi `lead` thì chạy lại từ `prep` |
Sửa xong chạy lại từ bước bị ảnh hưởng: đồ hoạ hoặc phụ đề → `render audio mix final`; chỉ âm thanh → `audio mix final`.

### Người dùng góp ý dạng "giây X, thành phần Y, đổi thành Z"
Tìm thành phần trong scenes.json theo mốc in ra ở `events`, sửa, xem lại bằng `stills <giây X>`, rồi `render audio mix final`.

## Giới hạn cần nói thật với người dùng
- Thời điểm từng từ được ước lượng từ khoảng ngắt và số âm tiết (không có nhận dạng giọng nói), có thể lệch khoảng 0,1 s. Kịch bản phải đúng với voice.
- Nhạc nền tự tổng hợp: sạch bản quyền nhưng đơn giản. Muốn nhạc thư viện thì tắt nhạc và ghép trong CapCut.
- Video thô ngắn hơn voice thì khung cuối được giữ yên. Quay ngang thì bị cắt giữa thành khung dọc.
