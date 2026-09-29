# 阿里云部署指南 —— John Locke 手稿转写平台

本目录提供在**阿里云 ECS（香港/境外，免备案）**上以
**Nginx + Gunicorn + systemd** 原生方式部署本项目的配置与步骤。

## 架构

```
浏览器 → Nginx (80/443)
          ├── /         → 前端 dist/ 静态文件（vue-router history 回退 index.html）
          ├── /api/     → 反代 gunicorn (127.0.0.1:8000) → Django
          ├── /media/   → 直接托管 backend/media/（用户上传 + 导入的手稿图）
          └── /static/  → 托管 backend/staticfiles/（Django admin 用）
Django → 出站调用 OpenRouter API (openrouter.ai) 进行手稿识别
```

- 无本地 ML/GPU，识别为远程 API 转发 → **2核2G ECS 即可**，2核4G 更宽裕。
- 数据库为 SQLite（单文件 `backend/db.sqlite3`），单机低并发足够。
- 关键超时：识别同步调用 OpenRouter（默认 120s），故 gunicorn 与 nginx 超时均设为 300s。

## 本目录文件

| 文件 | 用途 | 服务器上位置 |
|---|---|---|
| `john-locke.service` | gunicorn 的 systemd 服务 | `/etc/systemd/system/john-locke.service` |
| `nginx-john-locke.conf` | Nginx 站点配置 | `/etc/nginx/sites-available/john-locke` |
| `env.production.example` | 生产 `.env` 模板 | 复制为 `backend/.env` |
| `update.sh` | 更新部署脚本（每次改代码后跑） | 就地运行 |

> 以下步骤假设：项目部署在 `/opt/john-locke`，运行用户为 `deploy`，域名为 `john-locke.ccwu.cc`。若不同，请同步修改上述文件里的路径/用户/域名。

---

## 一、购买与准备 ECS

1. **地域**：香港 或 其他境外地域（免 ICP 备案）。
2. **规格**：2核2G 起步（如 ecs.t6-c1m1.large 之类突发性能实例），预算够选 2核4G。
3. **系统**：Ubuntu 22.04 LTS（下述命令按此编写）。
4. **系统盘**：40GB ESSD/高效云盘（media 会增长）。
5. **带宽**：按量或固定 3Mbps（主要传图片）。
6. **安全组**：放行入方向 **22 / 80 / 443**；**不要**放行 8000（仅本机 nginx 反代）。
7. **DNS**：把 `john-locke.ccwu.cc` 的 A 记录解析到 ECS 公网 IP。

---

## 二、首次部署（在 ECS 上执行）

### 1. 基础环境

```bash
sudo apt update
sudo apt install -y python3-venv python3-pip nginx git curl
# Node.js 20（用于构建前端）
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
```

### 2. 创建运行用户与目录，拉取代码

```bash
# 若还没有 deploy 用户
sudo adduser --disabled-password --gecos "" deploy

sudo mkdir -p /opt/john-locke
sudo chown deploy:deploy /opt/john-locke

# 切到 deploy 用户操作
sudo -u deploy -H bash
git clone <你的仓库地址> /opt/john-locke
cd /opt/john-locke
```

> 若代码不通过 git 传输，也可用 `scp`/`rsync` 上传整个项目到 `/opt/john-locke`。
> **注意**：`backend/media/` 与 `db.sqlite3` 被 gitignore，不会随 git 传输。
> - 首次可不传 media，靠下方 `import_dataset` 重新生成系统手稿图（需要 `Locke_dataset/` 目录，它在仓库里）。
> - 若要保留本地已有的用户上传数据，用 rsync 单独同步 `backend/media/` 与 `backend/db.sqlite3`。

### 3. 后端：虚拟环境 + 依赖 + 数据

```bash
cd /opt/john-locke/backend
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt

# 配置生产环境变量
cp ../deploy/env.production.example .env
# 生成 SECRET_KEY：
.venv/bin/python -c "import secrets; print(secrets.token_urlsafe(64))"
# 编辑 .env：填入上一步的 SECRET_KEY、你的 RECOGNITION_API_KEY（OpenRouter），确认 DEBUG=False、域名正确
nano .env

# 迁移 + 导入手稿数据集 + 收集静态文件
.venv/bin/python manage.py migrate
.venv/bin/python manage.py import_dataset       # 生成系统手稿图到 media/manuscripts/
.venv/bin/python manage.py collectstatic --noinput
# 可选：创建管理员
.venv/bin/python manage.py createsuperuser
```

### 4. 前端：构建静态文件

```bash
cd /opt/john-locke/frontend
npm ci
npm run build      # 产物输出到 frontend/dist/
```

### 5. 注册 gunicorn 服务

```bash
sudo cp /opt/john-locke/deploy/john-locke.service /etc/systemd/system/john-locke.service
# 如目录/用户与默认不同，先编辑该文件
sudo systemctl daemon-reload
sudo systemctl enable --now john-locke
sudo systemctl status john-locke        # 应为 active (running)
```

允许 deploy 用户重启服务（供 update.sh 用），执行 `sudo visudo` 追加一行：

```
deploy ALL=(root) NOPASSWD: /bin/systemctl restart john-locke
```

### 6. 配置 Nginx

```bash
sudo cp /opt/john-locke/deploy/nginx-john-locke.conf /etc/nginx/sites-available/john-locke
sudo ln -s /etc/nginx/sites-available/john-locke /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default   # 移除默认站点
sudo nginx -t                                 # 语法检查
sudo systemctl reload nginx
```

此时用浏览器访问 `http://john-locke.ccwu.cc` 应能看到站点。

### 7. 启用 HTTPS（Let's Encrypt，免费）

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d john-locke.ccwu.cc
# certbot 会自动改写 nginx 配置：加 443、证书、并把 80 跳转到 443
```

启用 HTTPS 后，确认 `backend/.env` 里 `CORS_ALLOWED_ORIGINS=https://john-locke.ccwu.cc`，
然后 `sudo systemctl restart john-locke`。

---

## 三、日常更新

改完代码 push 后，在服务器上：

```bash
cd /opt/john-locke
./deploy/update.sh
```

## 四、排错

- 后端日志：`sudo journalctl -u john-locke -f`
- Nginx 错误日志：`sudo tail -f /var/log/nginx/error.log`
- 502 Bad Gateway → gunicorn 没起来，看 `systemctl status john-locke`
- 图片打不开（/media 404）→ 检查 nginx 里 `alias` 路径与 `backend/media/` 实际目录、及目录读权限
- 识别超时/499 → 确认 gunicorn `--timeout` 与 nginx `proxy_read_timeout` 都是 300s
- 前端刷新子路由 404 → 确认 nginx `try_files ... /index.html` 存在

## 五、备份

- 数据库：`backend/db.sqlite3`
- 用户上传：`backend/media/workspace/`（`manuscripts/` 可由 import_dataset 重建）
- 环境密钥：`backend/.env`

定期把这几项打包备份（可挂载阿里云 OSS 或定时 `tar` + 下载）。

## 六、整机迁移（自定义镜像）

把当前轻量应用服务器整机做成**自定义镜像**，用它开一台新的轻量服务器。
镜像会包含代码、venv、`db.sqlite3`、`media/`、`.env`、nginx/systemd 配置，
迁移后基本"开机即用"，只需处理域名/证书/IP 相关的少量配置。

### 1. 旧服务器：先让数据落盘

创建镜像前停掉写库服务，避免 SQLite 处于半写状态：

```bash
sudo systemctl stop john-locke
# 确认关键数据都在盘上：backend/db.sqlite3、backend/media/、backend/.env
```

### 2. 创建自定义镜像

阿里云 **轻量应用服务器控制台** → 选中当前实例 → **更多 / 镜像 → 创建自定义镜像**，
命名如 `john-locke-YYYYMMDD`，等待镜像状态变为「可用」。
（创建完可以先把旧实例 `sudo systemctl start john-locke` 恢复对外服务，等新机验证无误再释放。）

### 3. 用该镜像开新的轻量服务器

- **同地域（推荐，最简单）**：在香港地域新建轻量实例时，「镜像」处选
  **自定义镜像 → john-locke-YYYYMMDD** 即可。
- **跨地域**：轻量自定义镜像不能直接跨地域使用，需先在控制台把镜像**拷贝到目标地域**
  （或先「共享到 ECS 自定义镜像」再跨地域复制），完成后再用它开实例。若无特别原因，建议保持同地域。

### 4. 新机开机后校验

```bash
# 确认服务随开机自启（镜像已带 enable）
sudo systemctl status john-locke nginx
# 若未自启则手动拉起
sudo systemctl start john-locke
```

若新机换了公网 IP 或域名，编辑 `backend/.env` 并同步这几项，然后重启：

```bash
nano /opt/john-locke/backend/.env
#   DJANGO_ALLOWED_HOSTS   —— 新域名/IP
#   CORS_ALLOWED_ORIGINS   —— 新前端来源
#   RECOGNITION_SITE_URL   —— 新站点 URL（OpenRouter 归属头，可选）
sudo systemctl restart john-locke
```

### 5. 切流量与证书

- 把域名 `john-locke.ccwu.cc` 的 A 记录解析到**新实例公网 IP**。
- 证书二选一：
  - 新机重新申请：`sudo certbot --nginx -d john-locke.ccwu.cc`；
  - 或从旧机迁移整个 `/etc/letsencrypt/` 目录后 `sudo systemctl reload nginx`。
- **安全组**：新实例放行入方向 **22 / 80 / 443**，**不要**放行 8000。

### 6. 验证后再释放旧机

浏览器访问站点 → 登录 → 上传一张手稿触发识别，确认识别（OpenRouter）、
手稿库浏览与跳页均正常后，再释放旧实例。

> 若担心「创建镜像」时点与「新机上线」之间旧机又产生了新数据（新用户上传/新识别），
> 可在新机上线后，从旧机单独 rsync 一次增量：
> ```bash
> rsync -avz deploy@<旧机IP>:/opt/john-locke/backend/media/ /opt/john-locke/backend/media/
> rsync -avz deploy@<旧机IP>:/opt/john-locke/backend/db.sqlite3 /opt/john-locke/backend/db.sqlite3
> sudo systemctl restart john-locke
> ```
