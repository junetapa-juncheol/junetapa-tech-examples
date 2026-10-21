# 음원 폴더 라우드니스 검사

폴더 안 곡마다 통합 LUFS · True Peak · 클리핑 · 앞 무음 · 길이를 재서 표로 보여 주는 예제입니다.
Measure integrated LUFS, true peak, clipping and leading silence for every track in a folder.

- 확인한 날: 2026-10-21 (Spotify for Artists «Loudness normalization» 기준 · 바뀌면 함께 고침)
- 필요한 것: Python 3.8+ · ffmpeg (ffprobe 포함, PATH에 있어야 함)

## 실행

```bash
python make_test_tones.py tones                 # 시험용 10초 WAV 3개 만들기
python loudness_check.py tones                  # 표를 화면에 출력
python loudness_check.py tones --out report     # report/report.md, report/report.json 저장
```

출력 예 (위 시험 파일):

```
| file | length | LUFS | LRA | true peak | clipped | intro silence | notes |
|---|---|---|---|---|---|---|---|
| 01_normal.wav | 0:10 | -12.7 | 0.0 | -12.0 | 0 | 0.0s | ok |
| 02_clipped.wav | 0:10 | 1.0 | 0.0 | 0.1 | 251600 | 0.0s | true peak +0.1 dBTP > -2; ... |
| 03_late_start.wav | 0:10 | -12.8 | 6.3 | -12.0 | 0 | 3.0s | 3.0s silence at start |
```

## 파일

| 파일 | 하는 일 |
|---|---|
| `loudness_check.py` | ffmpeg 한 번 돌려 ebur128(LUFS · LRA · True Peak) · astats(0 dBFS 샘플 수) · silencedetect(앞 무음)를 읽고 표로 정리 |
| `make_test_tones.py` | 보통 사인파 · 일부러 찌그러뜨린 사인파 · 앞 3초가 빈 사인파 WAV를 만듦 |

## 기준

| 항목 | 값 | 출처 |
|---|---|---|
| 목표 라우드니스 | -14 LUFS (integrated) | Spotify for Artists |
| True Peak | -1 dBTP 아래 · -14 LUFS보다 크게 마스터했으면 -2 dBTP 아래 | Spotify for Artists |
| 앞 무음 | 2초 넘으면 표시 | 이 예제의 임의 값 |

Spotify Premium 정규화 단계는 Loud -11 · Normal -14 · Quiet -19 LUFS입니다. -14보다 크게 만든 곡은 재생할 때 소리가 줄어듭니다.

## 주의

- 음원 파일은 읽기만 하고 고치지 않습니다.
- 클리핑 칸은 0 dBFS에 닿은 샘플 수(astats Peak count)입니다. 손실 압축 파일은 디코딩 과정에서 값이 조금 달라질 수 있습니다.
- 가사 · 발음 · 편곡처럼 숫자로 못 재는 부분은 직접 들어 봐야 합니다.
