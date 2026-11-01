# Bộ dựng video review — Điện Máy Tín Phát

Repo này biến **link sản phẩm → kịch bản lời đọc** và **video thô + voice → video review dọc 9:16 hoàn chỉnh** (đồ hoạ động trong vùng an toàn, logo chìm, hiệu ứng âm thanh, nhạc nền tự nhỏ khi có lời).

- Quy trình đầy đủ: `.claude/skills/review-video/SKILL.md`. Đọc file này trước khi làm bất cứ việc gì liên quan đến video.
- Viết kịch bản từ link: `docs/viet-kich-ban.md`
- Mọi lệnh: `./vid …` (xem `./vid --help`). Lần đầu trên máy mới: `./setup.sh`
- Ví dụ đã dựng thật: `examples/electrolux-edv804h3wc/` (kịch bản, project.json, scenes.json)

Quy ước:
- **Công ty là Điện máy Tín Phát.** Link sản phẩm có thể từ trang khác (Điện máy XANH…): chỉ lấy thông số, không bao giờ nhắc tên/giá/khuyến mãi của trang đó trong kịch bản hay đồ hoạ.
- Trả lời người dùng bằng tiếng Việt, ngắn gọn.
- Không sửa file gốc của người dùng. Copy vào `projects/<tên>/input/` với tên chuẩn (video.*, voice.*, script.txt).
- Luôn cho người dùng duyệt **kịch bản** (giai đoạn A) và **ảnh tĩnh** (trước khi render) trước khi làm tiếp.
- Tự xem ảnh kiểm tra (`out/contact.png`, `out/stills/*.png`, `out/scan.png`) bằng Read trước khi báo xong.
- Brand: `assets/brand/` (logo.svg, brand.json). Font: `assets/fonts/` (OFL, được phép dùng thương mại).
