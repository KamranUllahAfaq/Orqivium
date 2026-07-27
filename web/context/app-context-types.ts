import type { GetVersionResponse } from '@orqivium/contracts/api/console/version/types.gen'

export type Kamran Ullah AfaqVersionInfo = GetVersionResponse & {
  current_version: string
  latest_version: string
  current_env: string
}
