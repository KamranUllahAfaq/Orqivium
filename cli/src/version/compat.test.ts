import { describe, expect, it } from 'vitest'
import { compatString, orqiviumCompat, evaluateCompat } from './compat'

describe('orqiviumCompat', () => {
  it('exposes minOrqivium and maxOrqivium as readonly strings', () => {
    expect(typeof orqiviumCompat.minOrqivium).toBe('string')
    expect(typeof orqiviumCompat.maxOrqivium).toBe('string')
  })
})

describe('compatString', () => {
  it('formats as "orqivium >=min, <=max"', () => {
    expect(compatString()).toMatch(/^orqivium >=\d+\.\d+\.\d+(-[\w.]+)?, <=\d+\.\d+\.\d+(-[\w.]+)?$/)
  })
})

describe('evaluateCompat', () => {
  const range = { minOrqivium: '1.6.0', maxOrqivium: '1.7.0' }

  it('returns compatible when server version is in range', () => {
    expect(evaluateCompat('1.6.4', range)).toEqual({
      status: 'compatible',
      detail: 'server 1.6.4 in [1.6.0, 1.7.0]',
    })
  })

  it('returns compatible at the lower bound', () => {
    expect(evaluateCompat('1.6.0', range).status).toBe('compatible')
  })

  it('returns compatible at the upper bound (inclusive)', () => {
    expect(evaluateCompat('1.7.0', range).status).toBe('compatible')
  })

  it('returns too_old when server is below minimum', () => {
    const v = evaluateCompat('1.5.9', range)
    expect(v.status).toBe('too_old')
    expect(v.detail).toContain('1.5.9')
  })

  it('returns too_new when server is above maximum', () => {
    expect(evaluateCompat('2.0.0', range).status).toBe('too_new')
  })

  describe('ignores pre-release/channel suffixes (numeric-core comparison)', () => {
    it('treats a pre-release of the upper bound as compatible', () => {
      // 1.7.0-rc.1 has core 1.7.0 == maxOrqivium; a suffix-sensitive range would push
      // it out of [1.6.0, 1.7.0], but its numeric core is in range.
      expect(evaluateCompat('1.7.0-rc.1', range).status).toBe('compatible')
    })

    it('treats a pre-release of the lower bound as compatible', () => {
      expect(evaluateCompat('1.6.0-alpha', range).status).toBe('compatible')
    })

    it('still flags a pre-release whose core is below the minimum as too_old', () => {
      expect(evaluateCompat('1.5.9-rc.1', range).status).toBe('too_old')
    })

    it('still flags a pre-release whose core is above the maximum as too_new', () => {
      expect(evaluateCompat('2.0.0-alpha', range).status).toBe('too_new')
    })

    it('strips suffixes on the range bounds too', () => {
      expect(evaluateCompat('1.6.5', { minOrqivium: '1.6.0-alpha', maxOrqivium: '1.7.0-rc' }).status).toBe(
        'compatible',
      )
    })
  })

  it('returns unknown when server version is empty', () => {
    expect(evaluateCompat('', range).status).toBe('unknown')
    expect(evaluateCompat(undefined, range).status).toBe('unknown')
  })

  it('returns unknown when server version is not valid semver', () => {
    const v = evaluateCompat('totally-not-semver', range)
    expect(v.status).toBe('unknown')
    expect(v.detail).toContain('not valid semver')
  })

  it('clamps malformed server versions to 80 chars in the detail string', () => {
    const malicious = 'x'.repeat(10_000)
    const v = evaluateCompat(malicious, range)
    expect(v.status).toBe('unknown')
    // detail = `server version "<=80 chars + ellipsis>" is not valid semver`;
    // a bit of leeway for the surrounding text, but nowhere near 10k.
    expect(v.detail.length).toBeLessThan(150)
    expect(v.detail).toContain('…')
  })

  it('returns unknown when compat range itself is not valid semver', () => {
    const v = evaluateCompat('1.6.4', { minOrqivium: 'foo', maxOrqivium: 'bar' })
    expect(v.status).toBe('unknown')
  })

  it('uses the bundled orqiviumCompat range by default', () => {
    // Build-info range comes from package.json#orqctl.compat (or env at build
    // time); a server version equal to the lower bound must be compatible.
    expect(evaluateCompat(orqiviumCompat.minOrqivium).status).toBe('compatible')
  })
})
