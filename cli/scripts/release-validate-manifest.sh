#!/usr/bin/env bash
# scripts/release-validate-manifest.sh — validate cli/package.json release fields.

set -euo pipefail

_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/common.sh
source "${_dir}/lib/common.sh"

cd "$(cli::root)"

SEMVER_RE='^[0-9]+\.[0-9]+\.[0-9]+(-[0-9A-Za-z.-]+)?(\+[0-9A-Za-z.-]+)?$'

version=$(node -p "require('./package.json').version")
channel=$(node -p "require('./package.json').orqctl.channel")
min_orqivium=$(node -p "require('./package.json').orqctl.compat.minOrqivium")
max_orqivium=$(node -p "require('./package.json').orqctl.compat.maxOrqivium")

# Version form (per channel) and channel validity are enforced by
# release-naming.mjs validate below — the single source for those rules.

[[ "$min_orqivium" =~ $SEMVER_RE ]] || die "invalid orqctl.compat.minOrqivium: ${min_orqivium}"
[[ "$max_orqivium" =~ $SEMVER_RE ]] || die "invalid orqctl.compat.maxOrqivium: ${max_orqivium}"

case "$min_orqivium" in *[xX*]*) die "wildcards not allowed in minOrqivium: ${min_orqivium}" ;; esac
case "$max_orqivium" in *[xX*]*) die "wildcards not allowed in maxOrqivium: ${max_orqivium}" ;; esac

cmp=$(node -e "
const a = process.argv[1].split('-')[0].split('.').map(Number)
const b = process.argv[2].split('-')[0].split('.').map(Number)
for (let i = 0; i < 3; i++) {
    if (a[i] !== b[i]) { console.log(a[i] < b[i] ? -1 : 1); process.exit(0) }
}
console.log(0)
" "$min_orqivium" "$max_orqivium")

[[ "$cmp" -le 0 ]] || die "minOrqivium (${min_orqivium}) > maxOrqivium (${max_orqivium})"

node "${_dir}/release-naming.mjs" validate >/dev/null

log::info "manifest valid: version=${version} channel=${channel} compat=${min_orqivium}..${max_orqivium}"
