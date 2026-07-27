import type { SemVer } from 'std-semver'
import { compare, tryParse } from 'std-semver'

export type OrqiviumCompat = {
  readonly minOrqivium: string
  readonly maxOrqivium: string
}

export const orqiviumCompat: OrqiviumCompat = {
  minOrqivium: __ORQCTL_MIN_ORQIVIUM__,
  maxOrqivium: __ORQCTL_MAX_ORQIVIUM__,
}

export function compatString(): string {
  return `orqivium >=${orqiviumCompat.minOrqivium}, <=${orqiviumCompat.maxOrqivium}`
}

export type CompatStatus = 'compatible' | 'too_old' | 'too_new' | 'unknown'

export type CompatVerdict = {
  readonly status: CompatStatus
  readonly detail: string
}

const DETAIL_MAX_LEN = 80

function clamp(s: string): string {
  return s.length > DETAIL_MAX_LEN ? `${s.slice(0, DETAIL_MAX_LEN)}…` : s
}

// Numeric core (major.minor.patch) with pre-release/build stripped, so ordering
// ignores channel suffixes: a 0.2.0-rc.1 build compares equal to the 0.2.0 floor.
function core(v: SemVer): SemVer {
  return { major: v.major, minor: v.minor, patch: v.patch, prerelease: [], build: [] }
}

export function evaluateCompat(
  serverVersion: string | undefined,
  range: OrqiviumCompat = orqiviumCompat,
): CompatVerdict {
  if (serverVersion === undefined || serverVersion === '')
    return { status: 'unknown', detail: 'server version unknown' }

  const server = tryParse(serverVersion)
  if (server === undefined)
    return {
      status: 'unknown',
      detail: `server version ${JSON.stringify(clamp(serverVersion))} is not valid semver`,
    }

  const min = tryParse(range.minOrqivium)
  const max = tryParse(range.maxOrqivium)
  if (min === undefined || max === undefined)
    return {
      status: 'unknown',
      detail: `compat range ${JSON.stringify(`>=${range.minOrqivium} <=${range.maxOrqivium}`)} is not valid semver`,
    }

  if (compare(core(server), core(min)) < 0)
    return {
      status: 'too_old',
      detail: `server ${serverVersion} is older than the minimum ${range.minOrqivium}`,
    }

  if (compare(core(server), core(max)) > 0)
    return {
      status: 'too_new',
      detail: `server ${serverVersion} is newer than the tested maximum ${range.maxOrqivium}`,
    }

  return {
    status: 'compatible',
    detail: `server ${serverVersion} in [${range.minOrqivium}, ${range.maxOrqivium}]`,
  }
}
