#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECT_PATH="$ROOT_DIR/macos/SgodAI-Mac/SgodAI-Mac.xcodeproj"
SCHEME="SgodAI-Mac"
CONFIGURATION="Release"
VERSION="${SGODAI_VERSION:-0.2.0}"
ARCHIVE_DIR="$ROOT_DIR/dist/macos"
DERIVED_DATA="$ROOT_DIR/build/xcode-derived-data"
APP_PATH="$DERIVED_DATA/Build/Products/$CONFIGURATION/SgodAI Market Radar.app"
ZIP_PATH="$ROOT_DIR/dist/SgodAI-Market-Radar-macOS-v$VERSION.zip"

if [[ -d "/Applications/Xcode-beta.app/Contents/Developer" ]]; then
  export DEVELOPER_DIR="${DEVELOPER_DIR:-/Applications/Xcode-beta.app/Contents/Developer}"
fi

mkdir -p "$ARCHIVE_DIR" "$ROOT_DIR/dist"

xcodebuild \
  -project "$PROJECT_PATH" \
  -scheme "$SCHEME" \
  -configuration "$CONFIGURATION" \
  -derivedDataPath "$DERIVED_DATA" \
  CODE_SIGNING_ALLOWED=NO \
  clean build

rm -rf "$ARCHIVE_DIR/SgodAI Market Radar.app"
ditto "$APP_PATH" "$ARCHIVE_DIR/SgodAI Market Radar.app"
ditto -c -k --keepParent "$ARCHIVE_DIR/SgodAI Market Radar.app" "$ZIP_PATH"

echo "$ZIP_PATH"
