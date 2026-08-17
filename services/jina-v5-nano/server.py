#!/usr/bin/env python3
import os
import sys
import numpy as np
from typing import List, Union
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import onnxruntime as ort
from tokenizers import Tokenizer
from huggingface_hub import hf_hub_download

app = FastAPI(title="Jina Embeddings v5 Nano ONNX Server")

REPO_ID = "jaganadhg/jina-v5-nano-onnx"
CACHE_DIR = os.path.expanduser("~/.cache/huggingface/hub")

print("Initializing Jina v5 Nano ONNX model...")
model_path = hf_hub_download(repo_id=REPO_ID, filename="model.onnx", cache_dir=CACHE_DIR)
tokenizer_path = hf_hub_download(repo_id=REPO_ID, filename="tokenizer.json", cache_dir=CACHE_DIR)

tokenizer = Tokenizer.from_file(tokenizer_path)
tokenizer.enable_truncation(max_length=8192)
tokenizer.enable_padding(pad_id=0, pad_token="[PAD]")

opts = ort.SessionOptions()
opts.intra_op_num_threads = max(1, os.cpu_count() or 2)
opts.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL

session = ort.InferenceSession(model_path, sess_options=opts, providers=["CPUExecutionProvider"])
print("Jina v5 Nano ONNX model loaded successfully!")


def encode_texts(texts: List[str]) -> List[List[float]]:
    if not texts:
        return []
    
    encodings = tokenizer.encode_batch(texts)
    input_ids = np.array([e.ids for e in encodings], dtype=np.int64)
    attention_mask = np.array([e.attention_mask for e in encodings], dtype=np.int64)
    
    inputs = {
        "input_ids": input_ids,
        "attention_mask": attention_mask
    }
    
    outputs = session.run(None, inputs)
    # Output is already pooled or (batch_size, 768)
    embeddings = outputs[0]
    if len(embeddings.shape) == 3:
        # Last token pooling or mean pooling if 3D
        embeddings = embeddings[:, -1, :]
        
    # L2 normalize
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    normalized = embeddings / norms
    return normalized.tolist()


class EmbeddingRequest(BaseModel):
    input: Union[str, List[str]]
    model: str = "jinaai/jina-embeddings-v5-text-nano"


@app.get("/health")
def health():
    return {"status": "ok", "model": REPO_ID, "dim": 768}


@app.post("/v1/embeddings")
def create_embeddings(req: EmbeddingRequest):
    try:
        texts = [req.input] if isinstance(req.input, str) else req.input
        embs = encode_texts(texts)
        data = [
            {"object": "embedding", "index": i, "embedding": emb}
            for i, emb in enumerate(embs)
        ]
        return {
            "object": "list",
            "data": data,
            "model": req.model,
            "usage": {"prompt_tokens": len(texts), "total_tokens": len(texts)}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="info")
