# tinphat-review-video

Bộ công cụ để **Claude Code** dựng video review sản phẩm khung dọc cho **Điện Máy Tín Phát**:

1. **Gửi link sản phẩm** → Claude viết kịch bản lời đọc (35–45 giây) và danh sách cảnh cần quay.
2. **Làm voice + quay video** theo kịch bản.
3. **Gửi video thô + voice** → Claude dựng video 1080×1920 hoàn chỉnh gồm:
   - đồ hoạ động (thẻ thông số, đồng hồ, danh sách tích, chữ lớn, màn kết) bật đúng lúc đọc, nằm trong vùng an toàn, không bị cột nút bên phải hay chú thích bên dưới của TikTok/Reels/Shorts che;
   - logo Tín Phát chìm 10% phủ giữa khung (chống lấy video);
   - hiệu ứng âm thanh khớp đồ hoạ, nhạc nền quảng cáo tự nhỏ xuống khi có lời, âm lượng chuẩn -14 LUFS;
   - tuỳ chọn phụ đề karaoke chữ nảy (font Hepta Slab).

Mọi thứ chạy trên máy bạn và không dùng dịch vụ trả phí. Nhạc và hiệu ứng được tổng hợp bằng code nên không vướng bản quyền.

---

## Cài đặt (một lần, macOS)

Cần **Homebrew** (https://brew.sh) và **Claude Code**.

```bash
git clone https://github.com/<tài-khoản>/tinphat-review-video.git
cd tinphat-review-video
./setup.sh
```
`setup.sh` cài ffmpeg, Node, Python (nếu chưa có), Playwright + Chromium, numpy + scipy (trong `.venv`), rồi chạy `./vid check`. Thấy **"✓ Máy đã sẵn sàng"** là xong.

## Cách dùng

Mở Terminal trong thư mục này và gõ `claude`, rồi nói chuyện bình thường:

**Bước 1 — kịch bản**
> Viết kịch bản review cho sản phẩm này: https://…

Claude trả về lời đọc (copy đi làm voice) và các cảnh cần quay.

**Bước 2 — dựng video**
> Dựng video cho dự án electrolux-edv804h3wc. Video: ~/Downloads/IMG_0568.MOV, voice: ~/Downloads/voice.mp3

Claude gửi ảnh tĩnh để bạn duyệt trước, sau đó dựng và báo đường dẫn file `projects/<tên>/out/<tên>.mp4` (khoảng 5–10 phút cho 45 giây).

**Sửa**: nói theo dạng *"giây 12, thẻ bảng điều khiển, đổi chữ thành …"*, *"nhạc nhỏ lại"*, *"bật phụ đề"*, *"bỏ nhạc để tôi ghép nhạc TikTok"*.

## Đầu vào cần có

| Giai đoạn | Cần | Ghi chú |
|---|---|---|
| Viết kịch bản | **Link sản phẩm** (hoặc dán phần thông số) | Không cần gì khác |
| Dựng video | **Video thô** quay dọc (.mov/.mp4) | iPhone 4K HDR được; quay liền theo thứ tự kịch bản; dài ≥ voice + 2 giây; phần trên khung nên trống (đồ hoạ nằm ở đó) |
| | **Voice** (.mp3/.wav) | Chỉ lời đọc, không nhạc; đọc đúng y kịch bản |
| | **Kịch bản** đúng lời trong voice | Có sẵn nếu đi từ bước 1; nếu đổi lời khi thu thì gửi lời mới |
| | Tên + mã sản phẩm, vài thông số | Có sẵn nếu đi từ bước 1 |

Không cần file SRT. Thời điểm từng từ được tự căn từ voice và kịch bản.

## Lệnh (Claude tự chạy, bạn không cần nhớ)

```
./vid check                         kiểm tra máy
./vid new <tên>                     tạo dự án
./vid count <dự án>                 đếm âm tiết kịch bản, ước lượng thời lượng
./vid <dự án> prep | align | contact | events | stills | render | audio | mix | final | all
```

## Cấu trúc

```
.claude/skills/review-video/SKILL.md   quy trình cho Claude Code
CLAUDE.md                              quy ước chung
docs/viet-kich-ban.md                  cách viết kịch bản từ link
engine/                                prep · align · overlay.html (thư viện đồ hoạ) · render.js · audio · mix · make.py
assets/brand/                          logo.svg, brand.json (tên cửa hàng, màu)
assets/fonts/                          Be Vietnam Pro, Hepta Slab (OFL)
examples/electrolux-edv804h3wc/        ví dụ đã dựng thật
projects/                              dự án của bạn (video/voice/kết quả không đẩy lên GitHub)
```

## Giới hạn

- Thời điểm từng từ được ước lượng từ chỗ ngắt và số âm tiết, có thể lệch khoảng 0,1 giây. Kịch bản phải khớp voice.
- Nhạc tự tổng hợp: sạch bản quyền nhưng đơn giản. Muốn nhạc thư viện thì bảo Claude bỏ nhạc rồi ghép trong CapCut.
- Đã thử trên Linux; cài đặt viết cho macOS (Homebrew). Windows chưa thử.
