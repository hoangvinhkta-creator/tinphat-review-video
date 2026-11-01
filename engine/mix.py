"""Bước 5 — trộn tiếng: giọng đọc + nhạc nền + hiệu ứng, giữ lời dẫn luôn rõ.
- Giọng: lọc trầm, nén nhẹ.
- Nhạc: cắt bớt dải giọng (250 Hz / 1 kHz / 2.5 kHz), tự nhỏ xuống khi có lời (sidechain, ratio 10).
- Hiệu ứng: lọc trầm, nhỏ nhẹ khi có lời (sidechain, ratio 3).
- Chuẩn hoá -14 LUFS, đỉnh ≤ -1.5 dBTP (chuẩn TikTok / Reels / YouTube).
- Đo: trong từng cửa sổ 0,4 s đang nói, giọng phải cao hơn nền ≥ min_voice_margin_db (mặc định 9 dB).
  Nếu không đạt, tự giảm nhạc/hiệu ứng 2 dB và trộn lại (tối đa 4 lần).
Mức trong project.json: "music": {"level_db": -6}, "sfx": {"level_db": -12}."""
import sys, json, wave, subprocess
import numpy as np
from scipy.signal import butter, sosfilt
from common import Project, run, loudness


def rd(p):
    w = wave.open(p); x = np.frombuffer(w.readframes(w.getnframes()), dtype='<i2').astype(np.float64) / 32768
    return x.reshape(-1, w.getnchannels()).mean(1), w.getframerate()


def mix_once(pr, mus_db, sfx_db, dur):
    m_on = pr.cfg['music'].get('enabled', True); s_on = pr.cfg['sfx'].get('enabled', True)
    fc = (f"[0:a]highpass=f=70,acompressor=threshold=-22dB:ratio=3:attack=5:release=120:makeup=3dB,apad,atrim=0:{dur},asplit=3[v][k1][k2];"
          f"[1:a]equalizer=f=2500:t=o:w=1.5:g=-6,equalizer=f=1000:t=o:w=1:g=-3,equalizer=f=250:t=o:w=1:g=-2,volume={mus_db if m_on else -90}dB[m];"
          f"[m][k1]sidechaincompress=threshold=0.02:ratio=10:attack=20:release=450:knee=3[md];"
          f"[2:a]highpass=f=120,volume={sfx_db if s_on else -90}dB[s];[s][k2]sidechaincompress=threshold=0.02:ratio=3:attack=3:release=150[sd];"
          f"[md][sd]amix=inputs=2:normalize=0,apad,atrim=0:{dur}[bed]")
    run(['ffmpeg', '-v', 'error', '-y', '-i', pr.b('voice.wav'), '-i', pr.b('music.wav'), '-i', pr.b('sfx.wav'), '-filter_complex', fc,
         '-map', '[v]', '-c:a', 'pcm_s16le', pr.b('voice_proc.wav'), '-map', '[bed]', '-c:a', 'pcm_s16le', pr.b('bed.wav')])
    v, sr = rd(pr.b('voice_proc.wav')); b, _ = rd(pr.b('bed.wav')); n = min(len(v), len(b))
    k = butter(2, 150, 'highpass', fs=sr, output='sos'); vf, bf = sosfilt(k, v[:n]), sosfilt(k, b[:n])
    win = int(.4 * sr); res = []
    for s in json.load(open(pr.b('words.json')))['segs']:
        a, e = int(s['s'] * sr), int(s['e'] * sr)
        for i in range(a, max(a + 1, e - win), win // 2):
            rv = np.sqrt(np.mean(vf[i:i + win] ** 2)) + 1e-9; rb = np.sqrt(np.mean(bf[i:i + win] ** 2)) + 1e-9
            res.append((20 * np.log10(rv / rb), i / sr, 20 * np.log10(rv)))
    # chỉ tính cửa sổ đang nói rõ (bỏ đầu/cuối hơi thở): mức giọng ≥ trung vị − 6 dB
    med = float(np.median([r[2] for r in res]))
    return [(d, t) for d, t, lv in res if lv >= med - 6]


def main(path):
    pr = Project(path)
    dur = pr.duration()
    mus_db, sfx_db = float(pr.cfg['music']['level_db']), float(pr.cfg['sfx']['level_db'])
    need = float(pr.cfg['min_voice_margin_db'])
    for attempt in range(5):
        res = mix_once(pr, mus_db, sfx_db, dur)
        d = np.array([r[0] for r in res]); worst = sorted(res)[:3]
        print(f'• nhạc {mus_db:+.0f} dB, hiệu ứng {sfx_db:+.0f} dB → giọng hơn nền: trung bình {d.mean():.1f} dB, thấp nhất {d.min():.1f} dB '
              f'(ở {", ".join(f"{t:.1f}s" for _, t in worst)})')
        if d.min() >= need: break
        mus_db -= 2; sfx_db -= 2
    else:
        print(f'! Chưa đạt {need} dB ở vài chỗ — xem các giây trên, có thể do hiệu ứng trùng lúc đang nói.')
    run(['ffmpeg', '-v', 'error', '-y', '-i', pr.b('voice_proc.wav'), '-i', pr.b('bed.wav'), '-filter_complex',
         '[0][1]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11', '-ar', '48000', '-c:a', 'pcm_s16le', pr.b('mix_tmp.wav')])
    I, _ = loudness(pr.b('mix_tmp.wav'))
    run(['ffmpeg', '-v', 'error', '-y', '-i', pr.b('mix_tmp.wav'), '-af', f'volume={-14 - I:.2f}dB,alimiter=limit=0.84:level=false', '-c:a', 'pcm_s16le', pr.b('mix.wav')])
    I, P = loudness(pr.b('mix.wav'))
    json.dump({'music_db': mus_db, 'sfx_db': sfx_db, 'margin_mean': round(float(d.mean()), 1), 'margin_min': round(float(d.min()), 1), 'lufs': I, 'peak': P},
              open(pr.b('mix_report.json'), 'w'), indent=1)
    print(f'✓ build/mix.wav ({I:.1f} LUFS, đỉnh {P:.1f} dBFS)')


if __name__ == '__main__':
    main(sys.argv[1])
