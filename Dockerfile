# Stage 1 - Install build dependencies
FROM python:3.13-alpine AS builder
RUN apk add --no-cache \
    build-base \
    sdl2-dev \
    gcc
WORKDIR /app
RUN python -m venv .venv && .venv/bin/pip install --no-cache-dir -U pip setuptools
COPY requirements.txt .
RUN .venv/bin/pip install --no-cache-dir -r requirements.txt
RUN find /app/.venv \
      \( -type d \( -name test -o -name tests \) -o -type f \( -name '*.pyc' -o -name '*.pyo' \) \) \
      -exec rm -rf '{}' + 2>/dev/null || true
# Stage 2 - Copy only necessary files to the runner stage
FROM python:3.13-alpine
RUN apk add --no-cache g++ jpeg-dev zlib-dev libjpeg make
WORKDIR /app
COPY --from=builder /app /app
COPY . .
ENV PATH="/app/.venv/bin:$PATH"
CMD ["python", "/app/run.py"]
