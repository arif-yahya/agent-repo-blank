# Jina Embeddings v5 Nano (ONNX)

- **Model Identifier**: `jaganadhg/jina-v5-nano-onnx`
- **Base Architecture**: `jinaai/jina-embeddings-v5-text-nano` (EuroBERT Backbone)
- **Embedding Dimension**: 768
- **Context Window**: 8,192 tokens
- **Runtime Engine**: `onnxruntime` (CPU Execution Provider)
- **Memory Footprint**: ~350 MB RAM

## Retrieval Task Prefixes
When using asymmetric retrieval queries:
- **Search Query Prefix**: `"Query: "`
- **Stored Document Prefix**: `"Document: "`

## Files
- `model.onnx`: Exported ONNX graph and weights for fast CPU inference.
- `tokenizer.json`: Pre-compiled Hugging Face Fast Tokenizer.
