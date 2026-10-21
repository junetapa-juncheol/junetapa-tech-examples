"""PreToolUse hook: refuse shell commands chained with ; && || | $( ) or newlines.

Separators inside quotes are fine. Set BLOCK_CHAINED_OFF=1 to turn it off.
"""
import json
import os
import re
import sys

INLINE_CODE = re.compile(r"^(python3?|py|node)(\.exe)?\s+(-X\s+\S+\s+)*(-c|-e|--eval)\b", re.I)


def find_separators(cmd, powershell=False):
    found = []
    escape = "`" if powershell else "\\"
    quote = None
    i = 0
    while i < len(cmd):
        ch = cmd[i]
        if quote:
            if ch == escape and quote == '"':
                i += 2
                continue
            if ch == quote:
                # PowerShell writes a literal ' inside '...' as ''
                if powershell and quote == "'" and cmd[i + 1:i + 2] == "'":
                    i += 2
                    continue
                quote = None
            i += 1
            continue

        if ch in "\"'":
            quote = ch
        elif ch == escape:
            i += 1
        elif cmd[i:i + 2] in ("&&", "||"):
            found.append(cmd[i:i + 2])
            i += 1
        elif cmd[i:i + 2] == "$(":
            found.append("$()")
            i += 1
        elif ch in ";|":
            found.append(ch)
        elif ch == "\n" and cmd[:i].strip() and cmd[i + 1:].strip():
            found.append("newline")
        elif ch == "&" and not powershell and cmd[i - 1:i] not in "<>" and cmd[i + 1:i + 2] not in (">", "1", "2"):
            # bash background job; leaves 2>&1 and &> alone
            found.append("&")
        i += 1
    return found


def main():
    if os.environ.get("BLOCK_CHAINED_OFF") == "1":
        return
    try:
        event = json.load(sys.stdin)
    except ValueError:
        return

    tool = event.get("tool_name")
    if tool not in ("Bash", "PowerShell"):
        return
    cmd = str(event.get("tool_input", {}).get("command", "")).strip()
    if not cmd:
        return

    powershell = tool == "PowerShell"
    # heredocs and here-strings are usually file content, skip them
    if "<<" in cmd and not powershell:
        return
    if powershell and ("@'" in cmd or '@"' in cmd):
        return

    found = find_separators(cmd, powershell)
    if INLINE_CODE.match(cmd):
        found.append("inline -c/-e code")
    if not found:
        return

    reason = (
        f"Chained command found ({', '.join(sorted(set(found)))}). "
        "Run each command as its own tool call, or write the steps to a script file "
        "and run that file with a single command."
    )
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }))


if __name__ == "__main__":
    main()
