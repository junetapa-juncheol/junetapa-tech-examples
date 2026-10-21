# junetapa-tech-examples

junetapa.com 테크 글에 나오는 예제 코드를 글 하나에 폴더 하나로 모았습니다.
Example code for the tech posts on junetapa.com — one folder per post.

## 예제 목록

| 폴더 | 블로그 글 | 필요한 것 |
|---|---|---|
| [comfyui/png-workflow-metadata](comfyui/png-workflow-metadata) | [ComfyUI 워크플로 불러오기 — PNG 한 장에 노드가 되살아나는 이유](https://junetapa.com/blog/dev/posts/ai-tools/comfyui-load-workflow-from-png.html) | Python 3.8+ |
| [audio/loudness-check](audio/loudness-check) | — | Python 3.8+ · ffmpeg |
| [claude-code/hooks/block-chained-commands](claude-code/hooks/block-chained-commands) | — | Python 3.8+ · Claude Code |
| [local-ai/private-summary](local-ai/private-summary) | — | Python 3.8+ · Ollama |

글이 새로 나오면 폴더도 하나씩 늘어납니다. 글보다 코드를 먼저 올린 폴더는 블로그 칸이 비어 있습니다.

## 쓰는 법

```bash
git clone https://github.com/junetapa-juncheol/junetapa-tech-examples.git
cd junetapa-tech-examples/comfyui/png-workflow-metadata
```

각 폴더 README의 «실행» 절을 따라 하면 됩니다.

## 원칙

- 키·토큰은 환경변수로 넣고, 이 저장소에는 올리지 않습니다.
- 예제는 글을 쓴 날의 공식 문서를 기준으로 합니다. 도구가 바뀌면 글과 함께 고칩니다.

## License

[MIT](LICENSE)
