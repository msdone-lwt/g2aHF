---
title: G2
emoji: 🐢
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
---

This Space exposes an OpenAI-compatible Gemini API server (gemini_webapi) via FastAPI.

Deployment: Docker (Hugging Face Spaces)

Environment variables (set in Spaces Secrets):
- SECURE_1PSID: required
- SECURE_1PSIDTS: optional
- API_KEY: optional. If set, requests must include Authorization: Bearer <API_KEY>
- ENABLE_THINKING: optional, default false
- GEMINI_COOKIE_PATH: optional, default /tmp/gemini_webapi

Endpoints:
- GET / : status
- GET /v1/models : list available models
- POST /v1/chat/completions : OpenAI-compatible chat API, supports stream=true (SSE) and data:image base64 attachments

Run: the container automatically starts uvicorn on $PORT.

Check out the configuration reference at https://huggingface.co/docs/hub/spaces-config-reference
