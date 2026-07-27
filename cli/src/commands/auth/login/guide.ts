export const agentGuide = `
WHEN TO USE
  Establish a session before any authenticated command. Interactive browser
  device flow:
    orqctl auth login
    orqctl auth login --host http://localhost
    orqctl auth login --no-browser     print the code/URL instead of opening

NON-INTERACTIVE
  Agents without a browser can supply a bearer token via the ORQIVIUM_TOKEN env
  var instead of logging in; orqctl reads it on every command. See
  'orqctl help account' and 'orqctl help external'.

AFTER LOGIN
  orqctl auth whoami      check the active session
  orqctl auth list        list every authenticated context
  orqctl get app          list apps
`
