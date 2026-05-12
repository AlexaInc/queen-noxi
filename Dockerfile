# ── HuggingFace / Docker deployment ──────────────────────────────────────────
FROM python:3.10-slim

ENV PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# System dependencies
RUN apt-get update && apt-get upgrade -y && \
    apt-get install --no-install-recommends -y \
        bash \
        curl \
        git \
        ffmpeg \
        libffi-dev \
        libjpeg-dev \
        libwebp-dev \
        libpq-dev \
        libssl-dev \
        libxml2-dev \
        libxslt1-dev \
        gcc \
        wget \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first (layer cache)
COPY requirements.txt .
RUN pip install --upgrade pip setuptools && \
    pip install -r requirements.txt

# Copy the full project
COPY . .

# Install Node.js dependencies for the brain (if package.json exists)
RUN if [ -f QueenNoxi/brain/package.json ]; then cd QueenNoxi/brain && npm install --production; fi

# HuggingFace Spaces listens on port 7860 by default (not needed for a bot,
# but included so the Space doesn't time out waiting for an HTTP server)
EXPOSE 7860

# Run the bot via the HF entrypoint
CMD ["python", "app.py"]
