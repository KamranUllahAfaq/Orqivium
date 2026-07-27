# orqctl

Compatibility CLI client for the Orqivium platform, retaining the `orqctl` command and Orqivium API contract. Browser device-flow signin, list/inspect apps, run with structured input, parse output as JSON, YAML, or human text.

## Install (edge, internal)

Per-commit `edge` builds are published to Cloudflare R2. The installer script lives in this repo; binaries are fetched from R2 via `ORQCTL_R2_BASE` (shared internally):

```sh
curl -fsSL https://raw.githubusercontent.com/kamranullahafaq/orqivium/main/cli/scripts/install-r2.sh | ORQCTL_R2_BASE=<BASE> sh
```

| Env                     | Default            | Purpose                                                             |
| ----------------------- | ------------------ | ------------------------------------------------------------------- |
| `ORQCTL_R2_BASE`       | — (required)       | R2 public base, e.g. `https://pub-….r2.dev`.                        |
| `ORQCTL_CHANNEL`       | `edge`             | Channel to install.                                                 |
| `ORQCTL_INSTALL_DIR`   | `$HOME/.local/bin` | Directory the binary is written to (`<dir>/orqctl`).               |
| `ORQCTL_VERSION`       | latest             | Pin an exact published version.                                     |
| `ORQCTL_COMMIT`        | latest             | Pin by git commit (short or full sha).                              |
| `ORQCTL_R2_PREFIX`     | `orqctl`          | R2 key root for the pointer JSONs (`manifest.json` / `index.json`). |
| `ORQCTL_R2_BIN_PREFIX` | `orqctl/bin`      | R2 key root for binaries (the lifecycle/TTL target).                |

By default the channel pointer (latest build) is installed. Set `ORQCTL_COMMIT` (e.g. `ce4af86`) or `ORQCTL_VERSION` to install a specific past build — both resolve through the channel's `index.json`:

```sh
curl -fsSL https://raw.githubusercontent.com/kamranullahafaq/orqivium/main/cli/scripts/install-r2.sh | ORQCTL_R2_BASE=<BASE> ORQCTL_COMMIT=ce4af86 sh
```

Windows: `$env:ORQCTL_R2_BASE='<BASE>'; irm https://raw.githubusercontent.com/kamranullahafaq/orqivium/main/cli/scripts/install-r2.ps1 | iex` (same env vars, e.g. `$env:ORQCTL_COMMIT='ce4af86'`).

Re-run to upgrade. For tagged `rc`/`stable` builds, use the GitHub installer (`install-cli.sh` / `install.ps1`), which resolves releases via the GitHub API. That API caps unauthenticated requests at 60/hour per IP; behind a shared NAT or in CI, set `GITHUB_TOKEN` (or `GH_TOKEN`) to raise it to 5000/hour — the installer sends it as a bearer token.

## Quickstart

```sh
orqctl auth login                                       # opens browser; paste the device code shown
orqctl get app                                          # list apps in default workspace
orqctl describe app <app-id>                            # inspect parameters
orqctl run app <app-id> "hello"                         # run, blocking
orqctl run app <app-id> "hello" -o json | jq .answer    # JSON output
orqctl run app <app-id> --input name=world --input topic=cats   # workflow inputs
```

Background docs: `orqctl help account`, `orqctl help external`, `orqctl help environment`, `orqctl help agent`.

## Commands

Run `orqctl --help` for the full list of commands.
Run `orqctl <cmd> --help` for per-command reference.

For agents (and scripting), start with `orqctl help agent` — the cross-command operating guide (output, discovery, auth, exit codes, errors, HITL, retry). Every help surface is also machine-readable: `orqctl help -o json` dumps the whole command tree plus the global contract (exit codes, output formats, error envelope, HITL protocol), and `orqctl <cmd> --help -o json` returns one command's descriptor.

## Agent skill

`orqctl skills install` installs a single, pure-delegation `SKILL.md` into your local agents so they auto-load it. The skill does not freeze the command set — it points the agent at `orqctl help -o json` for the live surface, so it never drifts from your binary. It is embedded in the binary (version-stamped) rather than checked in.

- `orqctl skills install` — dry-run: detect installed agents (Claude Code, Codex, opencode, Cursor, pi) and print where the skill would land. Writes nothing.
- `orqctl skills install --yes` — write to every detected agent, printing each path. `--agent claude-code[,cursor]` restricts to a subset; `<dir>` forces one explicit directory (handy when your agent isn't detected).
- `orqctl skills install --stdout` — print the `SKILL.md` to stdout (for piping or self-install); writes nothing.

Detection is by config-directory existence (`~/.claude`, `~/.codex`, `~/.config/opencode`, `~/.cursor`, `~/.pi`). If a copy ever looks stale, run `orqctl version` and re-run `orqctl skills install`.

## Output formats

| Flag      | Behavior                                               |
| --------- | ------------------------------------------------------ |
| (none)    | Human table, columns auto-sized to terminal.           |
| `-o wide` | Same as table, no column truncation.                   |
| `-o json` | Pretty-printed JSON, machine-parseable, stable shape.  |
| `-o yaml` | YAML mirror of `-o json`.                              |
| `-o name` | IDs only, newline-separated — pipes into `xargs`.      |
| `-o text` | kubectl-describe style human text (`describe`, `run`). |

Errors emit JSON envelope to stderr in `-o json` mode; else human message. Exit codes deterministic.

## Configuration

| OS      | Config path                                  |
| ------- | -------------------------------------------- |
| Linux   | `${XDG_CONFIG_HOME:-$HOME/.config}/orqctl/` |
| macOS   | `$HOME/.config/orqctl/`                     |
| Windows | `%APPDATA%\orqctl\`                         |

Override with `ORQIVIUM_CONFIG_DIR=/some/path`. Files written `0600`, directory `0700`. Tokens use OS keychain by default, fall back to sealed file on hosts without one.

For every env var `orqctl` reads, run `orqctl env list` (machine-readable) or `orqctl help environment` (narrative).

## Streaming

`run app` uses blocking transport by default. For long-running apps (likely exceed ~30s) pass `--stream`:

```sh
orqctl run app app-1 "tell me about cats" --stream
```

Agent apps (`mode === 'agent-chat'` or `is_agent` flag set) stream regardless — Orqivium backend rejects blocking requests for agent mode. Combining `--stream` with `-o json` or `-o yaml` aggregates SSE events into same envelope shape as blocking response, so structured output identical regardless of transport.

## HTTP retry

Idempotent requests (`GET`, `PUT`, `DELETE`) retry on transient network/DNS failures with exponential backoff. Default count: **3**. `POST` and `PATCH` never retry — side effects possible.

| Knob                     | Effect                                         |
| ------------------------ | ---------------------------------------------- |
| `--http-retry <n>`       | Per-invocation override. `0` disables retries. |
| `ORQCTL_HTTP_RETRY=<n>` | Process-level default.                         |

Resolution: flag → env → 3.

## Contributing

See [`ARD.md`] for architecture patterns, scaffolding recipe, dev workflow.

## License

Apache-2.0.

[Orqivium]: /
[`ARD.md`]: ARD.md
