"""
John Locke 手稿转写平台 —— Django 配置。

采用前后端分离架构：Django + DRF 提供 REST API，Vue3 作为独立前端。
数据库使用 SQLite。手稿识别通过 Agnes AI（OpenAI 兼容接口）完成，
相关密钥请在项目根目录的 .env 文件或环境变量中配置。
"""
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# 从 backend/.env 读取环境变量（若存在）。
load_dotenv(BASE_DIR / ".env")


def env(key: str, default: str = "") -> str:
    return os.environ.get(key, default)


SECRET_KEY = env("DJANGO_SECRET_KEY", "dev-insecure-key-change-me-in-production")
DEBUG = env("DJANGO_DEBUG", "True").lower() == "true"
ALLOWED_HOSTS = [h for h in env("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",") if h]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # 第三方
    "rest_framework",
    "corsheaders",
    # 本项目应用
    "accounts",
    "manuscripts",
    "workspace",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "locke_platform.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "locke_platform.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "zh-hans"
TIME_ZONE = "Asia/Shanghai"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# Django REST Framework / JWT
# ---------------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 24,
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=12),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=14),
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# ---------------------------------------------------------------------------
# CORS —— 允许 Vite 前端开发服务器访问
# ---------------------------------------------------------------------------
CORS_ALLOWED_ORIGINS = [
    o for o in env(
        "CORS_ALLOWED_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",") if o
]
CORS_ALLOW_CREDENTIALS = True

# ---------------------------------------------------------------------------
# Agnes AI 手稿识别接口配置
#   AGNES_API_KEY  ——  请在 .env 中填写你自己的密钥（此处留空）
#   AGNES_BASE_URL ——  OpenAI 兼容的接口基地址
#   AGNES_MODEL    ——  用于视觉识别的多模态模型名称
# ---------------------------------------------------------------------------
AGNES_API_KEY = env("AGNES_API_KEY", "")
AGNES_BASE_URL = env("AGNES_BASE_URL", "https://apihub.agnes-ai.com/v1")
AGNES_MODEL = env("AGNES_MODEL", "gpt-4o")
AGNES_TIMEOUT = int(env("AGNES_TIMEOUT", "120"))
AGNES_PROMPT = env(
    "AGNES_PROMPT",
    (
        "You are an expert palaeographer specialising in the handwriting of "
        "John Locke (1632–1704). Transcribe the handwritten text in this "
        "manuscript image faithfully into modern printed characters. Preserve "
        "the original spelling, punctuation and line order as far as possible. "
        "Output only the transcription, with no commentary."
    ),
)
