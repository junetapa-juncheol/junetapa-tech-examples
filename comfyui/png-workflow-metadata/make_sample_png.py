"""Make a small test PNG that carries ComfyUI-style metadata.

Handy when you want to try extract_workflow.py without running ComfyUI.
The text is written the same way ComfyUI's Save Image does it:
json.dumps() with the default ensure_ascii=True, so non-ASCII prompt text
becomes \\uXXXX escapes and fits in a plain tEXt chunk.

Usage:
    python make_sample_png.py sample.png
"""
import json
import struct
import sys
import zlib

PROMPT = {
    "4": {"class_type": "CheckpointLoaderSimple",
          "inputs": {"ckpt_name": "model.safetensors"}},
    "6": {"class_type": "CLIPTextEncode",
          "inputs": {"text": "창가에 앉은 고양이, 오후 햇빛", "clip": ["4", 1]}},
    "3": {"class_type": "KSampler",
          "inputs": {"seed": 42, "steps": 20, "cfg": 7.0, "sampler_name": "euler",
                     "model": ["4", 0], "positive": ["6", 0]}},
    "9": {"class_type": "SaveImage",
          "inputs": {"filename_prefix": "ComfyUI", "images": ["3", 0]}},
}

WORKFLOW = {
    "nodes": [
        {"id": 4, "type": "CheckpointLoaderSimple", "pos": [40, 120], "size": [315, 98]},
        {"id": 6, "type": "CLIPTextEncode", "pos": [400, 80], "size": [400, 200]},
        {"id": 3, "type": "KSampler", "pos": [860, 120], "size": [315, 262]},
        {"id": 9, "type": "SaveImage", "pos": [1220, 120], "size": [210, 270]},
    ],
    "links": [[1, 4, 1, 6, 0, "CLIP"], [2, 4, 0, 3, 0, "MODEL"],
              [3, 6, 0, 3, 1, "CONDITIONING"], [4, 3, 0, 9, 0, "IMAGE"]],
    "groups": [],
    "version": 0.4,
}


def chunk(ctype, data):
    body = ctype + data
    return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body))


def text_chunk(key, value):
    return chunk(b"tEXt", key.encode("latin-1") + b"\x00" + value.encode("latin-1"))


def make_png(path, width=64, height=64):
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)  # 8-bit RGB
    row = b"\x00" + bytes([200, 200, 200]) * width               # filter 0 + gray pixels
    idat = zlib.compress(row * height)

    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n")
        f.write(chunk(b"IHDR", ihdr))
        # text chunks go before the image data, like Pillow writes them
        f.write(text_chunk("prompt", json.dumps(PROMPT)))
        f.write(text_chunk("workflow", json.dumps(WORKFLOW)))
        f.write(chunk(b"IDAT", idat))
        f.write(chunk(b"IEND", b""))
    print(f"wrote {path}")


if __name__ == "__main__":
    make_png(sys.argv[1] if len(sys.argv) > 1 else "sample.png")
