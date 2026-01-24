FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

ARG VERSION
ENV SETUPTOOLS_SCM_PRETEND_VERSION_FOR_CVW22_OPERATIONS_OFFICER=${VERSION}
ENV UV_NO_DEV=1
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /bot

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project

COPY . /bot

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked

FROM python:3.12-slim-bookworm

COPY --from=builder --chown=nonroot:nonroot /bot /bot

ENV PATH="/bot/.venv/bin:$PATH"

WORKDIR /bot

CMD ["python", "src/cvw22_operations_officer", "--config-dir", "/config"]
