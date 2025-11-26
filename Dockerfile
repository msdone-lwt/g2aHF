# Hugging Face Spaces (Docker SDK) - Gemini-API wrapper
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
    && rm -rf /var/lib/apt/lists/*

# Copy files
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
COPY README.md ./README.md

# Runtime env
ENV PYTHONUNBUFFERED=1 \
    GEMINI_COOKIE_PATH=/tmp/gemini_webapi

# Expose $PORT for Spaces
ENV PORT=7860

# Make cookie dir writable
RUN mkdir -p /tmp/gemini_webapi && chown -R appuser:appuser /tmp/gemini_webapi

# Switch to non-root user
USER appuser

# Start the FastAPI server
CMD ["bash", "-lc", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]

