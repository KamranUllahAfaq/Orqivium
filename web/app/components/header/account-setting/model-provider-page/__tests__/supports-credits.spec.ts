import type { ModelProvider } from '../declarations'
import { CurrentSystemQuotaTypeEnum } from '../declarations'
import { providerSupportsCredits } from '../supports-credits'

const makeProvider = (overrides: Partial<ModelProvider> = {}): ModelProvider =>
  ({
    provider: 'orqivium/openai/openai',
    system_configuration: {
      enabled: true,
      current_quota_type: CurrentSystemQuotaTypeEnum.trial,
      quota_configurations: [],
    },
    ...overrides,
  }) as ModelProvider

describe('providerSupportsCredits', () => {
  it('returns true when the provider is system-enabled and listed in trial_models', () => {
    expect(providerSupportsCredits(makeProvider(), ['orqivium/openai/openai'], 'CLOUD')).toBe(
      true,
    )
  })

  it('returns false when the provider is not listed in trial_models', () => {
    expect(
      providerSupportsCredits(makeProvider(), ['orqivium/anthropic/anthropic'], 'CLOUD'),
    ).toBe(false)
  })

  it('returns false when system hosting is disabled', () => {
    expect(
      providerSupportsCredits(
        makeProvider({
          system_configuration: {
            enabled: false,
            current_quota_type: CurrentSystemQuotaTypeEnum.trial,
            quota_configurations: [],
          },
        }),
        ['orqivium/openai/openai'],
        'CLOUD',
      ),
    ).toBe(false)
  })

  it('returns false for an undefined provider', () => {
    expect(providerSupportsCredits(undefined, ['orqivium/openai/openai'], 'CLOUD')).toBe(false)
  })

  it.each(['COMMUNITY', 'ENTERPRISE'] as const)(
    'returns false outside Cloud when deployment edition is %s',
    (deploymentEdition) => {
      expect(
        providerSupportsCredits(makeProvider(), ['orqivium/openai/openai'], deploymentEdition),
      ).toBe(false)
    },
  )
})
