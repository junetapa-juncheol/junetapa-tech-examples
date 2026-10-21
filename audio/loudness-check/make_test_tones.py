"""Make three short test WAVs with ffmpeg: a normal tone, a clipped tone, and one with a silent intro."""
import subprocess
import sys
from pathlib import Path

TONES = {
    "01_normal.wav": "0.25*sin(2*PI*440*t)",
    "02_clipped.wav": "1.6*sin(2*PI*440*t)",
    "03_late_start.wav": "if(lt(t,3),0,0.25*sin(2*PI*440*t))",
}


def main():
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "test_tones")
    out.mkdir(parents=True, exist_ok=True)
    for name, expr in TONES.items():
        src = f"aevalsrc='{expr}|{expr}':s=44100:d=10"
        subprocess.run(
            ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
             "-f", "lavfi", "-i", src, "-c:a", "pcm_s16le", str(out / name)],
            check=True,
        )
        print(out / name)


if __name__ == "__main__":
    main()
