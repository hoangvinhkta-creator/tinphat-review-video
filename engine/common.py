"""Tiện ích dùng chung: đường dẫn dự án, cấu hình, ffprobe."""
import json, os, subprocess, sys, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENGINE = os.path.join(ROOT, 'engine')
FPS = 30
W, H = 1080, 1920

DEFAULTS = {
    "subtitles": False,
    "subtitleKeywords": [],
    "tail": 1.2,                       # giây giữ màn kết sau khi hết lời
    "watermark": {"opacity": 0.10, "scale": 1.0},
    "music": {"enabled": True, "bpm": 120, "key": 0, "seed": 7, "level_db": -6},
    "sfx": {"enabled": True, "level_db": -12},
    "min_voice_margin_db": 9,          # giọng phải cao hơn nền ít nhất chừng này dB khi đang nói
}


class Project:
    def __init__(self, path):
        self.dir = os.path.abspath(path)
        if not os.path.isdir(self.dir):
            die(f'Không có thư mục dự án: {self.dir}')
        self.name = os.path.basename(self.dir.rstrip('/'))
        self.input = os.path.join(self.dir, 'input')
        self.build = os.path.join(self.dir, 'build')
        self.out = os.path.join(self.dir, 'out')
        os.makedirs(self.build, exist_ok=True)
        os.makedirs(self.out, exist_ok=True)
        cfg = {}
        pj = os.path.join(self.dir, 'project.json')
        if os.path.exists(pj):
            cfg = json.load(open(pj, encoding='utf-8'))
        self.cfg = deep_merge(DEFAULTS, cfg)
        self.brand = json.load(open(os.path.join(ROOT, 'assets', 'brand', 'brand.json'), encoding='utf-8'))

    def p(self, *a):
        return os.path.join(self.dir, *a)

    def b(self, *a):
        return os.path.join(self.build, *a)

    def find_input(self, stem, exts):
        for e in exts:
            for f in glob.glob(os.path.join(self.input, f'{stem}.{e}')) + glob.glob(os.path.join(self.input, f'{stem}.{e.upper()}')):
                return f
        die(f'Thiếu file input/{stem}.* ({", ".join(exts)}) trong {self.dir}')

    def video_in(self):
        return self.find_input('video', ['mov', 'mp4', 'm4v', 'mkv'])

    def voice_in(self):
        return self.find_input('voice', ['mp3', 'wav', 'm4a', 'aac', 'flac'])

    def script_in(self):
        return self.find_input('script', ['txt'])

    def duration(self):
        return float(json.load(open(self.b('info.json')))['duration'])


def deep_merge(a, b):
    out = dict(a)
    for k, v in b.items():
        out[k] = deep_merge(a[k], v) if isinstance(v, dict) and isinstance(a.get(k), dict) else v
    return out


def die(msg):
    print('✗ ' + msg, file=sys.stderr)
    sys.exit(1)


def run(args, **kw):
    r = subprocess.run(args, **kw)
    if r.returncode != 0:
        die('Lệnh lỗi: ' + ' '.join(str(a) for a in args[:6]) + ' …')
    return r


def probe(path):
    r = subprocess.run(['ffprobe', '-v', 'error', '-print_format', 'json', '-show_streams', '-show_format', path],
                       capture_output=True, text=True)
    if r.returncode != 0:
        die(f'ffprobe không đọc được {path}')
    return json.loads(r.stdout)


def loudness(path):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-i', path, '-af', 'ebur128=peak=true', '-f', 'null', '-'],
                       capture_output=True, text=True).stderr
    I = [l for l in r.splitlines() if l.strip().startswith('I:')]
    P = [l for l in r.splitlines() if l.strip().startswith('Peak:')]
    return float(I[-1].split()[1]), float(P[-1].split()[1]) if P else None
