export const agentGuide = `
WHEN TO USE
  Inspect one app before running it — reveals its mode and the input
  variables / parameters it expects:
    orqctl describe app <id> -o json
    orqctl describe app <id> -o json | jq '.info.mode'

NEXT
  Feed the discovered inputs to run:
    orqctl run app <id> --inputs '{"key":"value"}' -o json

ERROR RECOVERY
  app not found (404)      orqctl get app
  not logged in (exit 4)   orqctl auth login
`
