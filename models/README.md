# Local Models Directory

This directory houses the local embedding and AI models used by the Antigravity workspace and memory layer.

## Active Models

### 1. [`jina-v5-nano-onnx`](./jina-v5-nano-onnx/)
- **Architecture**: EuroBERT-210M (Jina AI Embeddings v5 Nano)
- **Format**: ONNX Runtime (CPU-optimized)
- **Parameters**: ~239M
- **Embedding Dimension**: 768
- **Context Length**: 8,192 tokens
- **Source**: [Hugging Face: `jaganadhg/jina-v5-nano-onnx`](https://huggingface.co/jaganadhg/jina-v5-nano-onnx)
- **Serving Service**: `jina-embeddings.service` on `http://127.0.0.1:8001/v1/embeddings`

---

## Directory Structure
```text
models/
└── jina-v5-nano-onnx/
    ├── README.md           # Model card and specifications
    ├── model.onnx          # ONNX model graph & weights
    └── tokenizer.json      # Fast HuggingFace tokenizer
```
