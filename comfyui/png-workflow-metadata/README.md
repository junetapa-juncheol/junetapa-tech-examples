# ComfyUI PNG 안의 워크플로 꺼내기

ComfyUI가 PNG에 적어 두는 workflow · prompt 두 JSON을 꺼내 보고, 공유 전에 지우는 예제입니다.
Read (and strip) the workflow / prompt JSON that ComfyUI stores in PNG text chunks.

- 블로그 글: https://junetapa.com/blog/dev/posts/ai-tools/comfyui-load-workflow-from-png.html
- 확인한 날: 2026-10-20 (ComfyUI 공식 문서 Workflow Metadata · 프런트엔드 png.ts · app.ts 기준 · 바뀌면 글과 함께 고침)
- 필요한 것: Python 3.8+ (표준 라이브러리만 씀 · 설치할 것 없음)

## 실행

```bash
python make_sample_png.py sample.png          # 메타데이터가 든 시험용 PNG 만들기
python extract_workflow.py sample.png --save out   # 요약 보기 + out/workflow.json, out/prompt.json 저장
python strip_metadata.py sample.png clean.png  # 글 청크를 뺀 사본 만들기
```

ComfyUI로 만든 그림이 있으면 `sample.png` 자리에 그 파일을 넣으면 됩니다.

출력 예:

```
workflow: 4 nodes, 4 links
  - #4 CheckpointLoaderSimple at [40, 120]
  ...
prompt:   4 nodes (API format)
  - 4: CheckpointLoaderSimple
  ...

On drop, ComfyUI would use: canvas restored from workflow (with layout)
```

## 파일

| 파일 | 하는 일 |
|---|---|
| `extract_workflow.py` | PNG의 tEXt · zTXt · iTXt 청크를 읽어 workflow · prompt를 보여 주고 JSON으로 저장 · 끌어다 놓았을 때 ComfyUI가 무엇을 쓸지(workflow → prompt → parameters → Load Image) 알려 줌 |
| `make_sample_png.py` | ComfyUI Save Image와 같은 방식(json.dumps 기본값 → tEXt)으로 메타데이터를 넣은 64×64 시험 그림을 만듦 |
| `strip_metadata.py` | 그림 데이터는 그대로 두고 글 청크만 뺀 사본을 만듦 · 프롬프트·시드·모델 파일 이름을 드러내고 싶지 않을 때 |

## 주의

- 메타데이터에는 프롬프트 글, 시드, 체크포인트·LoRA 파일 이름이 그대로 들어 있습니다. 나누기 전에 확인합니다.
- 워크플로에는 모델 파일 · 입력 그림 · 커스텀 노드가 들어 있지 않습니다. 열려도 바로 돌지 않을 수 있습니다.
- 받은 그림의 메타데이터는 누가 만들었는지 증명하지 않습니다. 모르는 곳의 커스텀 노드는 설치 전에 저장소부터 확인합니다.
- 키·토큰은 환경변수로 · 이 저장소엔 넣지 않습니다.
