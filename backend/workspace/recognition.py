"""
手稿识别服务封装（OpenRouter，OpenAI 兼容接口）。

OpenRouter 提供与 OpenAI 兼容的多模态接口。此模块把一张手稿图片编码为
base64 data-url，连同转写提示词一起发送到 chat/completions 接口，
取回识别出的文本。默认使用 Google Gemini 视觉模型。

API Key 通过 settings.RECOGNITION_API_KEY 读取（默认留空，请在 .env 配置）。
"""
import base64
import mimetypes
from pathlib import Path

import requests
from django.conf import settings


class RecognitionConfigError(RuntimeError):
    """未配置 API Key 等。"""


class RecognitionAPIError(RuntimeError):
    """调用接口失败。"""


def _encode_image(path: Path) -> str:
    mime = mimetypes.guess_type(str(path))[0] or "image/png"
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{data}"


def transcribe_image(image_path: str) -> str:
    """调用 OpenRouter 识别单张图片，返回转写文本。"""
    api_key = (settings.RECOGNITION_API_KEY or "").strip()
    if not api_key:
        raise RecognitionConfigError(
            "尚未配置识别接口 API Key，请在 backend/.env 中设置 RECOGNITION_API_KEY。"
        )

    path = Path(image_path)
    if not path.exists():
        raise RecognitionAPIError(f"图片文件不存在：{image_path}")

    endpoint = settings.RECOGNITION_BASE_URL.rstrip("/") + "/chat/completions"
    payload = {
        "model": settings.RECOGNITION_MODEL,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": settings.RECOGNITION_PROMPT},
                    {
                        "type": "image_url",
                        "image_url": {"url": _encode_image(path)},
                    },
                ],
            }
        ],
        "temperature": 0,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    # OpenRouter 可选头：用于配额归属与在 openrouter.ai 上展示来源，留空则不发送。
    site_url = (settings.RECOGNITION_SITE_URL or "").strip()
    if site_url:
        headers["HTTP-Referer"] = site_url
    site_name = (settings.RECOGNITION_SITE_NAME or "").strip()
    if site_name:
        headers["X-Title"] = site_name

    try:
        resp = requests.post(
            endpoint,
            json=payload,
            headers=headers,
            timeout=settings.RECOGNITION_TIMEOUT,
        )
    except requests.RequestException as exc:
        raise RecognitionAPIError(f"请求识别接口失败：{exc}") from exc

    if resp.status_code != 200:
        raise RecognitionAPIError(
            f"识别接口返回 {resp.status_code}：{resp.text[:500]}"
        )

    try:
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()
    except (ValueError, KeyError, IndexError, TypeError) as exc:
        raise RecognitionAPIError(f"无法解析识别接口响应：{exc}") from exc
