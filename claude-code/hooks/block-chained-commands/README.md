# 이어 붙인 셸 명령 막는 Claude Code 훅

`cmd1 && cmd2`, `a | b`, `$(...)`처럼 한 줄에 이어 붙인 명령을 실행 전에 거절하고, 나눠서 다시 쓰라고 알려 주는 PreToolUse 훅입니다.
A Claude Code PreToolUse hook that refuses chained shell commands and asks for one command per call.

- 확인한 날: 2026-10-21 (Claude Code 공식 문서 Hooks 기준 · 바뀌면 함께 고침)
- 필요한 것: Python 3.8+ (표준 라이브러리만) · Claude Code

## 실행

```bash
mkdir -p .claude/hooks
cp block_chained.py .claude/hooks/
python test_samples.py        # samples/ 의 입력으로 거절/통과 확인
```

그다음 `settings.example.json`의 `hooks` 부분을 프로젝트의 `.claude/settings.json`에 넣습니다. Windows에서 `python`이 다른 이름이면 그 이름으로 바꿉니다.

거절할 때 훅이 내보내는 값:

```json
{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
 "permissionDecisionReason": "Chained command found (&&). Run each command as its own tool call, ..."}}
```

## 왜 막나

- 여러 명령이 한 줄에 붙어 있으면 허용 목록과 맞춰 보기 어렵고, 무엇이 실행되는지 한눈에 읽기도 어렵습니다.
- 거절 이유가 바로 돌아가므로 명령을 나눠 다시 시도하게 됩니다.

## 무엇을 거절하나

| 거절 | 통과 |
|---|---|
| 따옴표 밖 `;` `&&` `\|\|` `\|` `$(` | 따옴표 안의 같은 기호 (`grep -E "a;b\|c"`) |
| 두 줄 이상 명령 | `2>&1` 같은 출력 돌리기 |
| bash 뒤에 붙인 `&` | heredoc(`<<EOF`) · PowerShell here-string(`@' '@`) |
| `python -c` · `node -e` 한 줄 코드 | 그 밖의 한 줄 명령 |

## 파일

| 파일 | 하는 일 |
|---|---|
| `block_chained.py` | 훅 본체 · stdin JSON의 `tool_name`이 Bash · PowerShell일 때 `tool_input.command`를 검사 |
| `settings.example.json` | `.claude/settings.json`에 넣을 연결 조각 |
| `samples/*.json` | 시험 입력 · 파일 이름이 `deny_`면 거절, `allow_`면 통과가 맞음 |
| `test_samples.py` | samples 를 하나씩 훅에 넣어 결과 확인 |

## 주의

- 판단이 안 되는 입력(JSON 아님 · 명령 없음)은 그냥 통과시킵니다.
- 잠시 끄려면 환경 변수 `BLOCK_CHAINED_OFF=1`을 둡니다.
- 따옴표 짝이 안 맞는 명령 같은 특이한 경우는 정확하지 않을 수 있습니다. 자기 환경에 맞게 samples 를 늘려 확인합니다.
