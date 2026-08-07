FROM python:3.13-slim

RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libgomp1 \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN pip install uv

# Pull the local packages from the monorepo (not in this subtree).
# LUMINA_REPO must point at THIS repository — it previously cloned an unrelated
# fork, so the deployed API ran a different copy of scoring/ and ingest/ than the
# one in this tree.
ARG LUMINA_REPO=https://github.com/yashchandnani07/Code-Blooded.git
ARG LUMINA_REF=main
RUN git clone --depth=1 --branch "$LUMINA_REF" "$LUMINA_REPO" /tmp/lumina && \
    mkdir -p /app/packages && \
    cp -r /tmp/lumina/packages/. /app/packages/ && \
    rm -rf /tmp/lumina

# App code (subtree push puts apps/api contents here at repo root)
WORKDIR /app/apps/api
COPY . .

# No local database image: all data lives in Postgres via DATABASE_URL. This
# previously copied data/orpha.sqlite, which no longer exists after the Supabase
# migration and would fail the build.

# Install dependencies — local packages resolve via ../../packages = /app/packages
RUN uv sync --frozen --no-dev

EXPOSE 7860

CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
