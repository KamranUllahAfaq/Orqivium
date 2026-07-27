# orqivium-agent-runtime

Go implementation of the shellctl server and runtime utilities.

## Architecture

```
cmd/
  shellctl/          - main server binary (shellctl serve)
  sanitize-pty/      - tmux pipe-pane PTY sanitizer (stdin→stdout filter)
  runner-exit/       - post-drain SQLite exit recorder
  orqivium-agent-cli/    - cli tool talking to agent backend
  runner/            - process runner to bootstrap agent commands
internal/            - internal implementations
```

## Building

```bash
make build
```

Produces binaries in `bin/`:

### Building docker image

```
docker build -f orqivium-agent-runtime/docker/Dockerfile \
  --build-context agent=./orqivium-agent \
  -t orqivium-agent-runtime:latest \
  orqivium-agent-runtime/
```

### Running docker container

```
docker run -d --name orqivium-agent-runtime \
  -p 15004:5004 \
  orqivium-agent-runtime:latest
```

## Help text generation

Cli help can be generated and injected to orqivium-agent's system prompt.

```sh
make gen-cli-help
```

## Testing

```bash
make test
```

## Path Isolation

Each agent job runs inside a Landlock sandbox that restricts filesystem access:

| Access               | Paths (defaults)                                                                                              |
| -------------------- | ------------------------------------------------------------------------------------------------------------- |
| **Read-Write**       | `$HOME` (always, includes `$CWD/.tmp` as `TMPDIR`)                                                            |
| **Read-Write (dev)** | `/dev/null`, `/dev/zero`, `/dev/urandom`, `/dev/random`, `/dev/tty`                                           |
| **Read-Only + Exec** | `/usr`, `/bin`, `/sbin`, `/lib`, `/lib64`, `/etc`, `/proc`, `/opt/orqivium-agent-tools`, `/opt/homebrew`, `/snap` |
| **Denied**           | Everything else (`/tmp`, other agents' homes, `/var`, `/srv`, etc.)                                           |

The runner automatically creates `$CWD/.tmp` and sets `TMPDIR`, `TMP`, `TEMP` to it, so temp files stay isolated per workspace.

### Environment Variables

See [here](./internal/envvar/envvar.go)

Requires Linux ≥ 5.13. On unsupported kernels, a warning is printed to stderr.

## Dependencies

- Go 1.26
- `modernc.org/sqlite` (pure-Go SQLite driver, no CGO required)
- tmux (runtime dependency, not a build dependency)
