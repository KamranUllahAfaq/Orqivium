import { afterEach, beforeEach, describe, expect, it } from 'vitest'
import { ENV_REGISTRY, getEnv, lookupEnv, resolveEnv } from './registry'

describe('env registry', () => {
  it('contains every ORQIVIUM_* var from the v1.0 spec', () => {
    const names = ENV_REGISTRY.map((e) => e.name)
    expect(names).toContain('ORQIVIUM_TOKEN')
    expect(names).toContain('ORQIVIUM_HOST')
    expect(names).toContain('ORQIVIUM_WORKSPACE_ID')
    expect(names).toContain('ORQIVIUM_CONFIG_DIR')
    expect(names).toContain('ORQIVIUM_LIMIT')
    expect(names).toContain('ORQIVIUM_FORMAT')
    expect(names).toContain('ORQIVIUM_NO_PROGRESS')
    expect(names).toContain('ORQIVIUM_PLAIN')
  })

  it('is sorted alphabetically (matches Go init() ordering)', () => {
    const names = ENV_REGISTRY.map((e) => e.name)
    const sorted = [...names].sort()
    expect(names).toEqual(sorted)
  })

  it('marks ORQIVIUM_TOKEN as sensitive', () => {
    expect(lookupEnv('ORQIVIUM_TOKEN')?.sensitive).toBe(true)
  })

  it('does not mark non-secret vars as sensitive', () => {
    expect(lookupEnv('ORQIVIUM_HOST')?.sensitive).toBeFalsy()
    expect(lookupEnv('ORQIVIUM_LIMIT')?.sensitive).toBeFalsy()
  })

  it('lookupEnv returns undefined for unknown name', () => {
    expect(lookupEnv('ORQIVIUM_NOPE')).toBeUndefined()
  })

  it('lookupEnv finds the registry entry by name', () => {
    expect(lookupEnv('ORQIVIUM_HOST')?.description).toMatch(/host/i)
  })

  describe('process.env reads', () => {
    const originals: Record<string, string | undefined> = {}
    beforeEach(() => {
      originals.ORQIVIUM_LIMIT = process.env.ORQIVIUM_LIMIT
      originals.ORQIVIUM_HOST = process.env.ORQIVIUM_HOST
      originals.ORQIVIUM_TEST_NONEXISTENT = process.env.ORQIVIUM_TEST_NONEXISTENT
      delete process.env.ORQIVIUM_LIMIT
      delete process.env.ORQIVIUM_HOST
      delete process.env.ORQIVIUM_TEST_NONEXISTENT
    })
    afterEach(() => {
      for (const [k, v] of Object.entries(originals)) {
        if (v === undefined) delete process.env[k]
        else process.env[k] = v
      }
    })

    it('getEnv returns undefined for unset var', () => {
      expect(getEnv('ORQIVIUM_TEST_NONEXISTENT')).toBeUndefined()
    })

    it('getEnv returns the literal string for a set var', () => {
      process.env.ORQIVIUM_HOST = 'http://localhost'
      expect(getEnv('ORQIVIUM_HOST')).toBe('http://localhost')
    })

    it('resolveEnv returns parsed value for ORQIVIUM_LIMIT (uses parseLimit)', () => {
      process.env.ORQIVIUM_LIMIT = '42'
      expect(resolveEnv('ORQIVIUM_LIMIT')).toBe(42)
    })

    it('resolveEnv returns the raw string for vars with no parser', () => {
      process.env.ORQIVIUM_HOST = 'https://example.orqivium.local'
      expect(resolveEnv('ORQIVIUM_HOST')).toBe('https://example.orqivium.local')
    })

    it('resolveEnv returns undefined when var is unset and no default', () => {
      expect(resolveEnv('ORQIVIUM_HOST')).toBeUndefined()
    })

    it('resolveEnv propagates parser errors', () => {
      process.env.ORQIVIUM_LIMIT = '999'
      expect(() => resolveEnv('ORQIVIUM_LIMIT')).toThrow(/out of range/)
    })

    it('resolveEnv accepts unknown var name and returns undefined (no throw)', () => {
      expect(resolveEnv('ORQIVIUM_NOPE')).toBeUndefined()
    })
  })
})
