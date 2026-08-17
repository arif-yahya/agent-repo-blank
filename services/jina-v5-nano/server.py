#!/usr/bin/env python3
import os
import sys
from typing import List, Union
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from sentence_transformers import SentenceTransformer

app = FastAPI(title="Bekko Embedding v1 a8m Server")

MODEL_ID = os.environ.get("EMBEDDING_MODEL_ID", "hotchpotch/bekko-embedding-v1-a8m")
print(f"Loading embedding model: {MODEL_ID}...")

# Load Bekko model (ultra-lightweight ~8M params, 384-dim, ~30-50MB RAM)
model = SentenceTransformer(MODEL_ID, trust_remote_code=True)
print(f"Model {MODEL_ID} loaded successfully!")


def encode_texts(texts: List[str]) -> List[List[float]]:
    if not texts:
        return []
    embeddings = model.encode(texts, normalize_embeddings=True)
    return embeddings.tolist()


class EmbeddingRequest(BaseModel):
    input: Union[str, List[str]]
    model: str = MODEL_ID


@app.get("/health")
def health():
    return {"status": "ok", "model": MODEL_ID, "dim": 384, "params": "8M"}


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
