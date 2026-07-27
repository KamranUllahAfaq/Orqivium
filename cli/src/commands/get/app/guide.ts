export const agentGuide = `
DISCOVERY
  List apps to find their ids and modes before running one:
    orqctl get app -o json          all apps in the default workspace
    orqctl get app -A -o json       across every workspace you can see
    orqctl get app <id> -o json     one app's basic info

  Each app's "mode" (chat / advanced-chat / completion / workflow / agent-chat)
  decides how you call run app. Use 'orqctl describe app <id>' for the full
  input schema.

ERROR RECOVERY
  not logged in (exit 4)   orqctl auth login
  empty list               wrong workspace — try -A or --workspace <id>
`
