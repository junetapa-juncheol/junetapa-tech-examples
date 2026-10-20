"""Read the workflow / prompt JSON that ComfyUI writes into a PNG.

ComfyUI's Save Image node stores two text chunks in every PNG:
  - "workflow": the full graph shown on the canvas (nodes, links, positions)
  - "prompt":   the API-format graph that was sent to the server

When you drop a file on the canvas, the frontend tries them in this order:
workflow -> prompt -> parameters (AUTOMATIC1111 text). If none is found,
the image is added as a Load Image node instead.

Usage:
    python extract_workflow.py image.png
    python extract_workflow.py image.png --save out
"""
import argparse
import json
import struct
import sys
import zlib
from pathlib import Path

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def read_text_chunks(path):
    """Return {keyword: text} for every tEXt / zTXt / iTXt chunk in a PNG."""
    data = Path(path).read_bytes()
    if not data.startswith(PNG_SIGNATURE):
        raise ValueError(f"not a PNG file: {path}")

    texts = {}
    pos = len(PNG_SIGNATURE)
    while pos + 8 <= len(data):
        length, ctype = struct.unpack(">I4s", data[pos:pos + 8])
        body = data[pos + 8:pos + 8 + length]

        if ctype == b"tEXt":
            key, _, value = body.partition(b"\x00")
            texts[key.decode("latin-1")] = value.decode("latin-1")
        elif ctype == b"zTXt":
            key, _, rest = body.partition(b"\x00")
            texts[key.decode("latin-1")] = zlib.decompress(rest[1:]).decode("latin-1")
        elif ctype == b"iTXt":
            key, _, rest = body.partition(b"\x00")
            compressed = rest[0]
            _lang, _, rest = rest[2:].partition(b"\x00")
            _translated, _, value = rest.partition(b"\x00")
            if compressed:
                value = zlib.decompress(value)
            texts[key.decode("latin-1")] = value.decode("utf-8")
        elif ctype == b"IEND":
            break

        # 4 bytes length + 4 bytes type + data + 4 bytes CRC
        pos += 12 + length
    return texts


def describe(texts):
    """Print what ComfyUI would do with this file."""
    if "workflow" in texts:
        wf = json.loads(texts["workflow"])
        nodes = wf.get("nodes", [])
        print(f"workflow: {len(nodes)} nodes, {len(wf.get('links', []))} links")
        for node in nodes:
            print(f"  - #{node.get('id')} {node.get('type')} at {node.get('pos')}")
    if "prompt" in texts:
        prompt = json.loads(texts["prompt"])
        print(f"prompt:   {len(prompt)} nodes (API format)")
        for node_id, node in prompt.items():
            print(f"  - {node_id}: {node.get('class_type')}")
    if "parameters" in texts:
        print("parameters: AUTOMATIC1111-style text found")

    if "workflow" in texts:
        result = "canvas restored from workflow (with layout)"
    elif "prompt" in texts:
        result = "nodes restored from prompt (no layout)"
    elif "parameters" in texts:
        result = "basic graph built from parameters text"
    else:
        result = "no metadata -> image goes into a Load Image node"
    print(f"\nOn drop, ComfyUI would use: {result}")


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("png", help="PNG file saved by ComfyUI")
    parser.add_argument("--save", metavar="DIR", help="write workflow.json / prompt.json here")
    args = parser.parse_args()

    texts = read_text_chunks(args.png)
    if not texts:
        print("No text chunks in this PNG.")
    describe(texts)

    if args.save:
        out = Path(args.save)
        out.mkdir(parents=True, exist_ok=True)
        for key in ("workflow", "prompt"):
            if key in texts:
                target = out / f"{key}.json"
                # json.loads turns \uXXXX escapes back into readable text
                pretty = json.dumps(json.loads(texts[key]), ensure_ascii=False, indent=2)
                target.write_text(pretty, encoding="utf-8")
                print(f"saved {target}")


if __name__ == "__main__":
    sys.exit(main())
