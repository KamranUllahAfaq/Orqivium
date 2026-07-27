import { ENV_REGISTRY } from '@/env/registry'
import { CONTRACT } from './contract'

export type HelpTopic = {
  readonly name: string
  readonly summary: string
  readonly render: () => string
}

const ACCOUNT_HELP_TEXT = `orqctl: account-bearer onboarding

  1. Sign in interactively (browser device flow):
       orqctl auth login

  2. List accessible apps in your default workspace:
       orqctl get app

  3. Describe one app to see its parameters:
       orqctl describe app <id>

  4. Run an app and capture structured output:
       orqctl run app <id> "hello" -o json

Tips:
  * Two app nouns: 'studio-app' is what you build and edit in Studio on the
    web console inside a workspace (its source definition — export or move it);
    'app' is a published app you run and inspect.
  * 'orqctl auth list' shows your authenticated contexts; 'orqctl use host'
    and 'orqctl use account' switch between them.
  * Pass --workspace <id> to target a non-default workspace.
  * Pass --stream to 'orqctl run app' for live token/event output.
  * 'orqctl env list' shows every env var orqctl reads.
`

const EXTERNAL_HELP_TEXT = `orqctl: external-SSO bearer onboarding

  Most agents authenticate as a human account (see 'orqctl help account').
  External-SSO bearers (dfoe_) skip the human flow and exchange an upstream
  identity for a Orqivium token. The CLI surfaces the same commands but a
  smaller dataset:

  1. Acquire a token through your SSO provider (out of band).
  2. Hand it to the CLI via the ORQIVIUM_TOKEN environment variable:
       export ORQIVIUM_TOKEN="<your-token>"

  3. List apps your subject is permitted to invoke:
       orqctl get app

  4. Run an app:
       orqctl run app <id> "hello" -o json

Notes:
  * 'orqctl get workspace' returns an empty list for external bearers — that
    is expected; external subjects have no workspace membership.
  * Tokens are best stored in ORQIVIUM_TOKEN; orqctl reads it on every command.
`

function renderEnvironment(): string {
  let out = 'ENVIRONMENT VARIABLES\n\n'
  for (const v of ENV_REGISTRY) {
    out += `  ${v.name}\n      ${v.description}\n`
    if (v.sensitive) out += '      (treat as secret; never echoed)\n'
    out += '\n'
  }
  return out
}

function renderAgent(): string {
  const exitCodes = Object.entries(CONTRACT.exitCodes)
    .map(([code, desc]) => `  ${code}  ${desc}`)
    .join('\n')

  return `orqctl: agent operating guide

OUTPUT
  Pass -o json (or -o yaml) on every command — the JSON shape is stable and
  documented. Without it you get human tables meant for a terminal.

APP vs STUDIO-APP
  Two nouns, two faces of the same app:
    studio-app   what you build and edit in Studio on the web console,
                 inside a workspace — the app's source definition.
    app          a published app, live and runnable.
  Use 'studio-app' to work with the definition you manage on the website
  (export it, move it between workspaces or instances); use 'app' to run
  and inspect a published one. The COMMANDS list shows the verbs each
  noun supports.

DISCOVERY
  orqctl help -o json        full command tree + this contract, machine-readable
  orqctl get app -o json     list apps (ids + modes)
  orqctl describe app <id>   one app's mode and input schema

AUTH
  Interactive:     orqctl auth login         (browser device flow)
  Non-interactive: export ORQIVIUM_TOKEN=<bearer>  (read on every command)
  Details:         orqctl help account / orqctl help external

EXIT CODES
${exitCodes}

ERRORS
  Under -o json/yaml a failure writes a structured envelope to stderr:
    ${CONTRACT.errorEnvelope.shape}

HUMAN-IN-THE-LOOP
  ${CONTRACT.hitl.description}
  Resume: ${CONTRACT.hitl.resume}

RETRY
  Idempotent GET/PUT/DELETE retry on transient errors (default 3); POST/PATCH
  never. Override with --http-retry <n> or ORQCTL_HTTP_RETRY.
`
}

export const TOPICS: readonly HelpTopic[] = [
  {
    name: 'account',
    summary: 'Agent-onboarding text for account bearers (dfoa_)',
    render: () => ACCOUNT_HELP_TEXT,
  },
  {
    name: 'agent',
    summary: 'Cross-command contract for agents driving orqctl',
    render: renderAgent,
  },
  {
    name: 'environment',
    summary: 'Long-form documentation for every ORQIVIUM_* env var',
    render: renderEnvironment,
  },
  {
    name: 'external',
    summary: 'Agent-onboarding text for external-SSO bearers (dfoe_)',
    render: () => EXTERNAL_HELP_TEXT,
  },
]

export function findTopic(name: string): HelpTopic | undefined {
  return TOPICS.find((t) => t.name === name)
}
