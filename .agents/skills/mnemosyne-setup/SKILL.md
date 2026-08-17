---
name: mnemosyne-setup
description: >-
  Runbook for installing, configuring, and optimizing Mnemosyne memory for AI agents,
  including setting up local Jina v5 Nano ONNX embeddings via a systemd microservice,
  configuring vector retrieval, automated sleep timers, PreInvocation lifecycle hooks, and registering the MCP server.
---

# Mnemosyne Memory & Local ONNX Embeddings Setup

Use this skill when installing Mnemosyne memory, configuring local embedding backends (Jina v5 Nano ONNX), setting up persistent systemd services, automated sleep timers, lifecycle hooks, or connecting Mnemosyne to Antigravity via MCP.

## 1. Mnemosyne Installation & MCP Registration

### A. Install Package
```bash
pip install --break-system-packages mnemosyne-memory
```

### B. Register Global MCP Server in Antigravity
Add to `~/.gemini/config/mcp_config.json`:
```json
{
  "mcpServers": {
    "mnemosyne": {
      "command": "/home/ubuntu/.local/bin/mnemosyne",
      "args": ["mcp"]
    }
  }
}
```

## 2. Deploying Local Jina v5 Nano ONNX Service

### A. Install Runtime Dependencies
```bash
pip install --break-system-packages onnxruntime tokenizers huggingface-hub fastapi uvicorn numpy
```

### B. Create Microservice Script (`/home/ubuntu/services/jina-v5-nano/server.py`)
```python
import os, numpy as np
from typing import List, Union
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn, onnxruntime as ort
from tokenizers import Tokenizer
from huggingface_hub import hf_hub_download

app = FastAPI(title="Jina Embeddings v5 Nano ONNX Server")
REPO_ID = "jaganadhg/jina-v5-nano-onnx"

model_path = hf_hub_download(repo_id=REPO_ID, filename="model.onnx")
tokenizer_path = hf_hub_download(repo_id=REPO_ID, filename="tokenizer.json")

tokenizer = Tokenizer.from_file(tokenizer_path)
tokenizer.enable_truncation(max_length=8192)
tokenizer.enable_padding(pad_id=0, pad_token="[PAD]")

opts = ort.SessionOptions()
opts.intra_op_num_threads = max(1, os.cpu_count() or 2)
session = ort.InferenceSession(model_path, sess_options=opts, providers=["CPUExecutionProvider"])

def encode_texts(texts: List[str]) -> List[List[float]]:
    encodings = tokenizer.encode_batch(texts)
    input_ids = np.array([e.ids for e in encodings], dtype=np.int64)
    attention_mask = np.array([e.attention_mask for e in encodings], dtype=np.int64)
    outputs = session.run(None, {"input_ids": input_ids, "attention_mask": attention_mask})
    embeddings = outputs[0]
    if len(embeddings.shape) == 3:
        embeddings = embeddings[:, -1, :]
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return (embeddings / norms).tolist()

class EmbeddingRequest(BaseModel):
    input: Union[str, List[str]]
    model: str = "jinaai/jina-embeddings-v5-text-nano"

@app.get("/health")
def health():
    return {"status": "ok", "model": REPO_ID, "dim": 768}

@app.post("/v1/embeddings")
def create_embeddings(req: EmbeddingRequest):
    texts = [req.input] if isinstance(req.input, str) else req.input
    embs = encode_texts(texts)
    return {
        "object": "list",
        "data": [{"object": "embedding", "index": i, "embedding": emb} for i, emb in enumerate(embs)],
        "model": req.model
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)
```

### C. Systemd Unit Setup
Create `/etc/systemd/system/jina-embeddings.service`:
```ini
[Unit]
Description=Jina Embeddings v5 Nano ONNX Service
After=network.target

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/services/jina-v5-nano
ExecStart=/usr/bin/python3 /home/ubuntu/services/jina-v5-nano/server.py
Restart=always
RestartSec=3
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```
Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now jina-embeddings
```

## 3. Configuring Mnemosyne for Local Embeddings

Update `~/.hermes/mnemosyne/config.yaml`:
```yaml
embeddings_via_api: true
embedding_api_url: http://127.0.0.1:8001/v1/embeddings
embedding_model: jinaai/jina-embeddings-v5-text-nano
embedding_dim: 768
```

Reload and reindex:
```bash
mnemosyne config reload
mnemosyne reindex --yes
```

## 4. Automated Nightly Consolidation (Sleep Timer)

Create `/etc/systemd/system/mnemosyne-sleep.service`:
```ini
[Unit]
Description=Mnemosyne Memory Consolidation (Sleep Cycle)
After=network.target

[Service]
Type=oneshot
User=ubuntu
ExecStart=/home/ubuntu/.local/bin/mnemosyne sleep
Environment=HOME=/home/ubuntu
```

Create `/etc/systemd/system/mnemosyne-sleep.timer`:
```ini
[Unit]
Description=Run Mnemosyne Memory Consolidation Nightly at 3 AM

[Timer]
OnCalendar=*-*-* 03:00:00
Persistent=true

[Install]
WantedBy=timers.target
```
Enable:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now mnemosyne-sleep.timer
```

## 5. Automated Context Injection via Lifecycle Hooks (`hooks.json`)

To automatically inject relevant memories into the agent's context before each turn without manual intervention:

### A. Create Hook Script (`/home/ubuntu/services/jina-v5-nano/scripts/mnemosyne_hook.py`)
```python
#!/usr/bin/env python3
import sys, json, subprocess, os

def main():
    try:
        input_data = json.load(sys.stdin)
    except Exception:
        print("{}"); return

    transcript_path = input_data.get("transcriptPath")
    user_query = ""
    if transcript_path and os.path.exists(transcript_path):
        try:
            with open(transcript_path, "r", encoding="utf-8") as f:
                for line in reversed(f.readlines()[-20:]):
                    rec = json.loads(line)
                    if rec.get("type") == "USER_INPUT" and rec.get("content"):
                        user_query = rec["content"].strip()
                        break
        except Exception:
            pass

    if not user_query or len(user_query) < 3 or user_query.startswith("/"):
        print("{}"); return

    try:
        proc = subprocess.run(
            ["/home/ubuntu/.local/bin/mnemosyne", "recall", user_query, "2"],
            capture_output=True, text=True, timeout=2
        )
        output = proc.stdout.strip()
        memories = [line.replace("Content:", "•").strip() for line in output.splitlines() if line.strip().startswith("Content:")]
        if memories:
            msg = "🧠 [Mnemosyne Proactive Context]\n" + "\n".join(memories[:2])
            print(json.dumps({"injectSteps": [{"ephemeralMessage": msg}]}))
            return
    except Exception:
        pass

    print("{}")

if __name__ == "__main__":
    main()
```
Make executable: `chmod +x /home/ubuntu/services/jina-v5-nano/scripts/mnemosyne_hook.py`

### B. Register in `hooks.json`
Add to `.agents/hooks.json` (workspace) or `~/.gemini/config/hooks.json` (global):
```json
{
  "mnemosyne-proactive-recall": {
    "enabled": true,
    "PreInvocation": [
      {
        "type": "command",
        "command": "/usr/bin/python3 /home/ubuntu/services/jina-v5-nano/scripts/mnemosyne_hook.py",
        "timeout": 5
      }
    ]
  }
}
```

## 6. Verification & Operations

- Check embeddings service: `curl http://127.0.0.1:8001/health`
- Store test memory: `mnemosyne store "<content>" "<source>" 0.9`
- Semantic recall: `mnemosyne recall "<query>"`
- View stats: `mnemosyne stats`
- Run health report: `mnemosyne doctor`
- Run database integrity check: `mnemosyne verify`
- Audit memory noise: `mnemosyne hygiene audit`
- Create backup snapshot: `mnemosyne backup`
