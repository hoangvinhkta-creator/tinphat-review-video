"""Bước 2 — căn thời gian từng từ của kịch bản theo giọng đọc (không cần nhận dạng giọng nói).
1) Tìm các đoạn có tiếng nói trong build/voice.wav (năng lượng), các khoảng lặng giữa chúng.
2) Chia kịch bản thành cụm theo dấu câu; đếm âm tiết từng từ (tiếng Việt 1 từ = 1 âm tiết, số và từ ngoại được ước lượng).
3) Ghép dấu câu với khoảng lặng bằng quy hoạch động (cho phép dấu câu không ngắt và chỗ lấy hơi giữa cụm).
4) Giữa hai mốc ghép, rải âm tiết theo thời lượng có tiếng; trong mỗi đoạn, cắt âm tiết tại chỗ năng lượng thấp nhất.
Ra: build/words.json + build/words.js (window.WD) và in bảng cụm để kiểm tra."""
import sys, re, json, wave, unicodedata
import numpy as np
from common import Project, die

PUNCT_END = re.compile(r'[,.;:!?…]+["”’)\]]*$')
DASHES = {'-', '–', '—', '|'}
VN = set('àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ')


def vn_num(n):
    """Số âm tiết khi đọc số nguyên bằng tiếng Việt (ước lượng)."""
    if n < 10: return 1
    if n < 20: return 1 if n == 10 else 2
    if n < 100: return 2 + (1 if n % 10 else 0)
    if n < 1000:
        r = n % 100
        return 2 + (0 if r == 0 else 2 if r < 10 else vn_num(r))
    if n < 1_000_000:
        r = n % 1000
        return vn_num(n // 1000) + 1 + (0 if r == 0 else (2 + vn_num(r) if r < 100 else vn_num(r)))
    return vn_num(n // 1_000_000) + 1 + (vn_num(n % 1_000_000) if n % 1_000_000 else 0)


UNITS = {'kg': 3, 'g': 1, 'l': 1, 'lít': 1, 'w': 1, 'kw': 2, 'kwh': 3, 'cm': 3, 'mm': 3, 'm': 1, 'inch': 1, 'hp': 2, 'btu': 3, '%': 2, 'đ': 1, 'k': 1, 'tr': 1}


def syllables(tok):
    t = unicodedata.normalize('NFC', tok).strip('"“”‘’\'()[]{}«»…,.;:!?')
    if not t: return 0
    m = re.fullmatch(r'(\d+(?:[.,]\d+)*)(%|[a-zA-Zđ]+)?', t)
    if m:
        num, unit = m.group(1), (m.group(2) or '').lower()
        parts = re.split(r'[.,]', num)
        if len(parts) == 2 and len(parts[1]) != 3:  # số thập phân 5,5 / 5.5
            n = vn_num(int(parts[0])) + 1 + vn_num(int(parts[1]))
        else:
            n = vn_num(int(''.join(parts)))
        return n + UNITS.get(unit, len(unit) if unit else 0)
    low = t.lower()
    if any(ch in VN for ch in low): return max(1, len(re.findall(r'[-–]', t)) + 1)
    letters = re.sub(r'[^A-Za-z]', '', t)
    if t.isupper() and 2 <= len(letters) <= 3:
        return len(letters)                              # chữ viết tắt đọc từng chữ: LG, TV, UV, AI
    return max(1, len(re.findall(r'[aeiouy]+', low)))


def tokenize(text):
    text = unicodedata.normalize('NFC', text)
    raw = text.split()
    toks = []
    for r in raw:
        if r in DASHES:
            if toks: toks[-1]['brk'] = True
            continue
        toks.append({'w': r, 'syl': syllables(r), 'brk': bool(PUNCT_END.search(r))})
    if toks: toks[-1]['brk'] = True
    for t in toks:
        if t['syl'] == 0: t['syl'] = 1
    return toks


def speech_intervals(x, sr):
    hop = int(sr * .01); n = len(x) // hop
    env = np.sqrt(np.mean(x[: n * hop].reshape(n, hop) ** 2, axis=1) + 1e-12)
    env = np.convolve(env, np.ones(5) / 5, mode='same')
    db = 20 * np.log10(env + 1e-9); sp = db > db.max() - 38
    iv, i = [], 0
    while i < n:
        if sp[i]:
            j = i
            while j < n and sp[j]: j += 1
            iv.append([i, j]); i = j
        else:
            i += 1
    m = []
    for a, b in iv:
        if m and a - m[-1][1] < 18: m[-1][1] = b
        else: m.append([a, b])
    return [s for s in m if s[1] - s[0] >= 12], env


def main(path):
    pr = Project(path)
    text = open(pr.script_in(), encoding='utf-8').read()
    toks = tokenize(text)
    if not toks: die('script.txt trống')
    w = wave.open(pr.b('voice.wav')); sr = w.getframerate(); ch = w.getnchannels()
    x = np.frombuffer(w.readframes(w.getnframes()), dtype='<i2').astype(np.float32).reshape(-1, ch).mean(1) / 32768
    iv, env = speech_intervals(x, sr)
    if not iv: die('Không tìm thấy tiếng nói trong voice')

    N = sum(t['syl'] for t in toks)
    durs = np.array([b - a for a, b in iv], float)
    Vcum = np.concatenate([[0], np.cumsum(durs)])
    rate = N / Vcum[-1]
    # mốc dấu câu (số âm tiết tích luỹ tới cuối cụm), bỏ cụm cuối
    cb, acc = [], 0
    for i, t in enumerate(toks):
        acc += t['syl']
        if t['brk'] and i < len(toks) - 1: cb.append((acc, i))
    G = len(iv) - 1
    E = [Vcum[j + 1] * rate for j in range(G)]   # âm tiết dự kiến tại khoảng lặng j
    gap = [(iv[j + 1][0] - iv[j][1]) / 100 for j in range(G)]
    nb = len(cb); INF = 1e18
    dp = np.full((nb + 1, G + 1), INF); bk = np.zeros((nb + 1, G + 1), int)
    dp[0][0] = 0
    for i in range(nb + 1):
        for j in range(G + 1):
            if i == 0 and j == 0: continue
            best, how = INF, 0
            if i > 0 and j > 0:
                c = dp[i - 1][j - 1] + 0.6 * abs(cb[i - 1][0] - E[j - 1])
                if c < best: best, how = c, 1
            if i > 0:
                c = dp[i - 1][j] + 3.0                       # dấu câu không có khoảng lặng
                if c < best: best, how = c, 2
            if j > 0:
                c = dp[i][j - 1] + 2.0 + 10 * gap[j - 1]     # lấy hơi giữa cụm (lặng càng dài càng khó)
                if c < best: best, how = c, 3
            dp[i][j], bk[i][j] = best, how
    anchors = []; i, j = nb, G
    while i > 0 or j > 0:
        h = bk[i][j]
        if h == 1: anchors.append((cb[i - 1][0], j - 1)); i, j = i - 1, j - 1
        elif h == 2: i -= 1
        else: j -= 1
    anchors = [(0, -1)] + anchors[::-1] + [(N, G)]
    # rải âm tiết vào các đoạn có tiếng
    syl_iv = [0] * len(iv)
    for (s0, g0), (s1, g1) in zip(anchors, anchors[1:]):
        ks = list(range(g0 + 1, g1 + 1)); n = s1 - s0
        if not ks: continue
        d = np.array([durs[k] for k in ks]); cum = np.round(np.cumsum(d) / d.sum() * n).astype(int); prev = 0
        for k, c in zip(ks, cum): syl_iv[k] = c - prev; prev = c
    # cắt âm tiết trong từng đoạn
    sy = []
    for (a, b), n in zip(iv, syl_iv):
        if n <= 0: continue
        step = (b - a) / n; cuts = [a]
        for k in range(1, n):
            est = a + step * k; lo = max(int(est - step * .35), cuts[-1] + 5); hi = max(int(est + step * .35), lo + 1)
            seg = env[lo:hi]; cuts.append(lo + int(np.argmin(seg)) if len(seg) else int(est))
        cuts.append(b)
        sy += [(cuts[k] / 100, cuts[k + 1] / 100) for k in range(n)]
    words, k = [], 0
    for t in toks:
        a = sy[min(k, len(sy) - 1)][0]; e = sy[min(k + t['syl'] - 1, len(sy) - 1)][1]
        words.append({'w': t['w'], 's': round(a, 3), 'e': round(e, 3)}); k += t['syl']
    segs, w0 = [], 0
    for i, t in enumerate(toks):
        if t['brk']:
            segs.append({'text': ' '.join(x['w'] for x in toks[w0:i + 1]), 's': words[w0]['s'], 'e': words[i]['e'], 'w0': w0, 'w1': i + 1}); w0 = i + 1
    data = {'words': words, 'segs': segs}
    json.dump(data, open(pr.b('words.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    open(pr.b('words.js'), 'w', encoding='utf-8').write('window.WD = ' + json.dumps(data, ensure_ascii=False) + ';')
    matched = len(anchors) - 2
    print(f'• {len(toks)} từ, {N} âm tiết, {len(iv)} đoạn có tiếng, {nb + 1} cụm theo dấu câu; ghép được {matched}/{nb} dấu câu với khoảng lặng.')
    for s in segs: print(f'  {s["s"]:6.2f}–{s["e"]:6.2f}  {s["text"]}')
    if matched < nb * 0.6:
        print('! Ít dấu câu khớp khoảng lặng: kiểm tra script.txt có đúng y lời đọc không (thừa/thiếu câu?).')
    print('✓ build/words.json')


if __name__ == '__main__':
    main(sys.argv[1])
