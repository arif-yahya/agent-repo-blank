#!/usr/bin/env bash
set -e

echo "=== Antigravity & Mnemosyne Workspace Bootstrap ==="

# 1. System packages
echo "[1/5] Installing base packages..."
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv pipx git gh

# 2. Python ML & Memory dependencies
echo "[2/5] Installing Python dependencies..."
pip install --break-system-packages mnemosyne-memory onnxruntime tokenizers huggingface-hub fastapi uvicorn numpy

# 3. Setup MCP Configuration
echo "[3/5] Configuring global MCP server..."
mkdir -p ~/.gemini/config
cat << "EOF" > ~/.gemini/config/mcp_config.json
{
  "mcpServers": {
    "mnemosyne": {
      "command": "/home/ubuntu/.local/bin/mnemosyne",
      "args": ["mcp"]
    }
  }
}
EOF

# 4. Systemd services installation
echo "[4/5] Registering systemd daemons..."
sudo cp -p services/systemd/jina-embeddings.service /etc/systemd/system/
sudo cp -p services/systemd/mnemosyne-sleep.service /etc/systemd/system/
sudo cp -p services/systemd/mnemosyne-sleep.timer /etc/systemd/system/

sudo systemctl daemon-reload
sudo systemctl enable --now jina-embeddings
sudo systemctl enable --now mnemosyne-sleep.timer

# 5. Mnemosyne configuration
echo "[5/5] Configuring Mnemosyne local embeddings..."
~/.local/bin/mnemosyne config set embeddings_via_api true
~/.local/bin/mnemosyne config set embedding_api_url "http://127.0.0.1:8001/v1/embeddings"
~/.local/bin/mnemosyne config set embedding_model "jinaai/jina-embeddings-v5-text-nano"
~/.local/bin/mnemosyne config set embedding_dim 768
~/.local/bin/mnemosyne config reload

echo "=== Bootstrap Complete! All services active ==="
