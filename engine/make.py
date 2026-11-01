"""Điều phối toàn bộ quy trình.

  python3 engine/make.py check                       kiểm tra máy đã đủ công cụ chưa
  python3 engine/make.py new <tên>                   tạo projects/<tên>/ (input/, project.json mẫu)
  python3 engine/make.py <dự án> prep                video nền + giọng (build/base.mp4, build/voice.wav)
  python3 engine/make.py <dự án> align               căn thời gian từng từ (build/words.json)
  python3 engine/make.py <dự án> contact             bảng khung hình video (out/contact.png) để xem cảnh quay
     → viết scenes.json (Claude làm bước này)
  python3 engine/make.py <dự án> events              kiểm tra scenes.json, in mốc thời gian từng thành phần
  python3 engine/make.py <dự án> stills [giây,…] [--safe]   ảnh tĩnh để duyệt (out/stills/)
  python3 engine/make.py <dự án> render              dựng hình (build/video.mp4)
  python3 engine/make.py <dự án> audio               hiệu ứng + nhạc nền
  python3 engine/make.py <dự án> mix                 trộn tiếng, đo độ rõ lời dẫn
  python3 engine/make.py <dự án> final               ghép → out/<tên>.mp4 + out/scan.png
  python3 engine/make.py <dự án> all                 events → stills → render → audio → mix → final
"""
import sys, os, json, shutil, subprocess, importlib.util
from common import Project, ROOT, ENGINE, run, probe, die

NODE_ENV = dict(os.environ)


def node(*args):
    run(['node', os.path.join(ENGINE, 'render.js'), *args], env=NODE_ENV)


def check():
    ok = True
    def row(name, good, hint=''):
        nonlocal ok; ok &= good; print(f'  {"✓" if good else "✗"} {name}' + ('' if good else f'  → {hint}'))
    row('ffmpeg', shutil.which('ffmpeg') is not None, 'brew install ffmpeg')
    if shutil.which('ffmpeg'):
        f = subprocess.run(['ffmpeg', '-hide_banner', '-filters'], capture_output=True, text=True).stdout
        for flt in ('lut3d', 'sidechaincompress', 'loudnorm', 'acompressor'):
            row(f'  bộ lọc {flt}', f' {flt} ' in f, 'brew reinstall ffmpeg')
        if ' zscale ' not in f:
            print('  · không có zscale: video HDR sẽ chuyển màu bằng 3D LUT (kết quả tương đương, không cần cài thêm)')
    row('node ≥ 18', shutil.which('node') is not None and int(subprocess.run(['node', '-v'], capture_output=True, text=True).stdout[1:].split('.')[0]) >= 18, 'brew install node')
    r = subprocess.run(['node', '-e', "require('playwright').chromium.executablePath()"], capture_output=True, text=True, cwd=ROOT) if shutil.which('node') else None
    row('playwright (npm)', r is not None and r.returncode == 0, 'npm install   (trong thư mục bộ công cụ)')
    r2 = subprocess.run(['node', '-e', "const p=require('playwright').chromium.executablePath();process.exit(require('fs').existsSync(p)?0:1)"], capture_output=True, cwd=ROOT) if r and r.returncode == 0 else None
    row('Chromium cho playwright', r2 is not None and r2.returncode == 0, 'npx playwright install chromium')
    for mod in ('numpy', 'scipy'):
        row(f'python: {mod}', importlib.util.find_spec(mod) is not None, 'python3 -m pip install -r requirements.txt')
    row('logo + brand.json', os.path.exists(os.path.join(ROOT, 'assets', 'brand', 'brand.json')), 'thêm assets/brand/brand.json')
    print('✓ Máy đã sẵn sàng.' if ok else '✗ Còn thiếu công cụ (xem trên).')
    return ok


def new(name):
    d = os.path.join(ROOT, 'projects', name)
    if os.path.exists(d): die(f'Đã có {d}')
    os.makedirs(os.path.join(d, 'input'))
    shutil.copy(os.path.join(ROOT, 'engine', 'project.template.json'), os.path.join(d, 'project.json'))
    print(f'✓ Tạo {d}\n  Bỏ vào input/: video.mov (hoặc .mp4) · voice.mp3 (hoặc .wav) · script.txt (đúng lời đọc)\n  Điền thông tin sản phẩm vào project.json.')


def default_stills(pr):
    ev = json.load(open(pr.b('events.json')))
    items = ev['items']; ts = []
    for it in items:
        if it['to'] - it['from'] > .9: ts.append(round(min(it['to'] - .2, it['from'] + 1.1), 2))
    if len(ts) > 6:   # lấy 6 khoảnh khắc trải đều
        idx = [round(i * (len(ts) - 1) / 5) for i in range(6)]; ts = [ts[i] for i in idx]
    return ','.join(str(t) for t in ts)


def contact(pr):
    """Bảng khung hình video nền (mỗi giây 1 ô, có giờ + lưới vùng an toàn) + bảng cụm lời đọc, để chọn chỗ đặt đồ hoạ."""
    dur = pr.duration(); rows = int((dur + 7) // 8)
    grid = ("drawbox=x=0:y=0:w=1080:h=250:color=red@0.15:t=fill,drawbox=x=0:y=1440:w=1080:h=480:color=red@0.15:t=fill,"
            "drawbox=x=940:y=250:w=140:h=1190:color=red@0.15:t=fill,drawbox=x=60:y=250:w=880:h=1000:color=lime@0.9:t=4,")
    run(['ffmpeg', '-v', 'error', '-y', '-i', pr.b('base.mp4'), '-vf',
         f"fps=1,{grid}scale=240:-2,drawtext=text='%{{pts\\:hms}}':x=6:y=6:fontsize=22:fontcolor=yellow:box=1:boxcolor=black@0.6,tile=8x{rows}",
         '-frames:v', '1', os.path.join(pr.out, 'contact.png')])
    print(f'✓ out/contact.png ({rows} hàng × 8 ô, mỗi ô 1 giây; khung xanh = vùng đặt đồ hoạ, đỏ = vùng nền tảng che)')
    if os.path.exists(pr.b('words.json')):
        for s in json.load(open(pr.b('words.json')))['segs']: print(f'  {s["s"]:6.2f}–{s["e"]:6.2f}  {s["text"]}')


def final(pr):
    out = os.path.join(pr.out, f'{pr.name}.mp4')
    dur = pr.duration()
    run(['ffmpeg', '-v', 'error', '-y', '-i', pr.b('video.mp4'), '-i', pr.b('mix.wav'), '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
         '-c:a', 'aac', '-b:a', '256k', '-ar', '48000', '-t', str(dur), '-movflags', '+faststart', out])
    r = subprocess.run(['ffmpeg', '-v', 'error', '-i', out, '-f', 'null', '-'], capture_output=True, text=True)
    if r.stderr.strip(): die('File ra bị lỗi khi đọc lại:\n' + r.stderr[:500])
    run(['ffmpeg', '-v', 'error', '-y', '-i', out, '-vf', 'fps=2,scale=150:266,tile=13x8', '-frames:v', '1', os.path.join(pr.out, 'scan.png')])
    info = probe(out); v = [s for s in info['streams'] if s['codec_type'] == 'video'][0]
    rep = json.load(open(pr.b('mix_report.json')))
    print(f'✓ {out}\n  {v["width"]}x{v["height"]} · {v["r_frame_rate"]} fps · {float(info["format"]["duration"]):.2f}s · '
          f'{int(info["format"]["size"]) / 1e6:.1f} MB · {rep["lufs"]:.1f} LUFS · giọng hơn nền ≥ {rep["margin_min"]} dB\n  Xem nhanh cả video: out/scan.png (mỗi ô 0,5 s)')


def main():
    a = sys.argv[1:]
    if not a or a[0] in ('-h', '--help'): print(__doc__); return
    if a[0] == 'check': sys.exit(0 if check() else 1)
    if a[0] == 'new': return new(a[1])
    if a[0] == 'count':   # đếm âm tiết kịch bản, ước lượng thời lượng
        from align import tokenize
        f = a[1] if a[1].endswith('.txt') else os.path.join(a[1], 'input', 'script.txt')
        toks = tokenize(open(f, encoding='utf-8').read()); n = sum(t['syl'] for t in toks)
        print(f'{len(toks)} từ · {n} âm tiết · ước lượng {n / 4.3:.0f} giây khi đọc (≈4,3 âm tiết/giây)' + ('  ! dài quá, nên ≤ 190' if n > 200 else ''))
        return
    pr = Project(a[0]); step = a[1] if len(a) > 1 else 'all'; rest = a[2:]
    sys.argv = [sys.argv[0], pr.dir]
    if step == 'prep': import prep; prep.main(pr.dir)
    elif step == 'align': import align; align.main(pr.dir)
    elif step == 'contact': contact(pr)
    elif step == 'events': node(pr.dir, 'events')
    elif step == 'stills':
        times = next((x for x in rest if not x.startswith('--')), None)
        if not times: node(pr.dir, 'events'); times = default_stills(pr)
        node(pr.dir, 'stills', times, *[x for x in rest if x.startswith('--')])
    elif step == 'render': node(pr.dir, 'full')
    elif step == 'audio': node(pr.dir, 'events'); import audio; audio.main(pr.dir)
    elif step == 'mix': import mix; mix.main(pr.dir)
    elif step == 'final': final(pr)
    elif step == 'all':
        for f in ('build/base.mp4', 'build/words.json', 'scenes.json'):
            if not os.path.exists(pr.p(f)): die(f'Thiếu {f}. Thứ tự: prep → align → viết scenes.json → all.')
        node(pr.dir, 'events'); node(pr.dir, 'stills', default_stills(pr))
        node(pr.dir, 'full')
        import audio; audio.main(pr.dir)
        import mix; mix.main(pr.dir)
        final(pr)
    else: die(f'Không có bước "{step}". Xem: python3 engine/make.py --help')


if __name__ == '__main__':
    main()
