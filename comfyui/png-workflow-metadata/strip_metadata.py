"""Copy a PNG without its text chunks (prompt, workflow, parameters ...).

Use it on images you want to share without the prompt text, seed and
model file names. The image data is copied byte for byte, so the picture
does not change. Keep the original if you may want the workflow later.

Usage:
    python strip_metadata.py in.png out.png
"""
import struct
import sys

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
TEXT_CHUNKS = {b"tEXt", b"zTXt", b"iTXt"}


def strip(src, dst):
    data = open(src, "rb").read()
    if not data.startswith(PNG_SIGNATURE):
        raise ValueError(f"not a PNG file: {src}")

    out = [PNG_SIGNATURE]
    removed = []
    pos = len(PNG_SIGNATURE)
    while pos + 8 <= len(data):
        length, ctype = struct.unpack(">I4s", data[pos:pos + 8])
        end = pos + 12 + length
        if ctype in TEXT_CHUNKS:
            key = data[pos + 8:end - 4].split(b"\x00", 1)[0].decode("latin-1")
            removed.append(key)
        else:
            out.append(data[pos:end])
        pos = end
        if ctype == b"IEND":
            break

    with open(dst, "wb") as f:
        f.write(b"".join(out))
    print(f"wrote {dst} (removed: {', '.join(removed) or 'nothing'})")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    strip(sys.argv[1], sys.argv[2])
