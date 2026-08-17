# Bekko Embedding v1 a8m

- **Model Identifier**: `hotchpotch/bekko-embedding-v1-a8m`
- **Author**: Yuichi Tateno (`hotchpotch`)
- **Base Architecture**: Pruned `mmBERT-small` (4 layers)
- **Active Parameters**: **~8 Million** (Ultra-compact)
- **Embedding Dimension**: 384 (supports Matryoshka down to 256, 128, 64)
- **Context Window**: 8,192 tokens
- **RAM Footprint**: **$\sim 30\text{ MB} - 50\text{ MB}$**
- **Serving Service**: `jina-embeddings.service` on `http://127.0.0.1:8001/v1/embeddings`

## Characteristics
- **Blazing Fast**: Designed for edge devices, Raspberry Pi 5, in-browser WASM, and ultra-low resource Linux servers.
- **Multilingual Support**: Supports English, Japanese, and diverse multilingual benchmarks (MMTEB v2).
