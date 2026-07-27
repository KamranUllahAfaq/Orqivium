#!/bin/sh
# uninstall-local.sh — remove a locally installed orqctl.
# Run via: pnpm uninstall:local
set -eu

PREFIX="${ORQCTL_PREFIX:-${HOME}/.local}"
SHARE_DIR="${PREFIX}/share/orqctl"
BIN_LINK="${PREFIX}/bin/orqctl"

rm -rf "$SHARE_DIR"
rm -f  "$BIN_LINK"
echo "removed ${SHARE_DIR} and ${BIN_LINK}"
