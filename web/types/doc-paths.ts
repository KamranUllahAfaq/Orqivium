// GENERATE BY script
// DON NOT EDIT IT MANUALLY
//
// Generated from: /docs.json
// Generated at: 2026-07-09T10:55:53.618Z

// Language prefixes
export type DocLanguage = 'en' | 'zh' | 'ja'
export type DocsProduct = 'cloud' | 'self-host'

// Cloud paths
type CloudPath =
  | '/cloud/use-orqivium/build/additional-features'
  | '/cloud/use-orqivium/build/agent'
  | '/cloud/use-orqivium/build/chatbot'
  | '/cloud/use-orqivium/build/orchestrate-node'
  | '/cloud/use-orqivium/build/predefined-error-handling-logic'
  | '/cloud/use-orqivium/build/shortcut-key'
  | '/cloud/use-orqivium/build/text-generator'
  | '/cloud/use-orqivium/build/version-control'
  | '/cloud/use-orqivium/build/workflow-chatflow'
  | '/cloud/use-orqivium/debug/error-type'
  | '/cloud/use-orqivium/debug/history-and-logs'
  | '/cloud/use-orqivium/debug/step-run'
  | '/cloud/use-orqivium/debug/variable-inspect'
  | '/cloud/use-orqivium/getting-started/introduction'
  | '/cloud/use-orqivium/knowledge/connect-external-knowledge-base'
  | '/cloud/use-orqivium/knowledge/create-knowledge/chunking-and-cleaning-text'
  | '/cloud/use-orqivium/knowledge/create-knowledge/import-text-data/readme'
  | '/cloud/use-orqivium/knowledge/create-knowledge/import-text-data/sync-from-notion'
  | '/cloud/use-orqivium/knowledge/create-knowledge/import-text-data/sync-from-website'
  | '/cloud/use-orqivium/knowledge/create-knowledge/introduction'
  | '/cloud/use-orqivium/knowledge/create-knowledge/setting-indexing-methods'
  | '/cloud/use-orqivium/knowledge/external-knowledge-api'
  | '/cloud/use-orqivium/knowledge/integrate-knowledge-within-application'
  | '/cloud/use-orqivium/knowledge/knowledge-pipeline/authorize-data-source'
  | '/cloud/use-orqivium/knowledge/knowledge-pipeline/create-knowledge-pipeline'
  | '/cloud/use-orqivium/knowledge/knowledge-pipeline/knowledge-pipeline-orchestration'
  | '/cloud/use-orqivium/knowledge/knowledge-pipeline/manage-knowledge-base'
  | '/cloud/use-orqivium/knowledge/knowledge-pipeline/publish-knowledge-pipeline'
  | '/cloud/use-orqivium/knowledge/knowledge-pipeline/readme'
  | '/cloud/use-orqivium/knowledge/knowledge-pipeline/upload-files'
  | '/cloud/use-orqivium/knowledge/knowledge-request-rate-limit'
  | '/cloud/use-orqivium/knowledge/manage-knowledge/introduction'
  | '/cloud/use-orqivium/knowledge/manage-knowledge/maintain-knowledge-documents'
  | '/cloud/use-orqivium/knowledge/metadata'
  | '/cloud/use-orqivium/knowledge/readme'
  | '/cloud/use-orqivium/knowledge/test-retrieval'
  | '/cloud/use-orqivium/monitor/analysis'
  | '/cloud/use-orqivium/monitor/annotation-reply'
  | '/cloud/use-orqivium/monitor/integrations/integrate-aliyun'
  | '/cloud/use-orqivium/monitor/integrations/integrate-arize'
  | '/cloud/use-orqivium/monitor/integrations/integrate-langfuse'
  | '/cloud/use-orqivium/monitor/integrations/integrate-langsmith'
  | '/cloud/use-orqivium/monitor/integrations/integrate-opik'
  | '/cloud/use-orqivium/monitor/integrations/integrate-phoenix'
  | '/cloud/use-orqivium/monitor/integrations/integrate-weave'
  | '/cloud/use-orqivium/monitor/logs'
  | '/cloud/use-orqivium/nodes/agent'
  | '/cloud/use-orqivium/nodes/answer'
  | '/cloud/use-orqivium/nodes/code'
  | '/cloud/use-orqivium/nodes/doc-extractor'
  | '/cloud/use-orqivium/nodes/http-request'
  | '/cloud/use-orqivium/nodes/human-input'
  | '/cloud/use-orqivium/nodes/ifelse'
  | '/cloud/use-orqivium/nodes/iteration'
  | '/cloud/use-orqivium/nodes/knowledge-retrieval'
  | '/cloud/use-orqivium/nodes/list-operator'
  | '/cloud/use-orqivium/nodes/llm'
  | '/cloud/use-orqivium/nodes/loop'
  | '/cloud/use-orqivium/nodes/output'
  | '/cloud/use-orqivium/nodes/parameter-extractor'
  | '/cloud/use-orqivium/nodes/question-classifier'
  | '/cloud/use-orqivium/nodes/start'
  | '/cloud/use-orqivium/nodes/template'
  | '/cloud/use-orqivium/nodes/tools'
  | '/cloud/use-orqivium/nodes/trigger/overview'
  | '/cloud/use-orqivium/nodes/trigger/plugin-trigger'
  | '/cloud/use-orqivium/nodes/trigger/schedule-trigger'
  | '/cloud/use-orqivium/nodes/trigger/webhook-trigger'
  | '/cloud/use-orqivium/nodes/user-input'
  | '/cloud/use-orqivium/nodes/variable-aggregator'
  | '/cloud/use-orqivium/nodes/variable-assigner'
  | '/cloud/use-orqivium/publish/README'
  | '/cloud/use-orqivium/publish/publish-mcp'
  | '/cloud/use-orqivium/publish/publish-to-marketplace'
  | '/cloud/use-orqivium/publish/webapp/chatflow-webapp'
  | '/cloud/use-orqivium/publish/webapp/embedding-in-websites'
  | '/cloud/use-orqivium/publish/webapp/web-app-settings'
  | '/cloud/use-orqivium/publish/webapp/workflow-webapp'
  | '/cloud/use-orqivium/workspace/api-extension/api-extension'
  | '/cloud/use-orqivium/workspace/api-extension/cloudflare-worker'
  | '/cloud/use-orqivium/workspace/api-extension/external-data-tool-api-extension'
  | '/cloud/use-orqivium/workspace/api-extension/moderation-api-extension'
  | '/cloud/use-orqivium/workspace/app-management'
  | '/cloud/use-orqivium/workspace/model-providers'
  | '/cloud/use-orqivium/workspace/personal-account-management'
  | '/cloud/use-orqivium/workspace/plugins'
  | '/cloud/use-orqivium/workspace/readme'
  | '/cloud/use-orqivium/workspace/subscription-management'
  | '/cloud/use-orqivium/workspace/team-members-management'
  | '/cloud/use-orqivium/workspace/tools'

// UseOrqivium paths
type UseOrqiviumPath =
  | '/use-orqivium/build/additional-features'
  | '/use-orqivium/build/agent'
  | '/use-orqivium/build/chatbot'
  | '/use-orqivium/build/new-agent/build'
  | '/use-orqivium/build/new-agent/overview'
  | '/use-orqivium/build/orchestrate-node'
  | '/use-orqivium/build/predefined-error-handling-logic'
  | '/use-orqivium/build/shortcut-key'
  | '/use-orqivium/build/text-generator'
  | '/use-orqivium/build/version-control'
  | '/use-orqivium/build/workflow-chatflow'
  | '/use-orqivium/build/workflow-collaboration'
  | '/use-orqivium/debug/error-type'
  | '/use-orqivium/debug/history-and-logs'
  | '/use-orqivium/debug/step-run'
  | '/use-orqivium/debug/variable-inspect'
  | '/use-orqivium/getting-started/introduction'
  | '/use-orqivium/knowledge/connect-external-knowledge-base'
  | '/use-orqivium/knowledge/create-knowledge/chunking-and-cleaning-text'
  | '/use-orqivium/knowledge/create-knowledge/import-text-data/readme'
  | '/use-orqivium/knowledge/create-knowledge/import-text-data/sync-from-notion'
  | '/use-orqivium/knowledge/create-knowledge/import-text-data/sync-from-website'
  | '/use-orqivium/knowledge/create-knowledge/introduction'
  | '/use-orqivium/knowledge/create-knowledge/setting-indexing-methods'
  | '/use-orqivium/knowledge/external-knowledge-api'
  | '/use-orqivium/knowledge/integrate-knowledge-within-application'
  | '/use-orqivium/knowledge/knowledge-pipeline/authorize-data-source'
  | '/use-orqivium/knowledge/knowledge-pipeline/create-knowledge-pipeline'
  | '/use-orqivium/knowledge/knowledge-pipeline/knowledge-pipeline-orchestration'
  | '/use-orqivium/knowledge/knowledge-pipeline/manage-knowledge-base'
  | '/use-orqivium/knowledge/knowledge-pipeline/publish-knowledge-pipeline'
  | '/use-orqivium/knowledge/knowledge-pipeline/readme'
  | '/use-orqivium/knowledge/knowledge-pipeline/upload-files'
  | '/use-orqivium/knowledge/knowledge-request-rate-limit'
  | '/use-orqivium/knowledge/manage-knowledge/introduction'
  | '/use-orqivium/knowledge/manage-knowledge/maintain-knowledge-documents'
  | '/use-orqivium/knowledge/metadata'
  | '/use-orqivium/knowledge/readme'
  | '/use-orqivium/knowledge/test-retrieval'
  | '/use-orqivium/monitor/analysis'
  | '/use-orqivium/monitor/annotation-reply'
  | '/use-orqivium/monitor/integrations/integrate-aliyun'
  | '/use-orqivium/monitor/integrations/integrate-arize'
  | '/use-orqivium/monitor/integrations/integrate-langfuse'
  | '/use-orqivium/monitor/integrations/integrate-langsmith'
  | '/use-orqivium/monitor/integrations/integrate-opik'
  | '/use-orqivium/monitor/integrations/integrate-phoenix'
  | '/use-orqivium/monitor/integrations/integrate-weave'
  | '/use-orqivium/monitor/logs'
  | '/use-orqivium/nodes/agent'
  | '/use-orqivium/nodes/answer'
  | '/use-orqivium/nodes/code'
  | '/use-orqivium/nodes/doc-extractor'
  | '/use-orqivium/nodes/http-request'
  | '/use-orqivium/nodes/human-input'
  | '/use-orqivium/nodes/ifelse'
  | '/use-orqivium/nodes/iteration'
  | '/use-orqivium/nodes/knowledge-retrieval'
  | '/use-orqivium/nodes/list-operator'
  | '/use-orqivium/nodes/llm'
  | '/use-orqivium/nodes/loop'
  | '/use-orqivium/nodes/output'
  | '/use-orqivium/nodes/parameter-extractor'
  | '/use-orqivium/nodes/question-classifier'
  | '/use-orqivium/nodes/start'
  | '/use-orqivium/nodes/template'
  | '/use-orqivium/nodes/tools'
  | '/use-orqivium/nodes/trigger/overview'
  | '/use-orqivium/nodes/trigger/plugin-trigger'
  | '/use-orqivium/nodes/trigger/schedule-trigger'
  | '/use-orqivium/nodes/trigger/webhook-trigger'
  | '/use-orqivium/nodes/user-input'
  | '/use-orqivium/nodes/variable-aggregator'
  | '/use-orqivium/nodes/variable-assigner'
  | '/use-orqivium/publish/README'
  | '/use-orqivium/publish/publish-mcp'
  | '/use-orqivium/publish/publish-to-marketplace'
  | '/use-orqivium/publish/webapp/chatflow-webapp'
  | '/use-orqivium/publish/webapp/embedding-in-websites'
  | '/use-orqivium/publish/webapp/web-app-settings'
  | '/use-orqivium/publish/webapp/workflow-webapp'
  | '/use-orqivium/workspace/api-extension/api-extension'
  | '/use-orqivium/workspace/api-extension/cloudflare-worker'
  | '/use-orqivium/workspace/api-extension/external-data-tool-api-extension'
  | '/use-orqivium/workspace/api-extension/moderation-api-extension'
  | '/use-orqivium/workspace/app-management'
  | '/use-orqivium/workspace/model-providers'
  | '/use-orqivium/workspace/personal-account-management'
  | '/use-orqivium/workspace/plugins'
  | '/use-orqivium/workspace/readme'
  | '/use-orqivium/workspace/subscription-management'
  | '/use-orqivium/workspace/team-members-management'
  | '/use-orqivium/workspace/tools'

// UseOrqivium node paths (without prefix)
type ExtractNodesPath<T> = T extends `/use-orqivium/nodes/${infer Path}` ? Path : never
export type UseOrqiviumNodesPath = ExtractNodesPath<UseOrqiviumPath>

// Home paths
type HomePath = '/home'

// Learn paths
type LearnPath =
  | '/learn/key-concepts'
  | '/learn/tutorials/article-reader'
  | '/learn/tutorials/build-ai-image-generation-app'
  | '/learn/tutorials/customer-service-bot'
  | '/learn/tutorials/simple-chatbot'
  | '/learn/tutorials/twitter-chatflow'
  | '/learn/tutorials/workflow-101/lesson-01'
  | '/learn/tutorials/workflow-101/lesson-02'
  | '/learn/tutorials/workflow-101/lesson-03'
  | '/learn/tutorials/workflow-101/lesson-04'
  | '/learn/tutorials/workflow-101/lesson-05'
  | '/learn/tutorials/workflow-101/lesson-06'
  | '/learn/tutorials/workflow-101/lesson-07'
  | '/learn/tutorials/workflow-101/lesson-08'
  | '/learn/tutorials/workflow-101/lesson-09'
  | '/learn/tutorials/workflow-101/lesson-10'

// QuickStart paths
type QuickStartPath = '/quick-start'

// ApiReference paths
type ApiReferencePath =
  | '/api-reference/guides/agent'
  | '/api-reference/guides/chat'
  | '/api-reference/guides/chatflow'
  | '/api-reference/guides/completion'
  | '/api-reference/guides/end-user-identity'
  | '/api-reference/guides/errors'
  | '/api-reference/guides/get-started'
  | '/api-reference/guides/human-input-flow'
  | '/api-reference/guides/knowledge'
  | '/api-reference/guides/streaming'
  | '/api-reference/guides/workflow'

// Cli paths
type CliPath =
  | '/cli/authenticate'
  | '/cli/common-tasks'
  | '/cli/install'
  | '/cli/integrate-agents/auth-for-agent-deployments'
  | '/cli/integrate-agents/error-handling-and-retries-for-agents'
  | '/cli/integrate-agents/install-the-orqctl-skill'
  | '/cli/integrate-agents/overview'
  | '/cli/overview'
  | '/cli/quick-start'
  | '/cli/reference/apps'
  | '/cli/reference/auth-and-contexts'
  | '/cli/reference/command-index'
  | '/cli/reference/environment-variables'
  | '/cli/reference/global-flags'
  | '/cli/reference/help'
  | '/cli/reference/output-formats-and-exit-codes'
  | '/cli/reference/skills'
  | '/cli/reference/version'
  | '/cli/reference/workspaces'
  | '/cli/troubleshooting'

// DevelopPlugin paths
type DevelopPluginPath =
  | '/develop-plugin/dev-guides-and-walkthroughs/agent-strategy-plugin'
  | '/develop-plugin/dev-guides-and-walkthroughs/cheatsheet'
  | '/develop-plugin/dev-guides-and-walkthroughs/creating-new-model-provider'
  | '/develop-plugin/dev-guides-and-walkthroughs/datasource-plugin'
  | '/develop-plugin/dev-guides-and-walkthroughs/develop-a-slack-bot-plugin'
  | '/develop-plugin/dev-guides-and-walkthroughs/develop-flomo-plugin'
  | '/develop-plugin/dev-guides-and-walkthroughs/develop-md-exporter'
  | '/develop-plugin/dev-guides-and-walkthroughs/develop-multimodal-data-processing-tool'
  | '/develop-plugin/dev-guides-and-walkthroughs/endpoint'
  | '/develop-plugin/dev-guides-and-walkthroughs/tool-oauth'
  | '/develop-plugin/dev-guides-and-walkthroughs/tool-plugin'
  | '/develop-plugin/dev-guides-and-walkthroughs/trigger-plugin'
  | '/develop-plugin/features-and-specs/advanced-development/bundle'
  | '/develop-plugin/features-and-specs/advanced-development/customizable-model'
  | '/develop-plugin/features-and-specs/advanced-development/reverse-invocation'
  | '/develop-plugin/features-and-specs/advanced-development/reverse-invocation-app'
  | '/develop-plugin/features-and-specs/advanced-development/reverse-invocation-model'
  | '/develop-plugin/features-and-specs/advanced-development/reverse-invocation-node'
  | '/develop-plugin/features-and-specs/advanced-development/reverse-invocation-tool'
  | '/develop-plugin/features-and-specs/plugin-types/general-specifications'
  | '/develop-plugin/features-and-specs/plugin-types/model-designing-rules'
  | '/develop-plugin/features-and-specs/plugin-types/model-schema'
  | '/develop-plugin/features-and-specs/plugin-types/multilingual-readme'
  | '/develop-plugin/features-and-specs/plugin-types/persistent-storage-kv'
  | '/develop-plugin/features-and-specs/plugin-types/plugin-info-by-manifest'
  | '/develop-plugin/features-and-specs/plugin-types/plugin-logging'
  | '/develop-plugin/features-and-specs/plugin-types/remote-debug-a-plugin'
  | '/develop-plugin/features-and-specs/plugin-types/tool'
  | '/develop-plugin/getting-started/choose-plugin-type'
  | '/develop-plugin/getting-started/cli'
  | '/develop-plugin/getting-started/getting-started-orqivium-plugin'
  | '/develop-plugin/publishing/faq/faq'
  | '/develop-plugin/publishing/marketplace-listing/plugin-auto-publish-pr'
  | '/develop-plugin/publishing/marketplace-listing/release-by-file'
  | '/develop-plugin/publishing/marketplace-listing/release-overview'
  | '/develop-plugin/publishing/marketplace-listing/release-to-orqivium-marketplace'
  | '/develop-plugin/publishing/marketplace-listing/release-to-individual-github-repo'
  | '/develop-plugin/publishing/standards/contributor-covenant-code-of-conduct'
  | '/develop-plugin/publishing/standards/privacy-protection-guidelines'
  | '/develop-plugin/publishing/standards/third-party-signature-verification'

// SelfHost paths
type SelfHostPath =
  | '/self-host/deploy/advanced-deployments/local-source-code'
  | '/self-host/deploy/advanced-deployments/start-the-frontend-docker-container'
  | '/self-host/deploy/configuration/environments'
  | '/self-host/deploy/overview'
  | '/self-host/deploy/platform-guides/bt-panel'
  | '/self-host/deploy/platform-guides/orqivium-premium'
  | '/self-host/deploy/quick-start/docker-compose'
  | '/self-host/deploy/quick-start/faqs'
  | '/self-host/deploy/troubleshooting/common-issues'
  | '/self-host/deploy/troubleshooting/docker-issues'
  | '/self-host/deploy/troubleshooting/integrations'
  | '/self-host/deploy/troubleshooting/storage-and-migration'
  | '/self-host/deploy/troubleshooting/weaviate-v4-migration'
  | '/self-host/use-orqivium/build/additional-features'
  | '/self-host/use-orqivium/build/agent'
  | '/self-host/use-orqivium/build/chatbot'
  | '/self-host/use-orqivium/build/new-agent/build'
  | '/self-host/use-orqivium/build/new-agent/overview'
  | '/self-host/use-orqivium/build/orchestrate-node'
  | '/self-host/use-orqivium/build/predefined-error-handling-logic'
  | '/self-host/use-orqivium/build/shortcut-key'
  | '/self-host/use-orqivium/build/text-generator'
  | '/self-host/use-orqivium/build/version-control'
  | '/self-host/use-orqivium/build/workflow-chatflow'
  | '/self-host/use-orqivium/build/workflow-collaboration'
  | '/self-host/use-orqivium/debug/error-type'
  | '/self-host/use-orqivium/debug/history-and-logs'
  | '/self-host/use-orqivium/debug/step-run'
  | '/self-host/use-orqivium/debug/variable-inspect'
  | '/self-host/use-orqivium/getting-started/introduction'
  | '/self-host/use-orqivium/knowledge/connect-external-knowledge-base'
  | '/self-host/use-orqivium/knowledge/create-knowledge/chunking-and-cleaning-text'
  | '/self-host/use-orqivium/knowledge/create-knowledge/import-text-data/readme'
  | '/self-host/use-orqivium/knowledge/create-knowledge/import-text-data/sync-from-notion'
  | '/self-host/use-orqivium/knowledge/create-knowledge/import-text-data/sync-from-website'
  | '/self-host/use-orqivium/knowledge/create-knowledge/introduction'
  | '/self-host/use-orqivium/knowledge/create-knowledge/setting-indexing-methods'
  | '/self-host/use-orqivium/knowledge/external-knowledge-api'
  | '/self-host/use-orqivium/knowledge/integrate-knowledge-within-application'
  | '/self-host/use-orqivium/knowledge/knowledge-pipeline/authorize-data-source'
  | '/self-host/use-orqivium/knowledge/knowledge-pipeline/create-knowledge-pipeline'
  | '/self-host/use-orqivium/knowledge/knowledge-pipeline/knowledge-pipeline-orchestration'
  | '/self-host/use-orqivium/knowledge/knowledge-pipeline/manage-knowledge-base'
  | '/self-host/use-orqivium/knowledge/knowledge-pipeline/publish-knowledge-pipeline'
  | '/self-host/use-orqivium/knowledge/knowledge-pipeline/readme'
  | '/self-host/use-orqivium/knowledge/knowledge-pipeline/upload-files'
  | '/self-host/use-orqivium/knowledge/manage-knowledge/introduction'
  | '/self-host/use-orqivium/knowledge/manage-knowledge/maintain-knowledge-documents'
  | '/self-host/use-orqivium/knowledge/metadata'
  | '/self-host/use-orqivium/knowledge/readme'
  | '/self-host/use-orqivium/knowledge/test-retrieval'
  | '/self-host/use-orqivium/monitor/analysis'
  | '/self-host/use-orqivium/monitor/annotation-reply'
  | '/self-host/use-orqivium/monitor/integrations/integrate-aliyun'
  | '/self-host/use-orqivium/monitor/integrations/integrate-arize'
  | '/self-host/use-orqivium/monitor/integrations/integrate-langfuse'
  | '/self-host/use-orqivium/monitor/integrations/integrate-langsmith'
  | '/self-host/use-orqivium/monitor/integrations/integrate-opik'
  | '/self-host/use-orqivium/monitor/integrations/integrate-phoenix'
  | '/self-host/use-orqivium/monitor/integrations/integrate-weave'
  | '/self-host/use-orqivium/monitor/logs'
  | '/self-host/use-orqivium/nodes/agent'
  | '/self-host/use-orqivium/nodes/answer'
  | '/self-host/use-orqivium/nodes/code'
  | '/self-host/use-orqivium/nodes/doc-extractor'
  | '/self-host/use-orqivium/nodes/http-request'
  | '/self-host/use-orqivium/nodes/human-input'
  | '/self-host/use-orqivium/nodes/ifelse'
  | '/self-host/use-orqivium/nodes/iteration'
  | '/self-host/use-orqivium/nodes/knowledge-retrieval'
  | '/self-host/use-orqivium/nodes/list-operator'
  | '/self-host/use-orqivium/nodes/llm'
  | '/self-host/use-orqivium/nodes/loop'
  | '/self-host/use-orqivium/nodes/output'
  | '/self-host/use-orqivium/nodes/parameter-extractor'
  | '/self-host/use-orqivium/nodes/question-classifier'
  | '/self-host/use-orqivium/nodes/start'
  | '/self-host/use-orqivium/nodes/template'
  | '/self-host/use-orqivium/nodes/tools'
  | '/self-host/use-orqivium/nodes/trigger/overview'
  | '/self-host/use-orqivium/nodes/trigger/plugin-trigger'
  | '/self-host/use-orqivium/nodes/trigger/schedule-trigger'
  | '/self-host/use-orqivium/nodes/trigger/webhook-trigger'
  | '/self-host/use-orqivium/nodes/user-input'
  | '/self-host/use-orqivium/nodes/variable-aggregator'
  | '/self-host/use-orqivium/nodes/variable-assigner'
  | '/self-host/use-orqivium/publish/README'
  | '/self-host/use-orqivium/publish/publish-mcp'
  | '/self-host/use-orqivium/publish/publish-to-marketplace'
  | '/self-host/use-orqivium/publish/webapp/chatflow-webapp'
  | '/self-host/use-orqivium/publish/webapp/embedding-in-websites'
  | '/self-host/use-orqivium/publish/webapp/web-app-settings'
  | '/self-host/use-orqivium/publish/webapp/workflow-webapp'
  | '/self-host/use-orqivium/workspace/api-extension/api-extension'
  | '/self-host/use-orqivium/workspace/api-extension/cloudflare-worker'
  | '/self-host/use-orqivium/workspace/api-extension/external-data-tool-api-extension'
  | '/self-host/use-orqivium/workspace/api-extension/moderation-api-extension'
  | '/self-host/use-orqivium/workspace/app-management'
  | '/self-host/use-orqivium/workspace/model-providers'
  | '/self-host/use-orqivium/workspace/personal-account-management'
  | '/self-host/use-orqivium/workspace/plugins'
  | '/self-host/use-orqivium/workspace/readme'
  | '/self-host/use-orqivium/workspace/team-members-management'
  | '/self-host/use-orqivium/workspace/tools'

// Deploy paths
type DeployPath =
  | '/deploy/advanced-deployments/local-source-code'
  | '/deploy/advanced-deployments/start-the-frontend-docker-container'
  | '/deploy/configuration/environments'
  | '/deploy/overview'
  | '/deploy/platform-guides/bt-panel'
  | '/deploy/platform-guides/orqivium-premium'
  | '/deploy/quick-start/docker-compose'
  | '/deploy/quick-start/faqs'
  | '/deploy/troubleshooting/common-issues'
  | '/deploy/troubleshooting/docker-issues'
  | '/deploy/troubleshooting/integrations'
  | '/deploy/troubleshooting/storage-and-migration'
  | '/deploy/troubleshooting/weaviate-v4-migration'

// API Reference endpoint paths
type ApiEndpointReferencePath =
  | '/api-reference/annotations/configure-annotation-reply'
  | '/api-reference/annotations/create-annotation'
  | '/api-reference/annotations/delete-annotation'
  | '/api-reference/annotations/get-annotation-reply-job-status'
  | '/api-reference/annotations/list-annotations'
  | '/api-reference/annotations/update-annotation'
  | '/api-reference/applications/get-app-info'
  | '/api-reference/applications/get-app-meta'
  | '/api-reference/applications/get-app-parameters'
  | '/api-reference/applications/get-app-webapp-settings'
  | '/api-reference/audio/convert-audio-to-text'
  | '/api-reference/audio/convert-text-to-audio'
  | '/api-reference/chat-messages/get-next-suggested-questions'
  | '/api-reference/chat-messages/send-chat-message'
  | '/api-reference/chat-messages/stop-chat-message-generation'
  | '/api-reference/chunks/create-child-chunk'
  | '/api-reference/chunks/create-chunks'
  | '/api-reference/chunks/delete-child-chunk'
  | '/api-reference/chunks/delete-chunk'
  | '/api-reference/chunks/get-chunk'
  | '/api-reference/chunks/list-child-chunks'
  | '/api-reference/chunks/list-chunks'
  | '/api-reference/chunks/update-child-chunk'
  | '/api-reference/chunks/update-chunk'
  | '/api-reference/completion-messages/send-completion-message'
  | '/api-reference/completion-messages/stop-completion-message-generation'
  | '/api-reference/conversations/delete-conversation'
  | '/api-reference/conversations/list-conversation-messages'
  | '/api-reference/conversations/list-conversation-variables'
  | '/api-reference/conversations/list-conversations'
  | '/api-reference/conversations/rename-conversation'
  | '/api-reference/conversations/update-conversation-variable'
  | '/api-reference/documents/create-document-by-file'
  | '/api-reference/documents/create-document-by-text'
  | '/api-reference/documents/delete-document'
  | '/api-reference/documents/download-document'
  | '/api-reference/documents/download-documents-as-zip'
  | '/api-reference/documents/get-document'
  | '/api-reference/documents/get-document-indexing-status'
  | '/api-reference/documents/list-documents'
  | '/api-reference/documents/update-document'
  | '/api-reference/documents/update-document-by-file'
  | '/api-reference/documents/update-document-by-text'
  | '/api-reference/documents/update-document-status-in-batch'
  | '/api-reference/end-users/get-end-user-info'
  | '/api-reference/feedback/list-app-feedbacks'
  | '/api-reference/feedback/submit-message-feedback'
  | '/api-reference/files/download-file'
  | '/api-reference/files/upload-file'
  | '/api-reference/human-input/get-human-input-form'
  | '/api-reference/human-input/submit-human-input-form'
  | '/api-reference/knowledge-bases/create-an-empty-knowledge-base'
  | '/api-reference/knowledge-bases/delete-knowledge-base'
  | '/api-reference/knowledge-bases/get-knowledge-base'
  | '/api-reference/knowledge-bases/list-knowledge-bases'
  | '/api-reference/knowledge-bases/retrieve-chunks-from-a-knowledge-base-/-test-retrieval'
  | '/api-reference/knowledge-bases/update-knowledge-base'
  | '/api-reference/knowledge-pipeline/list-datasource-plugins'
  | '/api-reference/knowledge-pipeline/run-datasource-node'
  | '/api-reference/knowledge-pipeline/run-pipeline'
  | '/api-reference/knowledge-pipeline/upload-pipeline-file'
  | '/api-reference/metadata/create-metadata-field'
  | '/api-reference/metadata/delete-metadata-field'
  | '/api-reference/metadata/get-built-in-metadata-fields'
  | '/api-reference/metadata/list-metadata-fields'
  | '/api-reference/metadata/update-built-in-metadata-field'
  | '/api-reference/metadata/update-document-metadata-in-batch'
  | '/api-reference/metadata/update-metadata-field'
  | '/api-reference/models/get-available-models'
  | '/api-reference/tags/create-knowledge-tag'
  | '/api-reference/tags/create-tag-binding'
  | '/api-reference/tags/delete-knowledge-tag'
  | '/api-reference/tags/delete-tag-binding'
  | '/api-reference/tags/get-knowledge-base-tags'
  | '/api-reference/tags/list-knowledge-tags'
  | '/api-reference/tags/update-knowledge-tag'
  | '/api-reference/workflow-runs/get-workflow-run-detail'
  | '/api-reference/workflow-runs/list-workflow-logs'
  | '/api-reference/workflow-runs/run-workflow'
  | '/api-reference/workflow-runs/run-workflow-by-id'
  | '/api-reference/workflow-runs/stop-workflow-task'
  | '/api-reference/workflow-runs/stream-workflow-events'

// Base path without language prefix
type DocPathWithoutLangBase =
  | CloudPath
  | UseOrqiviumPath
  | HomePath
  | LearnPath
  | QuickStartPath
  | ApiReferencePath
  | CliPath
  | DevelopPluginPath
  | SelfHostPath
  | DeployPath
  | ApiEndpointReferencePath

// Combined path without language prefix (supports optional #anchor)
export type DocPathWithoutLang = DocPathWithoutLangBase | `${DocPathWithoutLangBase}#${string}`

// Product availability for productless docs paths
export const docPathProductAvailability: Record<string, readonly DocsProduct[]> = {
  '/deploy/advanced-deployments/local-source-code': ['self-host'],
  '/deploy/advanced-deployments/start-the-frontend-docker-container': ['self-host'],
  '/deploy/configuration/environments': ['self-host'],
  '/deploy/overview': ['self-host'],
  '/deploy/platform-guides/bt-panel': ['self-host'],
  '/deploy/platform-guides/orqivium-premium': ['self-host'],
  '/deploy/quick-start/docker-compose': ['self-host'],
  '/deploy/quick-start/faqs': ['self-host'],
  '/deploy/troubleshooting/common-issues': ['self-host'],
  '/deploy/troubleshooting/docker-issues': ['self-host'],
  '/deploy/troubleshooting/integrations': ['self-host'],
  '/deploy/troubleshooting/storage-and-migration': ['self-host'],
  '/deploy/troubleshooting/weaviate-v4-migration': ['self-host'],
  '/use-orqivium/build/additional-features': ['cloud', 'self-host'],
  '/use-orqivium/build/agent': ['cloud', 'self-host'],
  '/use-orqivium/build/chatbot': ['cloud', 'self-host'],
  '/use-orqivium/build/new-agent/build': ['self-host'],
  '/use-orqivium/build/new-agent/overview': ['self-host'],
  '/use-orqivium/build/orchestrate-node': ['cloud', 'self-host'],
  '/use-orqivium/build/predefined-error-handling-logic': ['cloud', 'self-host'],
  '/use-orqivium/build/shortcut-key': ['cloud', 'self-host'],
  '/use-orqivium/build/text-generator': ['cloud', 'self-host'],
  '/use-orqivium/build/version-control': ['cloud', 'self-host'],
  '/use-orqivium/build/workflow-chatflow': ['cloud', 'self-host'],
  '/use-orqivium/build/workflow-collaboration': ['self-host'],
  '/use-orqivium/debug/error-type': ['cloud', 'self-host'],
  '/use-orqivium/debug/history-and-logs': ['cloud', 'self-host'],
  '/use-orqivium/debug/step-run': ['cloud', 'self-host'],
  '/use-orqivium/debug/variable-inspect': ['cloud', 'self-host'],
  '/use-orqivium/getting-started/introduction': ['cloud', 'self-host'],
  '/use-orqivium/knowledge/connect-external-knowledge-base': ['cloud', 'self-host'],
  '/use-orqivium/knowledge/create-knowledge/chunking-and-cleaning-text': ['cloud', 'self-host'],
  '/use-orqivium/knowledge/create-knowledge/import-text-data/readme': ['cloud', 'self-host'],
  '/use-orqivium/knowledge/create-knowledge/import-text-data/sync-from-notion': ['cloud', 'self-host'],
  '/use-orqivium/knowledge/create-knowledge/import-text-data/sync-from-website': ['cloud', 'self-host'],
  '/use-orqivium/knowledge/create-knowledge/introduction': ['cloud', 'self-host'],
  '/use-orqivium/knowledge/create-knowledge/setting-indexing-methods': ['cloud', 'self-host'],
  '/use-orqivium/knowledge/external-knowledge-api': ['cloud', 'self-host'],
  '/use-orqivium/knowledge/integrate-knowledge-within-application': ['cloud', 'self-host'],
  '/use-orqivium/knowledge/knowledge-pipeline/authorize-data-source': ['cloud', 'self-host'],
  '/use-orqivium/knowledge/knowledge-pipeline/create-knowledge-pipeline': ['cloud', 'self-host'],
  '/use-orqivium/knowledge/knowledge-pipeline/knowledge-pipeline-orchestration': ['cloud', 'self-host'],
  '/use-orqivium/knowledge/knowledge-pipeline/manage-knowledge-base': ['cloud', 'self-host'],
  '/use-orqivium/knowledge/knowledge-pipeline/publish-knowledge-pipeline': ['cloud', 'self-host'],
  '/use-orqivium/knowledge/knowledge-pipeline/readme': ['cloud', 'self-host'],
  '/use-orqivium/knowledge/knowledge-pipeline/upload-files': ['cloud', 'self-host'],
  '/use-orqivium/knowledge/knowledge-request-rate-limit': ['cloud'],
  '/use-orqivium/knowledge/manage-knowledge/introduction': ['cloud', 'self-host'],
  '/use-orqivium/knowledge/manage-knowledge/maintain-knowledge-documents': ['cloud', 'self-host'],
  '/use-orqivium/knowledge/metadata': ['cloud', 'self-host'],
  '/use-orqivium/knowledge/readme': ['cloud', 'self-host'],
  '/use-orqivium/knowledge/test-retrieval': ['cloud', 'self-host'],
  '/use-orqivium/monitor/analysis': ['cloud', 'self-host'],
  '/use-orqivium/monitor/annotation-reply': ['cloud', 'self-host'],
  '/use-orqivium/monitor/integrations/integrate-aliyun': ['cloud', 'self-host'],
  '/use-orqivium/monitor/integrations/integrate-arize': ['cloud', 'self-host'],
  '/use-orqivium/monitor/integrations/integrate-langfuse': ['cloud', 'self-host'],
  '/use-orqivium/monitor/integrations/integrate-langsmith': ['cloud', 'self-host'],
  '/use-orqivium/monitor/integrations/integrate-opik': ['cloud', 'self-host'],
  '/use-orqivium/monitor/integrations/integrate-phoenix': ['cloud', 'self-host'],
  '/use-orqivium/monitor/integrations/integrate-weave': ['cloud', 'self-host'],
  '/use-orqivium/monitor/logs': ['cloud', 'self-host'],
  '/use-orqivium/nodes/agent': ['cloud', 'self-host'],
  '/use-orqivium/nodes/answer': ['cloud', 'self-host'],
  '/use-orqivium/nodes/code': ['cloud', 'self-host'],
  '/use-orqivium/nodes/doc-extractor': ['cloud', 'self-host'],
  '/use-orqivium/nodes/http-request': ['cloud', 'self-host'],
  '/use-orqivium/nodes/human-input': ['cloud', 'self-host'],
  '/use-orqivium/nodes/ifelse': ['cloud', 'self-host'],
  '/use-orqivium/nodes/iteration': ['cloud', 'self-host'],
  '/use-orqivium/nodes/knowledge-retrieval': ['cloud', 'self-host'],
  '/use-orqivium/nodes/list-operator': ['cloud', 'self-host'],
  '/use-orqivium/nodes/llm': ['cloud', 'self-host'],
  '/use-orqivium/nodes/loop': ['cloud', 'self-host'],
  '/use-orqivium/nodes/output': ['cloud', 'self-host'],
  '/use-orqivium/nodes/parameter-extractor': ['cloud', 'self-host'],
  '/use-orqivium/nodes/question-classifier': ['cloud', 'self-host'],
  '/use-orqivium/nodes/start': ['cloud', 'self-host'],
  '/use-orqivium/nodes/template': ['cloud', 'self-host'],
  '/use-orqivium/nodes/tools': ['cloud', 'self-host'],
  '/use-orqivium/nodes/trigger/overview': ['cloud', 'self-host'],
  '/use-orqivium/nodes/trigger/plugin-trigger': ['cloud', 'self-host'],
  '/use-orqivium/nodes/trigger/schedule-trigger': ['cloud', 'self-host'],
  '/use-orqivium/nodes/trigger/webhook-trigger': ['cloud', 'self-host'],
  '/use-orqivium/nodes/user-input': ['cloud', 'self-host'],
  '/use-orqivium/nodes/variable-aggregator': ['cloud', 'self-host'],
  '/use-orqivium/nodes/variable-assigner': ['cloud', 'self-host'],
  '/use-orqivium/publish/README': ['cloud', 'self-host'],
  '/use-orqivium/publish/publish-mcp': ['cloud', 'self-host'],
  '/use-orqivium/publish/publish-to-marketplace': ['cloud', 'self-host'],
  '/use-orqivium/publish/webapp/chatflow-webapp': ['cloud', 'self-host'],
  '/use-orqivium/publish/webapp/embedding-in-websites': ['cloud', 'self-host'],
  '/use-orqivium/publish/webapp/web-app-settings': ['cloud', 'self-host'],
  '/use-orqivium/publish/webapp/workflow-webapp': ['cloud', 'self-host'],
  '/use-orqivium/workspace/api-extension/api-extension': ['cloud', 'self-host'],
  '/use-orqivium/workspace/api-extension/cloudflare-worker': ['cloud', 'self-host'],
  '/use-orqivium/workspace/api-extension/external-data-tool-api-extension': ['cloud', 'self-host'],
  '/use-orqivium/workspace/api-extension/moderation-api-extension': ['cloud', 'self-host'],
  '/use-orqivium/workspace/app-management': ['cloud', 'self-host'],
  '/use-orqivium/workspace/model-providers': ['cloud', 'self-host'],
  '/use-orqivium/workspace/personal-account-management': ['cloud', 'self-host'],
  '/use-orqivium/workspace/plugins': ['cloud', 'self-host'],
  '/use-orqivium/workspace/readme': ['cloud', 'self-host'],
  '/use-orqivium/workspace/subscription-management': ['cloud'],
  '/use-orqivium/workspace/team-members-management': ['cloud', 'self-host'],
  '/use-orqivium/workspace/tools': ['cloud', 'self-host'],
}
