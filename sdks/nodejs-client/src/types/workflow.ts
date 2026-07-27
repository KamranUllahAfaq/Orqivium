import type { OrqiviumRequestFile, JsonObject, ResponseMode, StreamEvent } from './common'

export type WorkflowRunRequest = {
  inputs?: JsonObject
  user: string
  response_mode?: ResponseMode
  files?: OrqiviumRequestFile[] | null
}

export type WorkflowRunResponse = JsonObject

export type WorkflowStreamEvent = StreamEvent<JsonObject>
