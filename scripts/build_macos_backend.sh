#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-$ROOT_DIR/.venv/bin/python}"
BUILD_DIR="$ROOT_DIR/build/pyinstaller"
DIST_DIR="$ROOT_DIR/dist/backend"

if [[ -d "/Applications/Xcode-beta.app/Contents/Developer" ]]; then
  export DEVELOPER_DIR="${DEVELOPER_DIR:-/Applications/Xcode-beta.app/Contents/Developer}"
  export PATH="$DEVELOPER_DIR/Toolchains/XcodeDefault.xctoolchain/usr/bin:$DEVELOPER_DIR/usr/bin:$PATH"
fi

"$PYTHON_BIN" -m PyInstaller \
  --noconfirm \
  --clean \
  --onefile \
  --name sgodai-backend \
  --distpath "$DIST_DIR" \
  --workpath "$BUILD_DIR/work" \
  --specpath "$BUILD_DIR" \
  --collect-submodules app \
  --hidden-import dotenv \
  --hidden-import yaml \
  "$ROOT_DIR/app/desktop_backend.py"

chmod +x "$DIST_DIR/sgodai-backend"
echo "$DIST_DIR/sgodai-backend"
