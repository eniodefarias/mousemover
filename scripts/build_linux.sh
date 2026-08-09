#!/usr/bin/env bash
set -euo pipefail

python -m pip install -e ".[dev]"

pyinstaller \
  --noconfirm \
  --clean \
  --onefile \
  --name MouseMover \
  --collect-submodules mousemover.plugins \
  --paths src \
  launcher.py

echo "Gerado: dist/MouseMover"
echo "Sem argumentos: GUI"
echo "Com argumentos: CLI"
