// Bước 3 — dựng lớp đồ hoạ (engine/overlay.html) bằng Chromium không giao diện và ghép lên build/base.mp4.
//   node engine/render.js <dự án> events                 → build/events.json (mốc thời gian + danh sách hiệu ứng âm thanh)
//   node engine/render.js <dự án> stills 2.5,12,40 [--safe] → out/stills/still_<giây>.png (ghép lên video thật)
//   node engine/render.js <dự án> full                    → build/video.mp4 (hình, chưa có tiếng)
// --safe vẽ vùng an toàn để kiểm tra. Phụ đề bật/tắt bằng "subtitles" trong project.json.
const { chromium } = require('playwright');
const { spawn, execFileSync } = require('child_process');
const fs = require('fs'), path = require('path');

const ROOT = path.resolve(__dirname, '..');
const [projArg, mode, arg] = process.argv.slice(2);
if (!projArg || !mode) { console.error('Dùng: node engine/render.js <thư mục dự án> events|stills <giây,giây>|full [--safe]'); process.exit(1); }
const P = path.resolve(projArg), B = path.join(P, 'build'), OUT = path.join(P, 'out');
const safe = process.argv.includes('--safe');
const FPS = 30;
const readJSON = (f) => JSON.parse(fs.readFileSync(f, 'utf8'));

function merge(a, b) { const o = { ...a }; for (const [k, v] of Object.entries(b || {})) o[k] = v && typeof v === 'object' && !Array.isArray(v) && typeof a[k] === 'object' ? merge(a[k], v) : v; return o; }

(async () => {
  for (const f of ['info.json', 'words.json']) if (!fs.existsSync(path.join(B, f))) { console.error(`✗ Thiếu build/${f} — chạy bước prep và align trước.`); process.exit(1); }
  const scenesFile = path.join(P, 'scenes.json');
  if (!fs.existsSync(scenesFile)) { console.error('✗ Thiếu scenes.json trong dự án.'); process.exit(1); }
  const info = readJSON(path.join(B, 'info.json'));
  const brand = readJSON(path.join(ROOT, 'assets', 'brand', 'brand.json'));
  const proj = merge({ subtitles: false, subtitleKeywords: [], watermark: { opacity: 0.1, scale: 1 } }, fs.existsSync(path.join(P, 'project.json')) ? readJSON(path.join(P, 'project.json')) : {});
  const CFG = { brand, subtitles: !!proj.subtitles, subtitleKeywords: proj.subtitleKeywords || [], watermark: proj.watermark, duration: info.duration,
    logo: 'file://' + path.join(ROOT, 'assets', 'brand', brand.logo || 'logo.svg') };
  let scenes = readJSON(scenesFile); if (!Array.isArray(scenes)) scenes = scenes.scenes;

  const browser = await chromium.launch({ args: ['--allow-file-access-from-files'] });
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  const errs = []; page.on('pageerror', (e) => errs.push(e.message));
  await page.goto('file://' + path.join(ROOT, 'engine', 'overlay.html') + (safe ? '?safe=1' : ''));
  await page.addScriptTag({ path: path.join(B, 'words.js') });
  await page.addScriptTag({ content: `window.SCENES = ${JSON.stringify(scenes)}; window.CFG = ${JSON.stringify(CFG)};` });
  await page.evaluate(() => window.init());
  await page.waitForFunction(() => window.ready || window.err, null, { timeout: 30000 });
  const err = await page.evaluate(() => window.err);
  if (err || errs.length) { console.error('✗ ' + (err || errs.join('\n'))); await browser.close(); process.exit(1); }

  const ev = await page.evaluate(() => ({ sfx: window.SFX, items: window.TIMES }));
  fs.writeFileSync(path.join(B, 'events.json'), JSON.stringify({ duration: info.duration, ...ev }, null, 1));
  if (mode === 'events') {
    ev.items.forEach((it) => console.log(`  ${it.from.toFixed(2).padStart(6)}–${it.to.toFixed(2).padStart(6)}  ${it.type}`));
    console.log(`✓ build/events.json (${ev.items.length} thành phần, ${ev.sfx.length} hiệu ứng âm thanh)`);
    await browser.close(); return;
  }
  const shot = async (t) => { await page.evaluate((t) => window.seek(t), t); return page.screenshot({ omitBackground: true, type: 'png' }); };

  if (mode === 'stills') {
    const dir = path.join(OUT, 'stills'); fs.mkdirSync(dir, { recursive: true });
    const ts = (arg || '').split(',').filter(Boolean).map(Number);
    const outs = [];
    for (const t of ts) {
      const ov = path.join(B, `ov_${t}.png`); fs.writeFileSync(ov, await shot(t));
      const out = path.join(dir, `still_${t.toFixed(2)}${safe ? '_safe' : ''}.png`);
      execFileSync('ffmpeg', ['-v', 'error', '-y', '-ss', String(t), '-i', path.join(B, 'base.mp4'), '-i', ov, '-frames:v', '1', '-filter_complex', '[0][1]overlay', out]);
      outs.push(out); console.log(out);
    }
    if (outs.length > 1) {   // ghép ngang để xem nhanh
      const sheet = path.join(dir, `stills${safe ? '_safe' : ''}.png`);
      execFileSync('ffmpeg', ['-v', 'error', '-y', ...outs.flatMap((o) => ['-i', o]), '-filter_complex', `${outs.map((_, i) => `[${i}]`).join('')}hstack=${outs.length},scale=${Math.min(2160, 540 * outs.length)}:-2`, sheet]);
      console.log('✓ ' + sheet);
    }
  } else if (mode === 'full') {
    const N = Math.round(info.duration * FPS), out = path.join(B, 'video.mp4');
    const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-i', path.join(B, 'base.mp4'), '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'png', '-i', '-',
      '-filter_complex', '[0:v][1:v]overlay=eof_action=pass,format=yuv420p[v]', '-map', '[v]', '-t', String(info.duration),
      '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '17', '-profile:v', 'high', '-r', String(FPS), '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });
    const t0 = Date.now();
    for (let i = 0; i < N; i++) {
      const buf = await shot(i / FPS);
      if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once('drain', r));
      if (i % 150 === 0) console.log(`  khung ${i}/${N}  (${((Date.now() - t0) / 1000).toFixed(0)}s)`);
    }
    ff.stdin.end(); const code = await new Promise((r) => ff.on('close', r));
    if (code !== 0) { console.error('✗ ffmpeg lỗi khi ghép hình'); process.exit(1); }
    console.log(`✓ build/video.mp4 (${((Date.now() - t0) / 1000).toFixed(0)}s)`);
  }
  await browser.close();
})().catch((e) => { console.error('✗', e.message || e); process.exit(1); });
