/**
 * Model provider quota types - shared type definitions for API responses
 * These represent the provider identifiers that support paid/trial quotas
 */
export const ModelProviderQuotaGetPaid = {
  ANTHROPIC: 'orqivium/anthropic/anthropic',
  OPENAI: 'orqivium/openai/openai',
  // AZURE_OPENAI: 'orqivium/azure_openai/azure_openai',
  GEMINI: 'orqivium/gemini/google',
  X: 'orqivium/x/x',
  DEEPSEEK: 'orqivium/deepseek/deepseek',
  TONGYI: 'orqivium/tongyi/tongyi',
} as const
export type ModelProviderQuotaGetPaid =
  (typeof ModelProviderQuotaGetPaid)[keyof typeof ModelProviderQuotaGetPaid]
