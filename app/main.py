import asyncio
import base64
import json
import os
import tempfile
import time
import uuid
from pathlib import Path
from typing import List, Optional, Union, Any, Dict

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from loguru import logger

# Gemini web API wrapper
from gemini_webapi import GeminiClient, set_log_level
from gemini_webapi.constants import Model

# -----------------------------------------------------------------------------
# Environment & config
# -----------------------------------------------------------------------------
# Align with reference project: prefer uppercase env var names, keep backward compatibility
SECURE_1PSID = (
    os.getenv("SECURE_1PSID")
    or os.getenv("Secure_1PSID")
)
SECURE_1PSIDTS = (
    os.getenv("SECURE_1PSIDTS")
    or os.getenv("Secure_1PSIDTS")
)
API_KEY = os.getenv("API_KEY", "")
ENABLE_THINKING = os.getenv("ENABLE_THINKING", "false").lower() == "true"
COOKIE_DIR = os.getenv("GEMINI_COOKIE_PATH", "/tmp/gemini_webapi")
CLASH_PROXIES = os.getenv("CLASH_PROXIES", "")

# Ensure cookie dir exists
Path(COOKIE_DIR).mkdir(parents=True, exist_ok=True)

set_log_level("INFO")

# -----------------------------------------------------------------------------
# FastAPI app
# -----------------------------------------------------------------------------
app = FastAPI(title="Gemini API FastAPI Server")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------------------------------------------
# Models for OpenAI-compatible Chat Completions API
# -----------------------------------------------------------------------------
class MessageContentText(BaseModel):
    type: str
    text: Optional[str] = None

class MessageContentImageURL(BaseModel):
    type: str
    image_url: Optional[dict] = None  # { url: "..." }

MessageContent = Union[MessageContentText, MessageContentImageURL]

class Message(BaseModel):
    role: str  # "system" | "user" | "assistant"
    content: Union[str, List[MessageContent]]

class ChatCompletionRequest(BaseModel):
    model: str = "gemini-2.5-pro"
    messages: List[Message]
    stream: Optional[bool] = False

# -----------------------------------------------------------------------------
# Global Gemini client (lazy init)
# -----------------------------------------------------------------------------
_gemini_client: Optional[GeminiClient] = None
_client_lock = asyncio.Lock()

async def get_gemini_client() -> GeminiClient:
    global _gemini_client
    async with _client_lock:
        if _gemini_client is None:
            if not SECURE_1PSID:
                logger.error("SECURE_1PSID is missing. Set it in environment variables.")
                raise HTTPException(status_code=500, detail="SECURE_1PSID not configured")
            try:
                # GeminiClient persists/refreshes cookies; path is controlled by env GEMINI_COOKIE_PATH
                # Parse and use proxy if CLASH_PROXIES is set
                proxy = None
                if CLASH_PROXIES:
                    proxy = parse_clash_proxy(CLASH_PROXIES)
                    if proxy:
                        logger.info(f"解析 Clash 代理成功: {proxy}")
                    else:
                        logger.warning("解析 Clash 代理失败，将不使用代理")
                
                _gemini_client = GeminiClient(SECURE_1PSID, SECURE_1PSIDTS, proxy=proxy)
                await _gemini_client.init(timeout=60, auto_close=True, close_delay=300, auto_refresh=True)
                if proxy:
                    logger.info(f"Gemini 客户端通过代理初始化成功: {proxy}")
                else:
                    logger.info("Gemini 客户端初始化成功（无代理）")
            except Exception as e:
                logger.exception("Failed to initialize Gemini client")
                raise HTTPException(status_code=500, detail=f"Failed to initialize Gemini client: {e}")
        return _gemini_client

# -----------------------------------------------------------------------------
# API key verification (optional)
# -----------------------------------------------------------------------------
async def verify_api_key(authorization: Optional[str] = Header(None)) -> None:
    """Verify API key if API_KEY is set. Use Authorization: Bearer <API_KEY>.
    If API_KEY is empty, authentication is skipped.
    """
    if not API_KEY:
        return
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    token = authorization.split(" ", 1)[1].strip()
    if token != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

# -----------------------------------------------------------------------------
# Proxy utilities
# -----------------------------------------------------------------------------
def parse_clash_proxy(clash_proxies: str) -> Optional[str]:
    """解析 Clash 节点信息并返回代理 URL
    
    Args:
        clash_proxies: Clash 节点 JSON 字符串
        
    Returns:
        代理 URL (如: socks5://127.0.0.1:1080) 或 None
    """
    if not clash_proxies:
        return None
        
    try:
        # 尝试解析 JSON
        proxy_config = json.loads(clash_proxies)
        
        # 根据不同类型生成代理 URL
        proxy_type = proxy_config.get('type', '').lower()
        server = proxy_config.get('server', '127.0.0.1')
        port = proxy_config.get('port', 1080)
        
        if proxy_type == 'vmess':
            # VMess 需要转换为本地代理端口，通常需要 clash 客户端运行
            # 这里假设 clash 客户端在本地运行，默认端口 1080
            return "socks5://127.0.0.1:1080"
        elif proxy_type == 'vless':
            return "socks5://127.0.0.1:1080"
        elif proxy_type == 'trojan':
            return "socks5://127.0.0.1:1080"
        elif proxy_type == 'ss':
            return "socks5://127.0.0.1:1080"
        elif proxy_type == 'ssr':
            return "socks5://127.0.0.1:1080"
        elif proxy_type == 'http':
            username = proxy_config.get('username')
            password = proxy_config.get('password')
            if username and password:
                return f"http://{username}:{password}@{server}:{port}"
            else:
                return f"http://{server}:{port}"
        elif proxy_type == 'socks5':
            username = proxy_config.get('username')
            password = proxy_config.get('password')
            if username and password:
                return f"socks5://{username}:{password}@{server}:{port}"
            else:
                return f"socks5://{server}:{port}"
        else:
            # 默认使用本地 clash 代理
            logger.warning(f"不支持的代理类型: {proxy_type}，使用默认本地代理")
            return "socks5://127.0.0.1:1080"
            
    except json.JSONDecodeError as e:
        logger.error(f"解析 Clash 代理配置失败: {e}")
        # 如果不是 JSON，尝试直接作为代理 URL
        if clash_proxies.startswith(('http://', 'https://', 'socks5://')):
            return clash_proxies
        return None
    except Exception as e:
        logger.error(f"处理代理配置时出错: {e}")
        return None

# -----------------------------------------------------------------------------
# Utilities
# -----------------------------------------------------------------------------
def map_model_name(openai_model_name: str) -> Any:
    """Map incoming model string to gemini_webapi.constants.Model enum value.
    Falls back to Model.UNSPECIFIED if no match.
    """
    name = (openai_model_name or "").lower()
    # Simple heuristics for mapping
    if "3.0" in name and "pro" in name:
        for m in Model:
            try:
                if "3.0" in m.model_name and "pro" in m.model_name:
                    return m
            except Exception:
                pass
    if "2.5" in name and "flash" in name:
        for m in Model:
            try:
                if "2.5" in m.model_name and "flash" in m.model_name:
                    return m
            except Exception:
                pass
    if "2.5" in name and "pro" in name:
        for m in Model:
            try:
                if "2.5" in m.model_name and "pro" in m.model_name:
                    return m
            except Exception:
                pass
    # Generic match by substring
    for m in Model:
        try:
            if name and name in m.model_name.lower():
                return m
        except Exception:
            continue
    # Default
    try:
        return Model.UNSPECIFIED
    except Exception:
        # Fallback to first enum member
        for m in Model:
            return m
        return None

def prepare_conversation(messages: List[Message]) -> tuple[str, List[str]]:
    """Transform OpenAI-like messages to a conversation string and collect temp files.
    - Supports plain string content.
    - Supports array content with type 'text' and 'image_url'.
    - For data URLs (base64), decode to temporary files and pass to Gemini.
    """
    conversation = ""
    temp_files: List[str] = []

    for msg in messages:
        role = msg.role
        content = msg.content
        prefix = ""
        if role == "system":
            prefix = "System: "
        elif role == "user":
            prefix = "Human: "
        elif role == "assistant":
            prefix = "Assistant: "
        else:
            prefix = f"{role.capitalize()}: "

        conversation += prefix

        if isinstance(content, str):
            conversation += content
        else:
            # content is a list of MessageContent
            for item in content:
                if isinstance(item, MessageContentText):
                    conversation += item.text or ""
                elif isinstance(item, MessageContentImageURL):
                    url = (item.image_url or {}).get("url", "")
                    if url.startswith("data:image/"):
                        # Handle base64 encoded image
                        try:
                            base64_data = url.split(",", 1)[1]
                            image_data = base64.b64decode(base64_data)
                            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                                tmp.write(image_data)
                                temp_files.append(tmp.name)
                        except Exception as e:
                            logger.warning(f"Failed to decode image data URL: {e}")
                    else:
                        # For remote URLs, we ignore here to avoid extra deps; users can send data URLs instead
                        logger.info("Ignoring non-data URL image. Use data URL if you need to attach inline images.")
        conversation += "\n\n"

    # Final assistant cue
    conversation += "Assistant: "
    return conversation, temp_files

# -----------------------------------------------------------------------------
# Endpoints
# -----------------------------------------------------------------------------
@app.get("/")
async def root():
    masked_sid = (SECURE_1PSID[:5] + "..." if SECURE_1PSID else "")
    masked_sidts = (SECURE_1PSIDTS[:5] + "..." if SECURE_1PSIDTS else "")
    
    # 显示代理信息
    proxy_info = None
    if CLASH_PROXIES:
        try:
            proxy_config = json.loads(CLASH_PROXIES)
            proxy_info = {
                "name": proxy_config.get("name", ""),
                "type": proxy_config.get("type", ""),
                "server": proxy_config.get("server", ""),
                "port": proxy_config.get("port", "")
            }
        except:
            proxy_info = {"raw": CLASH_PROXIES[:50] + "..." if len(CLASH_PROXIES) > 50 else CLASH_PROXIES}
    
    return {
        "status": "online",
        "message": "Gemini API FastAPI Server is running",
        "has_api_key": bool(API_KEY),
        "sid_prefix": masked_sid,
        "sidts_prefix": masked_sidts,
        "proxy_enabled": bool(CLASH_PROXIES),
        "proxy_info": proxy_info,
    }

@app.get("/v1/models")
async def list_models():
    models = []
    for m in Model:
        try:
            models.append({
                "id": m.model_name,
                "object": "model",
                "owned_by": "google-gemini-web",
            })
        except Exception:
            continue
    return {"object": "list", "data": models}

@app.post("/v1/chat/completions")
async def create_chat_completion(request: ChatCompletionRequest, _: None = Depends(verify_api_key)):
    client = await get_gemini_client()

    # Prepare conversation and files
    conversation, temp_files = prepare_conversation(request.messages)

    # Select model
    model = map_model_name(request.model)

    try:
        # Generate response
        if temp_files:
            resp = await client.generate_content(conversation, files=temp_files, model=model)
        else:
            resp = await client.generate_content(conversation, model=model)
    finally:
        # Clean up temp files
        for f in temp_files:
            try:
                os.unlink(f)
            except Exception:
                pass

    # Compose reply text
    reply_text = ""
    if ENABLE_THINKING and getattr(resp, "thoughts", None):
        reply_text += f"{resp.thoughts}"
    if getattr(resp, "text", None):
        reply_text += resp.text
    else:
        reply_text += str(resp)

    reply_text = reply_text.replace("\\_", "_")

    completion_id = f"chatcmpl-{uuid.uuid4()}"
    created_ts = int(time.time())

    if request.stream:
        async def event_stream():
            # Initial role chunk
            start_chunk = {
                "id": completion_id,
                "object": "chat.completion.chunk",
                "created": created_ts,
                "model": request.model,
                "choices": [{"index": 0, "delta": {"role": "assistant"}, "finish_reason": None}],
            }
            yield f"data: {json.dumps(start_chunk)}\n\n"
            # Stream content char by char (simple simulation)
            for ch in reply_text:
                chunk = {
                    "id": completion_id,
                    "object": "chat.completion.chunk",
                    "created": created_ts,
                    "model": request.model,
                    "choices": [{"index": 0, "delta": {"content": ch}, "finish_reason": None}],
                }
                yield f"data: {json.dumps(chunk)}\n\n"
                await asyncio.sleep(0.005)
            # End chunk
            end_chunk = {
                "id": completion_id,
                "object": "chat.completion.chunk",
                "created": created_ts,
                "model": request.model,
                "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}],
            }
            yield f"data: {json.dumps(end_chunk)}\n\n"
            yield "data: [DONE]\n\n"
        return StreamingResponse(event_stream(), media_type="text/event-stream")

    # Non-streaming result
    result = {
        "id": completion_id,
        "object": "chat.completion",
        "created": created_ts,
        "model": request.model,
        "choices": [{
            "index": 0,
            "message": {"role": "assistant", "content": reply_text},
            "finish_reason": "stop",
        }],
        "usage": {
            "prompt_tokens": len(conversation.split()),
            "completion_tokens": len(reply_text.split()),
            "total_tokens": len(conversation.split()) + len(reply_text.split()),
        },
    }
    return result

