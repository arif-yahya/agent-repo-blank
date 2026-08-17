# Local Models Directory

This directory houses the local embedding models used by the Antigravity workspace and Mnemosyne memory layer.

## Active Models

### 1. [`bekko-v1-a8m`](./bekko-v1-a8m/) — **Primary Embedding Model** ⚡
- **Architecture**: Pruned `mmBERT-small` (4 layers)
- **Parameters**: **~8M** (Ultra-compact)
- **RAM Usage**: **~30MB - 50MB**
- **Dimension**: 384
- **Context Length**: 8,192 tokens
- **Source**: [Hugging Face: `hotchpotch/bekko-embedding-v1-a8m`](https://huggingface.co/hotchpotch/bekko-embedding-v1-a8m)
- **Serving Service**: `jina-embeddings.service` on `http://127.0.0.1:8001/v1/embeddings`

### 2. [`jina-v5-nano-onnx`](./jina-v5-nano-onnx/) — Alternative Model
- **Architecture**: EuroBERT-210M (Jina AI Embeddings v5 Nano)
- **Parameters**: ~239M
- **RAM Usage**: ~350MB
- **Dimension**: 768
- **Context Length**: 8,192 tokens
- **Source**: [Hugging Face: `jaganadhg/jina-v5-nano-onnx`](https://huggingface.co/jaganadhg/jina-v5-nano-onnx)
