#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECT_PATH="$ROOT_DIR/ios/SgodAI-iOS/SgodAI-iOS.xcodeproj"
SCHEME="SgodAI-iOS"
CONFIGURATION="${CONFIGURATION:-Release}"
VERSION="${SGODAI_VERSION:-0.2.1}"
DERIVED_DATA="$ROOT_DIR/build/ios-derived-data"
ARCHIVE_DIR="$ROOT_DIR/dist/ios"
APP_PATH="$DERIVED_DATA/Build/Products/$CONFIGURATION-iphonesimulator/SgodAI Market Radar.app"
ZIP_PATH="$ROOT_DIR/dist/SgodAI-Market-Radar-iOS-Simulator-v$VERSION.zip"
DESTINATION="${IOS_DESTINATION:-generic/platform=iOS Simulator}"

if [[ -d "/Applications/Xcode-beta.app/Contents/Developer" ]]; then
  export DEVELOPER_DIR="${DEVELOPER_DIR:-/Applications/Xcode-beta.app/Contents/Developer}"
fi

mkdir -p "$ARCHIVE_DIR" "$ROOT_DIR/dist"

xcodebuild \
  -project "$PROJECT_PATH" \
  -scheme "$SCHEME" \
  -configuration "$CONFIGURATION" \
  -destination "$DESTINATION" \
  -derivedDataPath "$DERIVED_DATA" \
  CODE_SIGNING_ALLOWED=NO \
  clean build

rm -rf "$ARCHIVE_DIR/SgodAI Market Radar.app"
ditto "$APP_PATH" "$ARCHIVE_DIR/SgodAI Market Radar.app"
ditto -c -k --keepParent "$ARCHIVE_DIR/SgodAI Market Radar.app" "$ZIP_PATH"

echo "$ZIP_PATH"
