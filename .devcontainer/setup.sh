#!/usr/bin/env bash
# Runs once, when the codespace is created.
set -euo pipefail

# tshark, without the "may non-root users capture?" prompt: the labs only read files.
sudo apt-get update -q
sudo DEBIAN_FRONTEND=noninteractive apt-get install -yq tshark

# opencode installs into ~/.opencode/bin; link it where a Jupyter kernel finds it too.
curl -fsSL https://opencode.ai/install | bash
sudo ln -sf "$HOME/.opencode/bin/opencode" /usr/local/bin/opencode

# uv, then the lab dependencies into .venv
curl -LsSf https://astral.sh/uv/install.sh | sh
"$HOME/.local/bin/uv" sync --group labs

echo
echo "Ready. Log in to Copilot once:   opencode auth login --provider github-copilot"
