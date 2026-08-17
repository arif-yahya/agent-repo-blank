# Agent Blank Repository Template (`agent-repo-blank`)

A production-ready starter template for deploying **Google Antigravity (`agy`)** agents with:
- **Local Dense Embeddings**: CPU-optimized `jina-embeddings-v5-text-nano` via ONNX Runtime (~350MB RAM).
- **Persistent Memory Layer**: SQLite-backed **Mnemosyne Memory** connected via Model Context Protocol (MCP).
- **Proactive Context Injection**: Sub-15ms `PreInvocation` lifecycle hooks in `hooks.json`.
- **Systemd Daemons**: Managed embedding microservice and automated nightly consolidation timers.
- **Tailscale Ready**: Pre-configured exit node & Tailscale SSH runbooks.

---

## Repository Structure

```text
├── .agents/
│   ├── agents/
│   │   └── archivist/agent.md       # Memory curation and audit subagent
│   ├── skills/
│   │   ├── tailscale-setup/SKILL.md # Tailscale exit node & SSH runbook
│   │   └── mnemosyne-setup/SKILL.md # Mnemosyne & local ONNX runbook
│   └── hooks.json                   # PreInvocation proactive memory hook
├── docs/
│   └── mnemosyne_implementation_plan.md
├── models/
│   ├── README.md
│   └── jina-v5-nano-onnx/           # Local ONNX model specifications & card
├── services/
│   ├── jina-v5-nano/
│   │   ├── server.py                # Local FastAPI ONNX microservice (port 8001)
│   │   └── scripts/mnemosyne_hook.py# Instant transcript memory lookup
│   └── systemd/
│       ├── jina-embeddings.service  # Systemd daemon for local embeddings
│       ├── mnemosyne-sleep.service  # Consolidation service
│       └── mnemosyne-sleep.timer    # Daily 3:00 AM consolidation timer
├── scripts/
│   └── bootstrap.sh                 # One-click installer & service configurator
├── GEMINI.md                        # Agent memory directives & workspace context
└── .gitignore
```

---

## Quick Start (Deploy to a New Machine)

1. **Clone this template**:
   ```bash
   git clone <repo-url> my-agent-workspace
   cd my-agent-workspace
   ```

2. **Run One-Click Bootstrap**:
   ```bash
   ./scripts/bootstrap.sh
   ```

3. **Verify Everything is Active**:
   ```bash
   sudo systemctl status jina-embeddings mnemosyne-sleep.timer
   curl http://127.0.0.1:8001/health
   mnemosyne stats
   ```

4. **Launch Antigravity Agent**:
   ```bash
   agy
   ```
