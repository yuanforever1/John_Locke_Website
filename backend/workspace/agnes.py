"""
Agnes AI 手稿识别服务封装。

Agnes AI 提供与 OpenAI 兼容的多模态接口。此模块把一张手稿图片编码为
base64 data-url，连同转写提示词一起发送到 chat/completions 接口，
取回识别出的文本。

API Key 通过 settings.AGNES_API_KEY 读取（默认留空，请在 .env 配置）。
"""
import base64
import mimetypes
from pathlib import Path

import requests
from django.conf import settings


class AgnesConfigError(RuntimeError):
    """未配置 API Key 等。"""


class AgnesAPIError(RuntimeError):
    """调用接口失败。"""


def _encode_image(path: Path) -> str:
    mime = mimetypes.guess_type(str(path))[0] or "image/png"
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{data}"


def transcribe_image(image_path: str) -> str:
    """调用 Agnes 识别单张图片，返回转写文本。"""
    api_key = (settings.AGNES_API_KEY or "").strip()
    if not api_key:
        raise AgnesConfigError(
            "尚未配置 Agnes API Key，请在 backend/.env 中设置 AGNES_API_KEY。"
        )

    path = Path(image_path)
    if not path.exists():
        raise AgnesAPIError(f"图片文件不存在：{image_path}")

    endpoint = settings.AGNES_BASE_URL.rstrip("/") + "/chat/completions"
    payload = {
        "model": settings.AGNES_MODEL,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": settings.AGNES_PROMPT},
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

    try:
        resp = requests.post(
            endpoint,
            json=payload,
            headers=headers,
            timeout=settings.AGNES_TIMEOUT,
        )
    except requests.RequestException as exc:
        raise AgnesAPIError(f"请求 Agnes 接口失败：{exc}") from exc

    if resp.status_code != 200:
        raise AgnesAPIError(
            f"Agnes 接口返回 {resp.status_code}：{resp.text[:500]}"
        )

    try:
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()
    except (ValueError, KeyError, IndexError, TypeError) as exc:
        raise AgnesAPIError(f"无法解析 Agnes 响应：{exc}") from exc
