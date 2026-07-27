#!/bin/sh
# install-local.sh — install orqctl from locally built standalone binaries.
# Run via: pnpm install:local  (after `pnpm build:bin`)
#
# Consumes the raw, self-contained binaries emitted by scripts/release-build.sh
# into dist/bin (orqctl-v<ver>-<os>-<arch>). No GitHub Release needed: build on
# one machine, copy dist/bin to the tester, point this script at that directory.
set -eu

PREFIX="${ORQCTL_PREFIX:-${HOME}/.local}"
SHARE_DIR="${PREFIX}/share/orqctl"
BIN_DIR="${PREFIX}/bin"

case "$(uname -s)" in
  Linux*)  os=linux ;;
  Darwin*) os=darwin ;;
  *)       echo "unsupported OS: $(uname -s) (use install.ps1 on Windows)" >&2; exit 1 ;;
esac

case "$(uname -m)" in
  x86_64|amd64)  arch=x64 ;;
  arm64|aarch64) arch=arm64 ;;
  *)             echo "unsupported arch: $(uname -m)" >&2; exit 1 ;;
esac

# Accept an optional directory path as the first argument.
# Default to the cli/dist/bin directory if not provided.
ARTIFACT_DIR="${1:-$(cd "$(dirname "$0")/../dist/bin" 2>/dev/null && pwd || true)}"
BINARY="$(ls "${ARTIFACT_DIR}"/orqctl-v*-${os}-${arch} 2>/dev/null | sort -V | tail -1)"

if [ -z "$BINARY" ]; then
  echo "no binary found for ${os}-${arch} in ${ARTIFACT_DIR:-<unset>}" >&2
  echo "run: pnpm build:bin" >&2
  exit 1
fi

echo "installing from $(basename "$BINARY") ..."
rm -rf "$SHARE_DIR"
mkdir -p "${SHARE_DIR}/bin" "$BIN_DIR"
cp "$BINARY" "${SHARE_DIR}/bin/orqctl"
chmod +x "${SHARE_DIR}/bin/orqctl"
ln -sf "${SHARE_DIR}/bin/orqctl" "${BIN_DIR}/orqctl"
echo "installed: ${BIN_DIR}/orqctl"

case ":${PATH}:" in
  *":${BIN_DIR}:"*) ;;
  *) echo "note: add ${BIN_DIR} to your PATH" ;;
esac
