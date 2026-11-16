# Imágenes de producción (decisión 029). Se construyen en la propia VM: sirven igual en ARM y en x86.
#   app: API y worker (misma imagen, distinto comando en compose.prod.yaml)
#   web: Caddy con el frontend compilado

# --- Frontend compilado ---
FROM node:22-slim AS frontend
RUN corepack enable && corepack prepare pnpm@12.9.1 --activate
WORKDIR /frontend
COPY frontend/package.json frontend/pnpm-lock.yaml frontend/pnpm-workspace.yaml ./
RUN pnpm install --frozen-lockfile
COPY frontend/ ./
RUN pnpm run build

# --- Solver C del modelo ---
FROM python:3.14-slim AS solver
RUN apt-get update && apt-get install -y --no-install-recommends gcc libc6-dev && rm -rf /var/lib/apt/lists/*
WORKDIR /c_lib
COPY backend/services/verhulst/src/c_lib/cochlea_utils.c ./
RUN gcc -shared -fpic -O3 -ffast-math -o tridiag.so cochlea_utils.c

# --- API y worker ---
FROM python:3.14-slim AS app
COPY --from=ghcr.io/astral-sh/uv:0.12.21 /uv /bin/uv
WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy PATH="/app/.venv/bin:$PATH" PYTHONUNBUFFERED=1
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev
COPY . .
COPY --from=solver /c_lib/tridiag.so backend/services/verhulst/src/c_lib/tridiag.so
# Caddy es el único que llega a la API: se le cree la IP real del cliente (límite por IP de slowapi)
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips", "*"]

# --- Caddy con el frontend ---
FROM caddy:2 AS web
COPY deploy/Caddyfile /etc/caddy/Caddyfile
COPY --from=frontend /frontend/dist /srv
