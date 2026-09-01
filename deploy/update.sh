#!/usr/bin/env bash
# ============================================================
# John Locke 平台 —— 更新部署脚本（在服务器上运行）
# 用于「首次完成初始化后」的每次代码更新。
# 首次部署请先按 deploy/ 说明手动完成环境准备。
#
# 用法： cd /opt/john-locke && ./deploy/update.sh
# ============================================================
set -euo pipefail

# 项目根目录（脚本所在目录的上一级）
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND="$ROOT/backend"
FRONTEND="$ROOT/frontend"
VENV="$BACKEND/.venv"

echo "==> [1/6] 拉取最新代码"
git -C "$ROOT" pull --ff-only

echo "==> [2/6] 更新后端依赖"
"$VENV/bin/pip" install -r "$BACKEND/requirements.txt"

echo "==> [3/6] 数据库迁移"
"$VENV/bin/python" "$BACKEND/manage.py" migrate --noinput

echo "==> [4/6] 收集静态文件"
"$VENV/bin/python" "$BACKEND/manage.py" collectstatic --noinput

echo "==> [5/6] 构建前端"
cd "$FRONTEND"
npm ci
npm run build

echo "==> [6/6] 重启后端服务"
sudo systemctl restart john-locke

echo "==> 完成。查看状态： sudo systemctl status john-locke"
