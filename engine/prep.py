"""Bước 1 — chuẩn bị: giọng đọc → build/voice.wav; video thô → build/base.mp4 (1080x1920, 30 fps, SDR, không tiếng).
Độ dài video ra = độ dài giọng + tail (mặc định 1.2 s). Video thô ngắn hơn thì giữ khung cuối.
Video HDR của iPhone (HLG / PQ) được chuyển về màu thường để không bị bệt màu khi đăng."""
import sys, json, subprocess
from common import Project, run, probe, die, W, H, FPS


def main(path):
    pr = Project(path)
    vin, ain = pr.video_in(), pr.voice_in()
    pr.script_in()  # kiểm tra có kịch bản

    run(['ffmpeg', '-v', 'error', '-y', '-i', ain, '-ac', '2', '-ar', '48000', '-c:a', 'pcm_s16le', pr.b('voice.wav')])
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
    if hdr:
        tin = 'arib-std-b67' if trc == 'arib-std-b67' else 'smpte2084'
        vf += [f'zscale=tin={tin}:min=bt2020nc:pin=bt2020:t=linear:npl=203', 'format=gbrpf32le', 'zscale=p=bt709',
               'tonemap=hable:desat=0', 'zscale=t=bt709:m=bt709:r=tv']
    vf += ['format=yuv420p', f'fps={FPS}']
    if src_dur < dur:
        vf.append(f'tpad=stop_mode=clone:stop_duration={dur - src_dur + 0.5:.2f}')
        print(f'! Video thô ({src_dur:.1f}s) ngắn hơn lời đọc + đuôi ({dur:.1f}s): giữ khung cuối thêm {dur - src_dur:.1f}s.')
    print(f'• Chuẩn bị video nền {dur:.2f}s ({"HDR → SDR, " if hdr else ""}{w}x{h} → {W}x{H})…')
    r = subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', vin, '-t', f'{dur}', '-an', '-vf', ','.join(vf),
                        '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '14', pr.b('base.mp4')])
    if r.returncode != 0:
        if hdr:
            die('ffmpeg không chuyển được HDR (thiếu bộ lọc zscale). Cài: brew reinstall ffmpeg — hoặc quay lại với HDR tắt.')
        die('ffmpeg lỗi khi chuẩn bị video.')
    json.dump({'duration': dur, 'voice': vdur, 'source': src_dur, 'hdr': hdr}, open(pr.b('info.json'), 'w'), indent=1)
    print(f'✓ build/base.mp4 ({dur:.2f}s), build/voice.wav ({vdur:.2f}s)')


if __name__ == '__main__':
    main(sys.argv[1])
