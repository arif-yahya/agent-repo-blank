# Agent Blank Repository Template (`agent-repo-blank`)

A production-ready starter template for deploying **Google Antigravity (`agy`)** agents with:
- **Local Dense Embeddings**: Ultra-lightweight `hotchpotch/bekko-embedding-v1-a8m` (~8M params, 384-dim, ~30-50MB RAM).
- **Persistent Memory Layer**: SQLite-backed **Mnemosyne Memory** connected via Model Context Protocol (MCP).
- **Proactive Context Injection**: Sub-15ms `PreInvocation` lifecycle hooks in `hooks.json`.
- **Systemd Daemons**: Managed `local-model.service` microservice and automated nightly consolidation timers.
- **Tailscale Ready**: Pre-configured exit node & Tailscale SSH runbooks.

---

## Repository Structure

```text
├── .agents/
│   ├── agents/
│   │   └── archivist/agent.md       # Memory curation and audit subagent
│   ├── skills/
│   │   ├── tailscale-setup/SKILL.md # Tailscale exit node & SSH runbook
│   │   └── mnemosyne-setup/SKILL.md # Mnemosyne & local model runbook
│   └── hooks.json                   # PreInvocation proactive memory hook
├── docs/
│   └── mnemosyne_implementation_plan.md
├── models/
│   ├── README.md
│   ├── bekko-v1-a8m/                # Primary model card (384-dim, ~8M params)
│   └── jina-v5-nano-onnx/           # Alternative model card (768-dim, ~239M params)
├── services/
│   ├── local-model/
│   │   ├── server.py                # Local FastAPI microservice (port 8001)
│   │   ├── bekko-v1-a8m/            # Model documentation
│   │   ├── jina-v5-nano-onnx/       # Model documentation
│   │   └── scripts/
│   │       └── mnemosyne_hook.py    # Instant transcript memory lookup
│   └── systemd/
│       ├── local-model.service      # Systemd daemon for local embeddings
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
   sudo systemctl status local-model mnemosyne-sleep.timer
   curl http://127.0.0.1:8001/health
   mnemosyne stats
   ```

4. **Launch Antigravity Agent**:
   ```bash
   agy
   ```
