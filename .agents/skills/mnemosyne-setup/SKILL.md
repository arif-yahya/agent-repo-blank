---
name: mnemosyne-setup
description: >-
  Runbook for installing, configuring, and optimizing Mnemosyne memory for AI agents,
  including setting up local embedding microservices (Bekko v1 a8m / Jina v5 Nano) via systemd,
  configuring vector retrieval, automated sleep timers, PreInvocation lifecycle hooks, and registering the MCP server.
---

# Mnemosyne Memory & Local Embeddings Setup

Use this skill when installing Mnemosyne memory, configuring local embedding backends (`hotchpotch/bekko-embedding-v1-a8m` or `jina-v5-nano-onnx`), setting up persistent systemd services, automated sleep timers, lifecycle hooks, or connecting Mnemosyne to Antigravity via MCP.

## 1. Mnemosyne Installation & MCP Registration

### A. Install Package
```bash
pip install --break-system-packages mnemosyne-memory sentence-transformers onnxruntime tokenizers huggingface-hub fastapi uvicorn numpy
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

## 2. Deploying Local Embedding Service (`~/services/local-model/server.py`)

### A. Create Microservice Script (`/home/ubuntu/services/local-model/server.py`)
```python
#!/usr/bin/env python3
import os, sys
from typing import List, Union
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from sentence_transformers import SentenceTransformer

app = FastAPI(title="Local Embedding Server")

MODEL_ID = os.environ.get("EMBEDDING_MODEL_ID", "hotchpotch/bekko-embedding-v1-a8m")
model = SentenceTransformer(MODEL_ID, trust_remote_code=True)

def encode_texts(texts: List[str]) -> List[List[float]]:
    if not texts: return []
    embeddings = model.encode(texts, normalize_embeddings=True)
    return embeddings.tolist()

class EmbeddingRequest(BaseModel):
    input: Union[str, List[str]]
    model: str = MODEL_ID

@app.get("/health")
def health():
    return {"status": "ok", "model": MODEL_ID, "dim": 384}

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

### B. Systemd Unit Setup
Create `/etc/systemd/system/local-model.service`:
```ini
[Unit]
Description=Local Model Embedding Service (Bekko v1 a8m / Jina v5 Nano)
After=network.target

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/services/local-model
ExecStart=/usr/bin/python3 /home/ubuntu/services/local-model/server.py
Restart=always
RestartSec=3
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```
Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now local-model
```

## 3. Configuring Mnemosyne for Local Embeddings

Update `~/.hermes/mnemosyne/config.yaml`:
```yaml
embeddings_via_api: true
embedding_api_url: http://127.0.0.1:8001/v1/embeddings
embedding_model: hotchpotch/bekko-embedding-v1-a8m
embedding_dim: 384
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

Hook script: `/home/ubuntu/services/local-model/scripts/mnemosyne_hook.py`

Add to `.agents/hooks.json` (workspace) or `~/.gemini/config/hooks.json` (global):
```json
{
  "mnemosyne-proactive-recall": {
    "enabled": true,
    "PreInvocation": [
      {
        "type": "command",
        "command": "/usr/bin/python3 /home/ubuntu/services/local-model/scripts/mnemosyne_hook.py",
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
