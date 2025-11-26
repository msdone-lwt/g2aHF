# Hugging Face Spaces (Docker SDK) - Gemini-API wrapper with Clash proxy
FROM python:3.11-slim

# Avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Create non-root user (recommended for Spaces)
RUN useradd -m appuser
WORKDIR /home/appuser/app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libmagic1 \
    wget \
    unzip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Clash
RUN echo "安装 Clash..." \
    && CLASH_VERSION="v1.18.0" \
    && CLASH_ARCH="linux-amd64" \
    && wget -O /tmp/clash.tar.gz "https://github.com/Dreamacro/clash/releases/download/${CLASH_VERSION}/clash-${CLASH_ARCH}-${CLASH_VERSION}.gz" \
    && cd /tmp \
    && gunzip clash.tar.gz \
    && tar -xf clash.tar \
    && mv clash-${CLASH_ARCH}-${CLASH_VERSION}/clash /usr/local/bin/ \
    && chmod +x /usr/local/bin/clash \
    && rm -rf /tmp/clash*

# Install PyYAML for config generation
RUN pip install --no-cache-dir PyYAML

# Copy files
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt
COPY app ./app
COPY scripts ./scripts
COPY README.md ./README.md

# Runtime env
ENV PYTHONUNBUFFERED=1 \
    GEMINI_COOKIE_PATH=/tmp/gemini_webapi \
    CLASH_PORT=1080

# Expose ports
ENV PORT=7860
EXPOSE ${PORT}
EXPOSE ${CLASH_PORT}

# Make directories writable
RUN mkdir -p /tmp/gemini_webapi /tmp/clash && chown -R appuser:appuser /tmp/gemini_webapi /tmp/clash

# Switch to non-root user
USER appuser

# Start services with our custom script
CMD ["/home/appuser/app/scripts/start.sh"]

