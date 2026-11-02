"""Bước 1 — chuẩn bị: giọng đọc → build/voice.wav; video thô → build/base.mp4 (1080x1920, 30 fps, SDR, không tiếng).
Độ dài video ra = độ dài giọng + tail (mặc định 1.2 s). Video thô ngắn hơn thì giữ khung cuối.
Video HDR của iPhone (HLG / PQ) được chuyển về màu thường để không bị bệt màu khi đăng."""
import sys, os, json, subprocess
import numpy as np
from common import Project, run, probe, die, W, H, FPS


def has_filter(name):
    out = subprocess.run(['ffmpeg', '-hide_banner', '-filters'], capture_output=True, text=True).stdout
    return f' {name} ' in out


def make_hdr_cube(path, transfer, size=65):
    """3D LUT: R'G'B' HDR (BT.2020, HLG hoặc PQ) → R'G'B' SDR (BT.709), tone map Hable, trắng chuẩn 203 nit.
    Dùng khi ffmpeg không có zscale (bản Homebrew trên macOS). Kết quả gần giống đường zscale + tonemap=hable."""
    v = np.linspace(0, 1, size)
    b, g, r = np.meshgrid(v, v, v, indexing='ij')           # .cube: R chạy nhanh nhất
    rgb = np.stack([r, g, b], -1).reshape(-1, 3)
    if transfer == 'arib-std-b67':                           # HLG: OETF⁻¹ → ánh sáng cảnh → OOTF (1000 nit, gamma 1.2)
        a, bb = 0.17883277, 0.28466892; c = 0.5 - a * np.log(4 * a)
        E = np.where(rgb <= 0.5, rgb ** 2 / 3, (np.exp((rgb - c) / a) + bb) / 12)
        Ys = E @ np.array([0.2627, 0.6780, 0.0593])
        nits = 1000 * np.power(np.maximum(Ys, 1e-9), 0.2)[:, None] * E
    else:                                                    # PQ (ST 2084): EOTF → nit tuyệt đối
        m1, m2, c1, c2, c3 = 0.1593017578125, 78.84375, 0.8359375, 18.8515625, 18.6875
        p = np.power(rgb, 1 / m2)
        nits = 10000 * np.power(np.maximum(p - c1, 0) / (c2 - c3 * p), 1 / m1)
    L = nits / 203.0
    M = np.array([[1.6605, -0.5876, -0.0728], [-0.1246, 1.1329, -0.0083], [-0.0182, -0.1006, 1.1187]])
    L = np.maximum(L @ M.T, 0)                               # BT.2020 → BT.709
    def hable(x):
        A, B, C, D, E_, F = 0.15, 0.50, 0.10, 0.20, 0.02, 0.30
        return (x * (A * x + C * B) + D * E_) / (x * (A * x + B) + D * F) - E_ / F
    peak = 1000 / 203.0
    sig = np.maximum(L.max(1), 1e-6)
    L = L * (hable(sig) / hable(peak) / sig)[:, None]
    L = np.clip(L, 0, 1)
    V = np.where(L < 0.018, 4.5 * L, 1.099 * np.power(L, 0.45) - 0.099)   # OETF BT.709
    with open(path, 'w') as f:
        f.write(f'TITLE "hdr2sdr"\nLUT_3D_SIZE {size}\n')
        np.savetxt(f, np.clip(V, 0, 1), fmt='%.6f')


def main(path):
    pr = Project(path)
    vin, ain = pr.video_in(), pr.voice_in()
    pr.script_in()  # kiểm tra có kịch bản

    ic = pr.cfg['intro']; lead = float(ic['lead']) if ic.get('enabled') else 0.0
    af = ['-af', f'adelay={int(lead * 1000)}:all=1'] if lead > 0 else []   # chừa chỗ cho cú mở đầu trước lời dẫn
    run(['ffmpeg', '-v', 'error', '-y', '-i', ain, *af, '-ac', '2', '-ar', '48000', '-c:a', 'pcm_s16le', pr.b('voice.wav')])
    vdur = float(probe(pr.b('voice.wav'))['format']['duration'])

    info = probe(vin)
    vs = [s for s in info['streams'] if s['codec_type'] == 'video'][0]
    src_dur = float(info['format']['duration'])
    dur = round(vdur + float(pr.cfg['tail']), 2)
    trc = vs.get('color_transfer', '')
    hdr = trc in ('arib-std-b67', 'smpte2084')
    w, h = int(vs['width']), int(vs['height'])
    rot = 0
    for sd in vs.get('side_data_list', []):
        if 'rotation' in sd:
            rot = abs(int(sd['rotation']))
    if rot in (90, 270):
        w, h = h, w
    if w > h:
        print('! Video thô đang là khung ngang — sẽ cắt giữa thành khung dọc 9:16. Nên quay dọc.')

    vf = [f'scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos', f'crop={W}:{H}']
    method = ''
    if hdr:
        tin = 'arib-std-b67' if trc == 'arib-std-b67' else 'smpte2084'
        if has_filter('zscale') and not os.environ.get('VID_FORCE_LUT'):
            vf += [f'zscale=tin={tin}:min=bt2020nc:pin=bt2020:t=linear:npl=203', 'format=gbrpf32le', 'zscale=p=bt709',
                   'tonemap=hable:desat=0', 'zscale=t=bt709:m=bt709:r=tv']
            method = 'zscale'
        else:   # ffmpeg Homebrew không có zscale → dùng 3D LUT tự tính (chạy ở mọi bản ffmpeg)
            make_hdr_cube(pr.b('hdr2sdr.cube'), tin)
            vf += ['scale=in_color_matrix=bt2020:in_range=tv', 'format=rgb48le', 'lut3d=file=hdr2sdr.cube:interp=tetrahedral',
                   'scale=out_color_matrix=bt709:out_range=tv']
            method = '3D LUT'
    vf += ['format=yuv420p', 'setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709:range=tv', f'fps={FPS}']
    if src_dur < dur:
        vf.append(f'tpad=stop_mode=clone:stop_duration={dur - src_dur + 0.5:.2f}')
        print(f'! Video thô ({src_dur:.1f}s) ngắn hơn lời đọc + đuôi ({dur:.1f}s): giữ khung cuối thêm {dur - src_dur:.1f}s.')
    print(f'• Chuẩn bị video nền {dur:.2f}s ({f"HDR → SDR bằng {method}, " if hdr else ""}{w}x{h} → {W}x{H})…')
    r = subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', os.path.abspath(vin), '-t', f'{dur}', '-an', '-vf', ','.join(vf),
                        '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '14',
                        '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709', 'base.mp4'], cwd=pr.build)
    if r.returncode != 0:
        die('ffmpeg lỗi khi chuẩn bị video' + (' (bước chuyển HDR → SDR).' if hdr else '.'))
    boom = round(max(0.0, lead - 0.06), 3) if lead > 0 else 0.0   # tiếng nổ ngay trước chữ đầu tiên
    json.dump({'duration': dur, 'voice': vdur, 'source': src_dur, 'hdr': hdr, 'lead': lead, 'boom': boom}, open(pr.b('info.json'), 'w'), indent=1)
    print(f'✓ build/base.mp4 ({dur:.2f}s), build/voice.wav ({vdur:.2f}s)')


if __name__ == '__main__':
    main(sys.argv[1])
