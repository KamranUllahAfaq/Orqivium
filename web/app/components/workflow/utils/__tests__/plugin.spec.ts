import { extractPluginId } from '../plugin'

describe('extractPluginId', () => {
  it('returns the provider prefix for nested plugin paths', () => {
    expect(extractPluginId('orqivium/openai/tools/chat')).toBe('orqivium/openai')
  })

  it('returns the original provider when it has no nested path', () => {
    expect(extractPluginId('orqivium')).toBe('orqivium')
  })
})
