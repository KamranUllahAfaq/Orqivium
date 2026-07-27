#!/bin/sh
# install-cli.sh — one-line orqctl installer. orqctl ships as assets on Orqivium
# GitHub Releases; this installs the build matching your Orqivium version.
#
# usage:
#   curl -fsSL https://raw.githubusercontent.com/kamranullahafaq/orqivium/main/cli/scripts/install-cli.sh | sh
#
# env:
#   ORQIVIUM_VERSION     Orqivium release tag to install orqctl from (e.g. 1.14.2). Primary key.
#   ORQCTL_VERSION  orqctl version pin (used only when ORQIVIUM_VERSION is unset).
#   ORQCTL_PREFIX   install dir (default $HOME/.local); binary -> $PREFIX/bin/orqctl
#   ORQCTL_REPO     release source repo (default kamranullahafaq/orqivium)
#   GITHUB_TOKEN     GitHub token (or GH_TOKEN) to raise the API rate limit to 5000/hour.
# requires: curl, uname, sort -V, and sha256sum or shasum.
set -eu

REPO="${ORQCTL_REPO:-kamranullahafaq/orqivium}"
PREFIX="${ORQCTL_PREFIX:-${HOME}/.local}"
ORQIVIUM_VERSION="${ORQIVIUM_VERSION:-}"
ORQCTL_VERSION="${ORQCTL_VERSION:-}"
GH_AUTH="${GITHUB_TOKEN:-${GH_TOKEN:-}}"
# fetch_json runs in a subshell, so it reports failures via this file, not a variable.
FETCH_ERR_FILE="${TMPDIR:-/tmp}/orqctl-fetcherr.$$"
API="https://api.github.com/repos/${REPO}"
DL="https://github.com/${REPO}/releases/download"

err() { printf '%s\n' "install-cli: $*" >&2; }
die() { err "$*"; rm -f "$FETCH_ERR_FILE"; exit 1; }
need() { command -v "$1" >/dev/null 2>&1 || die "$1 is required"; }
re_escape() { printf '%s' "$1" | sed 's/[][\\.^$*+?(){}|/]/\\&/g'; }

detect_target() {
    case "$(uname -s)" in
        Linux*)  _os=linux ;;
        Darwin*) _os=darwin ;;
        *)       die "unsupported OS: $(uname -s) (use install.ps1 on Windows)" ;;
    esac
    case "$(uname -m)" in
        x86_64|amd64)  _arch=x64 ;;
        arm64|aarch64) _arch=arm64 ;;
        *)             die "unsupported arch: $(uname -m)" ;;
    esac
    printf '%s-%s' "$_os" "$_arch"
}

# list_asset_names  (reads release JSON on stdin) -> one orqctl asset name per line
list_asset_names() {
    grep -oE '"name"[[:space:]]*:[[:space:]]*"orqctl-v[^"]*"' \
        | sed -E 's#.*"name"[[:space:]]*:[[:space:]]*"([^"]*)".*#\1#'
}

# pick_asset TARGET  (reads release JSON on stdin) -> highest-semver matching asset name
pick_asset() {
    _target=$(re_escape "$1")
    list_asset_names \
        | grep -E -- "-${_target}(\\.exe)?\$" \
        | grep -vE -- '-checksums\.txt$' \
        | sort -V | tail -1
}

# asset_version ASSET_NAME TARGET -> orqctl version embedded in the name
asset_version() {
    _target=$(re_escape "$2")
    printf '%s' "$1" | sed -E "s#^orqctl-v(.*)-${_target}(\\.exe)?\$#\\1#"
}

# list_release_tags  (reads /releases array JSON on stdin) -> tag per line, newest first
list_release_tags() {
    grep -oE '"tag_name"[[:space:]]*:[[:space:]]*"[^"]*"' \
        | sed -E 's#.*:[[:space:]]*"([^"]*)".*#\1#'
}

# fetch_json URL -> body on stdout, 0 on success. On failure writes the cause to
# FETCH_ERR_FILE (ratelimit:<epoch> | http:<code> | network) and returns nonzero.
# Inspects the status and rate-limit headers, so it must not use curl -f.
fetch_json() {
    rm -f "$FETCH_ERR_FILE"
    _hdr=$(mktemp) || return 1
    _body=$(mktemp) || { rm -f "$_hdr"; return 1; }
    if [ -n "$GH_AUTH" ]; then
        _code=$(curl -sSL -D "$_hdr" -o "$_body" -w '%{http_code}' \
            -H "Accept: application/vnd.github+json" \
            -H "Authorization: Bearer ${GH_AUTH}" \
            "$1" 2>/dev/null) || _code=000
    else
        _code=$(curl -sSL -D "$_hdr" -o "$_body" -w '%{http_code}' \
            -H "Accept: application/vnd.github+json" \
            "$1" 2>/dev/null) || _code=000
    fi
    case "$_code" in
        2*) cat "$_body"; rm -f "$_hdr" "$_body"; return 0 ;;
        403|429)
            _rem=$(awk 'tolower($1)=="x-ratelimit-remaining:"{gsub(/\r/,"",$2);v=$2} END{print v}' "$_hdr")
            if [ "$_code" = "429" ] || [ "${_rem:-}" = "0" ]; then
                _rst=$(awk 'tolower($1)=="x-ratelimit-reset:"{gsub(/\r/,"",$2);v=$2} END{print v}' "$_hdr")
                printf 'ratelimit:%s' "$_rst" > "$FETCH_ERR_FILE"
            else
                printf 'http:%s' "$_code" > "$FETCH_ERR_FILE"
            fi ;;
        000) printf 'network' > "$FETCH_ERR_FILE" ;;
        *)   printf 'http:%s' "$_code" > "$FETCH_ERR_FILE" ;;
    esac
    rm -f "$_hdr" "$_body"
    return 1
}

# rate_limit_hint [RESET_EPOCH] -> explain the GitHub API limit and how to proceed.
rate_limit_hint() {
    err "GitHub API rate limit exceeded (unauthenticated requests are capped at 60/hour per IP)."
    case "${1:-}" in
        '' | *[!0-9]*) ;;
        *)
            _now=$(date +%s 2>/dev/null) || _now=""
            if [ -n "$_now" ]; then
                _mins=$(( ($1 - _now + 59) / 60 ))
                if [ "$_mins" -gt 0 ]; then
                    err "The limit resets in ~${_mins} min."
                fi
            fi ;;
    esac
    err "To proceed now, authenticate to raise the limit to 5000/hour:"
    err "  curl -fsSL <install-url> | GITHUB_TOKEN=<token> sh"
    err "Tip: pinning ORQIVIUM_VERSION makes a single API call (ORQCTL_VERSION scans many)."
}

# True if the last fetch_json hit a rate limit — lets a subshell bail without printing.
fetch_hit_ratelimit() {
    [ -f "$FETCH_ERR_FILE" ] || return 1
    case "$(cat "$FETCH_ERR_FILE" 2>/dev/null || true)" in
        ratelimit:*) return 0 ;;
    esac
    return 1
}

# Explain and exit if the last fetch_json hit a rate limit; else return. Main shell only.
maybe_ratelimit_exit() {
    fetch_hit_ratelimit || return 0
    _reset=$(cat "$FETCH_ERR_FILE" 2>/dev/null || true)
    rm -f "$FETCH_ERR_FILE"
    rate_limit_hint "${_reset#ratelimit:}"
    exit 1
}

# find_release_for_orqctl WANT TARGET -> newest Orqivium tag whose assets host that orqctl build
find_release_for_orqctl() {
    _want="$1"
    _target="$2"
    _raw=$(fetch_json "${API}/releases?per_page=100") \
        || { fetch_hit_ratelimit && return 1; die "failed to query ${REPO} releases (network error or GitHub API rate limit)"; }
    _tags=$(printf '%s' "$_raw" | list_release_tags)
    for _t in $_tags; do
        _rel=$(fetch_json "${API}/releases/tags/${_t}") \
            || { fetch_hit_ratelimit && return 1; err "fetch failed for ${_t}, skipping"; continue; }
        _name=$(printf '%s' "$_rel" | pick_asset "$_target")
        [ -n "$_name" ] || continue
        if [ "$(asset_version "$_name" "$_target")" = "$_want" ]; then
            printf '%s' "$_t"
            return 0
        fi
    done
    return 1
}

resolve_release() {
    _target="$1"
    if [ -n "$ORQIVIUM_VERSION" ]; then
        REL=$(fetch_json "${API}/releases/tags/${ORQIVIUM_VERSION}") \
            || { maybe_ratelimit_exit; die "Orqivium release ${ORQIVIUM_VERSION} not found"; }
        ORQIVIUM_TAG="$ORQIVIUM_VERSION"
    elif [ -n "$ORQCTL_VERSION" ]; then
        ORQIVIUM_TAG=$(find_release_for_orqctl "$ORQCTL_VERSION" "$_target") \
            || { maybe_ratelimit_exit; die "orqctl ${ORQCTL_VERSION} not found on any Orqivium release"; }
        REL=$(fetch_json "${API}/releases/tags/${ORQIVIUM_TAG}") \
            || { maybe_ratelimit_exit; die "failed to fetch Orqivium release ${ORQIVIUM_TAG}"; }
    else
        REL=$(fetch_json "${API}/releases/latest") \
            || { maybe_ratelimit_exit; die "failed to query latest Orqivium release (set ORQIVIUM_VERSION to pin one)"; }
        ORQIVIUM_TAG=$(printf '%s' "$REL" | list_release_tags | head -1)
        [ -n "$ORQIVIUM_TAG" ] || die "could not parse a tag from the latest Orqivium release"
    fi
}

main() {
    trap 'rm -f "$FETCH_ERR_FILE"' EXIT INT TERM
    need curl
    need uname
    sort -V /dev/null >/dev/null 2>&1 || die "sort with -V support is required (install coreutils)"
    if command -v sha256sum >/dev/null 2>&1; then
        HASH="sha256sum"
    elif command -v shasum >/dev/null 2>&1; then
        HASH="shasum -a 256"
    else
        die "need sha256sum or shasum"
    fi

    target=$(detect_target)
    resolve_release "$target"

    asset=$(printf '%s' "$REL" | pick_asset "$target")
    [ -n "$asset" ] || die "no orqctl published for Orqivium ${ORQIVIUM_TAG} (target ${target}); set ORQIVIUM_VERSION to a release that has one"
    version=$(asset_version "$asset" "$target")
    checksums="orqctl-v${version}-checksums.txt"
    base="${DL}/${ORQIVIUM_TAG}"

    tmp=$(mktemp -d 2>/dev/null || mktemp -d -t orqctl-install)
    trap 'rm -rf "$tmp"; rm -f "$FETCH_ERR_FILE"' EXIT INT TERM

    printf 'downloading %s (Orqivium %s)...\n' "$asset" "$ORQIVIUM_TAG"
    curl -fsSL "${base}/${asset}" -o "${tmp}/${asset}" \
        || die "download failed: ${base}/${asset}"
    curl -fsSL "${base}/${checksums}" -o "${tmp}/${checksums}" \
        || die "checksum manifest download failed: ${base}/${checksums}"

    _pattern=$(re_escape "$asset")
    _sumline=$(grep -E -- "[[:space:]]${_pattern}\$" "${tmp}/${checksums}") || true
    [ -n "$_sumline" ] || die "no checksum entry for ${asset}"
    (
        cd "$tmp"
        printf '%s\n' "$_sumline" | $HASH -c -
    ) || die "checksum mismatch for ${asset}"

    bin_dir="${PREFIX}/bin"
    mkdir -p "$bin_dir"
    target_bin="${bin_dir}/orqctl"
    cp "${tmp}/${asset}" "$target_bin"
    chmod +x "$target_bin"

    printf '\norqctl v%s installed (from Orqivium %s): %s\n' "$version" "$ORQIVIUM_TAG" "$target_bin"

    case ":${PATH}:" in
        *":${bin_dir}:"*)
            "$target_bin" version >/dev/null 2>&1 \
                && printf 'verify: run "orqctl version"\n' \
                || err "binary present but failed to execute; check ${target_bin}"
            ;;
        *)
            printf '\n%s is not on your PATH. Add this to your shell profile:\n' "$bin_dir"
            printf '  export PATH="%s:$PATH"\n' "$bin_dir"
            ;;
    esac
}

if [ "${ORQCTL_INSTALL_LIB:-0}" != "1" ]; then
    main "$@"
fi
