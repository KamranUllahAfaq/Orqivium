import type { OrqiviumResponse } from '../types/common'
import type { WorkspaceModelType, WorkspaceModelsResponse } from '../types/workspace'
import { OrqiviumClient } from './base'
import { ensureNonEmptyString } from './validation'

export class WorkspaceClient extends OrqiviumClient {
  async getModelsByType(
    modelType: WorkspaceModelType,
  ): Promise<OrqiviumResponse<WorkspaceModelsResponse>> {
    ensureNonEmptyString(modelType, 'modelType')
    return this.http.request({
      method: 'GET',
      path: `/workspaces/current/models/model-types/${modelType}`,
    })
  }
}
