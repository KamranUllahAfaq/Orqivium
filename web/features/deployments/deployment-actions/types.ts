import type { AppInstance } from '@orqivium/contracts/enterprise/types.gen'

export type DeploymentActionAppInstance = Pick<AppInstance, 'id' | 'displayName' | 'description'>
