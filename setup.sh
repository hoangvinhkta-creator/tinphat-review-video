#!/usr/bin/env bash
# Cài đặt một lần trên macOS (Apple chip hoặc Intel). Chạy:  ./setup.sh
set -e
cd "$(dirname "$0")"
if ! command -v brew >/dev/null; then
  echo "Chưa có Homebrew. Cài theo hướng dẫn ở https://brew.sh rồi chạy lại ./setup.sh"; exit 1
fi
for p in ffmpeg node python; do
  if ! brew list --versions $p >/dev/null 2>&1; then echo "• brew install $p"; brew install $p; fi
done
echo "• Cài thư viện Node (playwright) + Chromium"
npm install --no-audit --no-fund
npx playwright install chromium
echo "• Tạo môi trường Python riêng (.venv) + numpy, scipy"
python3 -m venv .venv
.venv/bin/pip install -q --upgrade pip
.venv/bin/pip install -q -r requirements.txt
chmod +x vid
./vid check
