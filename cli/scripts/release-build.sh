#!/usr/bin/env bash
# scripts/release-build.sh — cross-compile orqctl to standalone binaries
# for every release target via `bun build --compile`.
#
# Bun consumes bin/run.ts (which imports from src/) directly — no `pnpm build`
# / dist/ step needed.
#
# Prereqs:
#   - All @napi-rs/keyring native variants present in node_modules. Append
#     cli/scripts/cross-arch.pnpm.yaml onto pnpm-workspace.yaml before the
#     install that first populates node_modules so pnpm fetches every
#     foreign-arch prebuild (the CLI Release workflow does this).
#
# Env (all optional; defaults derived from cli/package.json + git):
#   CLI_VERSION        — package.json `version`
#   ORQCTL_CHANNEL    — package.json `orqctl.channel`
#   ORQCTL_MIN_ORQIVIUM   — package.json `orqctl.compat.minOrqivium`
#   ORQCTL_MAX_ORQIVIUM   — package.json `orqctl.compat.maxOrqivium`
#   ORQCTL_COMMIT     — `git rev-parse HEAD` (or "unknown")
#   ORQCTL_BUILD_DATE — current UTC time
#
# Output: dist/bin/orqctl-v<CLI_VERSION>-<target>[.exe]

set -euo pipefail

_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/common.sh
source "${_dir}/lib/common.sh"

require bun

cli_root="$(cli::root)"
entry="${cli_root}/bin/run.ts"
out_dir="${cli_root}/dist/bin"

read_pkg() { node -p "require('${cli_root}/package.json').$1" 2>/dev/null; }
naming() { node "${_dir}/release-naming.mjs" "$@"; }

CLI_VERSION="${CLI_VERSION:-$(read_pkg version)}"
ORQCTL_CHANNEL="${ORQCTL_CHANNEL:-$(read_pkg orqctl.channel)}"
ORQCTL_MIN_ORQIVIUM="${ORQCTL_MIN_ORQIVIUM:-$(read_pkg orqctl.compat.minOrqivium)}"
ORQCTL_MAX_ORQIVIUM="${ORQCTL_MAX_ORQIVIUM:-$(read_pkg orqctl.compat.maxOrqivium)}"
ORQCTL_COMMIT="${ORQCTL_COMMIT:-$(git -C "$cli_root" rev-parse HEAD 2>/dev/null || echo unknown)}"
ORQCTL_BUILD_DATE="${ORQCTL_BUILD_DATE:-$(date -u +%Y-%m-%dT%H:%M:%SZ)}"

[[ "$CLI_VERSION" != "undefined" ]] || die "CLI_VERSION could not be derived from package.json"

[[ -f "$entry" ]] || die "entry not found: $entry"

rm -rf "$out_dir"
mkdir -p "$out_dir"

# Build-info globals (referenced as bare identifiers in src/version/info.ts).
# Each value must be a JS expression — wrap strings as JSON-quoted strings.
defines=(
    "--define" "__ORQCTL_VERSION__=\"${CLI_VERSION}\""
    "--define" "__ORQCTL_CHANNEL__=\"${ORQCTL_CHANNEL}\""
    "--define" "__ORQCTL_MIN_ORQIVIUM__=\"${ORQCTL_MIN_ORQIVIUM}\""
    "--define" "__ORQCTL_MAX_ORQIVIUM__=\"${ORQCTL_MAX_ORQIVIUM}\""
    "--define" "__ORQCTL_COMMIT__=\"${ORQCTL_COMMIT}\""
    "--define" "__ORQCTL_BUILD_DATE__=\"${ORQCTL_BUILD_DATE}\""
)

# Targets and asset names come from cli/package.json `orqctl.release` via
# release-naming.mjs (single source of truth). Each line: bunTarget<TAB>id<TAB>exe.
while IFS=$'\t' read -r bun_target asset_target _exe; do
    out="${out_dir}/$(naming asset "$CLI_VERSION" "$asset_target")"
    log::info "compiling ${asset_target} -> $(basename "$out")..."
    bun build "$entry" \
        --target="$bun_target" \
        --compile \
        --minify \
        "${defines[@]}" \
        --outfile="$out" >/dev/null
done < <(naming targets)

log::info "built $(find "$out_dir" -type f | wc -l | tr -d ' ') binaries:"
ls -lh "$out_dir" >&2
