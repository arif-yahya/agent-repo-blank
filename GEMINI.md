# Antigravity Workspace Guidelines & Context

## 1. Memory Directives (Mnemosyne Integration)
- **Proactive Recall**: Before beginning non-trivial tasks or debugging, use `recall_memory` to check for prior environment quirks, architectural decisions, and preferences.
- **Proactive Storage**: After discovering significant environment facts, resolving difficult issues, or setting up new services, proactively store the insight using `save_memory` (importance >= 0.8).
- **Conciseness**: Keep stored memory entries atomic, specific, and actionable.

## 2. Infrastructure & Environment
- **Tailscale**: Configured as an Exit Node with SSH enabled (`100.77.235.99`) and `--accept-dns=false`.
- **Embedding Service**: Local `local-model.service` running on `http://127.0.0.1:8001/v1/embeddings` (**Bekko v1 a8m**, 384-dim, ~30MB RAM).
- **Memory Storage**: Mnemosyne SQLite database at `~/.hermes/mnemosyne/data/mnemosyne.db`.
