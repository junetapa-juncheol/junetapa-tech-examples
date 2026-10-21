"""Feed every file in samples/ to the hook. deny_* should be refused, allow_* should pass."""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
HOOK = HERE / "block_chained.py"

failed = 0
for sample in sorted((HERE / "samples").glob("*.json")):
    result = subprocess.run(
        [sys.executable, str(HOOK)],
        input=sample.read_text(encoding="utf-8"),
        capture_output=True, text=True,
    )
    out = result.stdout.strip()
    denied = bool(out) and json.loads(out)["hookSpecificOutput"]["permissionDecision"] == "deny"
    expected = sample.name.startswith("deny_")
    status = "ok  " if denied == expected else "FAIL"
    failed += denied != expected
    print(f"{status} {sample.name:28} {'denied' if denied else 'allowed'}")

sys.exit(1 if failed else 0)
