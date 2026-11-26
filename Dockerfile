# Dockerfile — MX-UI v2.2.0 + Xray Core + Telegram SOCKS5 + bore.pub TCP Tunnel
FROM python:3.11-slim AS builder

ARG XRAY_VERSION=v25.1.30
ARG BORE_VERSION=0.5.2
ARG TARGETARCH

RUN apt-get update && apt-get install -y --no-install-recommends \
        curl unzip tar ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN set -eux; \
    ARCH="${TARGETARCH:-amd64}"; \
    case "${ARCH}" in \
        amd64) XRAY_ASSET="Xray-linux-64.zip"; BORE_ARCH="x86_64-unknown-linux-musl" ;; \
        arm64) XRAY_ASSET="Xray-linux-arm64-v8a.zip"; BORE_ARCH="aarch64-unknown-linux-musl" ;; \
        arm)   XRAY_ASSET="Xray-linux-arm32-v7a.zip"; BORE_ARCH="" ;; \
        *) echo "Unsupported arch: ${ARCH}"; exit 1 ;; \
    esac; \
    mkdir -p /tmp/bins; \
    curl -fsSL -o /tmp/xray.zip "https://github.com/XTLS/Xray-core/releases/download/${XRAY_VERSION}/${XRAY_ASSET}"; \
    unzip -o /tmp/xray.zip xray -d /tmp/bins; \
    chmod +x /tmp/bins/xray; \
    if [ -n "${BORE_ARCH}" ]; then \
      curl -fsSL -o /tmp/bore.tar.gz "https://github.com/ekzhang/bore/releases/download/v${BORE_VERSION}/bore-v${BORE_VERSION}-${BORE_ARCH}.tar.gz"; \
      tar -xzf /tmp/bore.tar.gz -C /tmp/bins bore; \
      chmod +x /tmp/bins/bore; \
    fi

FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    DATA_DIR=/data \
    INTERNAL_PORT=8001 \
    PORT=8080 \
    TG_TUNNEL_MODE=bore \
    BORE_SERVER=bore.pub

RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates tzdata curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /tmp/bins/ /usr/local/bin/
RUN chmod +x /usr/local/bin/xray && /usr/local/bin/xray version

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /data && chmod 755 /data

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=25s --retries=3 \
    CMD curl -fsS http://127.0.0.1:${PORT:-8080}/health || exit 1

CMD ["python3", "main.py"]
