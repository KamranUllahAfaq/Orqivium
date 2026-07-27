# Dedicated image for the standalone Orqivium Agent backend server.
#
# It is laid out to match how the service is deployed today (see the
# agent_backend compose service): the virtualenv lives at /app/api/.venv and
# the server is started with
#   cd /app/api && .venv/bin/uvicorn orqivium_agent.server.app:app --host 0.0.0.0 --port 5050
#
# Unlike the orqivium-api image (which only installs the base `orqivium-agent`
# dependency), this image installs the `[server]` extra, so jwcrypto, fastapi,
# uvicorn, etc. are present and the server can
# actually start. orqivium-api is intentionally left lean.

# base image
FROM python:3.12-slim-bookworm AS base

WORKDIR /app/api

# Install uv
ENV UV_VERSION=0.8.9

RUN pip install --no-cache-dir uv==${UV_VERSION}


FROM base AS packages

# The build context is the repository root (see build-push.yml), so paths are
# repo-root relative. orqivium-agent ships its own uv.lock that resolves the server
# extra, so this builds standalone without the api project.
COPY orqivium-agent/pyproject.toml orqivium-agent/uv.lock orqivium-agent/README.md ./
COPY orqivium-agent/src ./src
# Trust the checked-in lock during image builds and install the server extra.
RUN uv sync --frozen --no-dev --no-editable --extra server


# production stage
FROM base AS production

ENV TZ=UTC
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
ENV PYTHONIOENCODING=utf-8
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app/api

# Create non-root user (uid matches the orqivium-api image convention)
ARG orqivium_uid=1001
RUN groupadd -r -g ${orqivium_uid} orqivium && \
    useradd -r -u ${orqivium_uid} -g ${orqivium_uid} -s /bin/bash orqivium

# Copy the resolved virtualenv. The orqivium-agent package is installed
# non-editable, so the source is already baked into site-packages.
ENV VIRTUAL_ENV=/app/api/.venv
COPY --from=packages --chown=orqivium:orqivium ${VIRTUAL_ENV} ${VIRTUAL_ENV}
ENV PATH="${VIRTUAL_ENV}/bin:${PATH}"

# storage is bind-mounted at runtime; pre-create it so the orqivium user can write.
RUN mkdir -p /app/api/storage && chown -R orqivium:orqivium /app/api

ARG COMMIT_SHA
ENV COMMIT_SHA=${COMMIT_SHA}

EXPOSE 5050

USER orqivium

CMD ["uvicorn", "orqivium_agent.server.app:app", "--host", "0.0.0.0", "--port", "5050"]
