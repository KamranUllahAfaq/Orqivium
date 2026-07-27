import type { ToolProviderType } from '@orqivium/contracts/api/console/workspaces/types.gen'
import { zToolProviderType } from '@orqivium/contracts/api/console/workspaces/zod.gen'

export const parseToolProviderType = (providerType: unknown): ToolProviderType =>
  zToolProviderType.parse(providerType)
