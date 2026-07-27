import { getLLMModelIssue, isLLMModelProviderInstalled, LLMModelIssueCode } from '../utils'

describe('llm utils', () => {
  describe('getLLMModelIssue', () => {
    it('returns provider-required when the model provider is missing', () => {
      expect(getLLMModelIssue({ modelProvider: undefined })).toBe(
        LLMModelIssueCode.providerRequired,
      )
    })

    it('returns provider-plugin-unavailable when the provider plugin is not installed', () => {
      expect(
        getLLMModelIssue({
          modelProvider: 'orqivium/openai/gpt-4.1',
          isModelProviderInstalled: false,
        }),
      ).toBe(LLMModelIssueCode.providerPluginUnavailable)
    })

    it('returns null when the provider is present and installed', () => {
      expect(
        getLLMModelIssue({
          modelProvider: 'orqivium/openai/gpt-4.1',
          isModelProviderInstalled: true,
        }),
      ).toBeNull()
    })
  })

  describe('isLLMModelProviderInstalled', () => {
    it('returns true when the model provider is missing', () => {
      expect(isLLMModelProviderInstalled(undefined, new Set())).toBe(true)
    })

    it('matches installed plugin ids using the provider plugin prefix', () => {
      expect(
        isLLMModelProviderInstalled('orqivium/openai/gpt-4.1', new Set(['orqivium/openai'])),
      ).toBe(true)
    })

    it('returns false when the provider plugin id is not installed', () => {
      expect(
        isLLMModelProviderInstalled('orqivium/openai/gpt-4.1', new Set(['orqivium/anthropic'])),
      ).toBe(false)
    })
  })
})
