# 约翰·洛克手写体识别平台 · John Locke Manuscript Atelier

面向数字人文研究的洛克手稿转写与识别平台。前后端分离：**Django + DRF** 提供 REST API，**Vue 3 + Vite** 构建古典风格前端，数据库使用 **SQLite**，手稿识别通过 **Agnes AI**（OpenAI 兼容接口）完成。

---

## 一、功能概览

- **首页**：约翰·洛克的生平年表与传世著述（学术成就）介绍。
- **注册 / 登录**：基于 JWT 的用户认证。
- **系统手稿库**：浏览系统提供的洛克手稿集（法国旅行日记，含 126 页影像与官方转写 ground truth），支持全文检索、影像与转写对照阅读。
- **个人工作区**：每位用户拥有独立工作区，可
  - 新建 / 删除文件夹；
  - 向文件夹上传、删除手稿图片（支持拖拽与多选批量上传）；
  - 对图片进行**单张识别**或**批量识别**，查看识别转写结果。
- **个人主页**：维护昵称、头像、邮箱、机构与个人简介。

---

## 二、目录结构

```
John_Locke_Website/
├── Locke_dataset/            # 系统提供的手稿数据集（图片 + France_Pages.csv）
├── backend/                  # Django 后端
│   ├── locke_platform/       # 项目配置
│   ├── accounts/             # 用户档案与认证
│   ├── manuscripts/          # 系统手稿集 / 页 + 数据集导入命令
│   ├── workspace/            # 用户文件夹 / 图片 / 识别（含 Agnes 服务）
│   ├── requirements.txt
│   └── .env.example
└── frontend/                 # Vue3 前端
    └── src/
        ├── views/            # 页面
        ├── components/       # 页头 / 页脚
        ├── stores/           # Pinia 状态（认证）
        ├── api/              # axios 客户端
        └── assets/styles/    # 古典风格样式系统
```

---

## 三、数据模型与关系

| 应用 | 模型 | 说明 | 关系 |
| --- | --- | --- | --- |
| accounts | `Profile` | 用户档案（昵称/头像/邮箱/机构/简介） | 与内置 `User` **一对一**（用户创建时自动生成） |
| manuscripts | `Collection` | 系统手稿集 | 一个集合含多页 |
| manuscripts | `ManuscriptPage` | 手稿页（影像 + 官方转写 ground truth） | **多对一** → `Collection` |
| workspace | `Folder` | 用户工作区文件夹（支持嵌套） | **多对一** → `User`；`parent` 自引用 |
| workspace | `UserImage` | 用户上传的手稿图片 | **多对一** → `User`、`Folder` |
| workspace | `Recognition` | 一张图片的识别结果（状态/文本/模型/错误） | 与 `UserImage` **一对一** |

---

## 四、启动步骤

### 1. 后端（Django）

```powershell
cd backend
pip install -r requirements.txt

# 配置环境变量（可选，含 Agnes 密钥）
copy .env.example .env    # 然后编辑 .env

python manage.py migrate
python manage.py import_dataset        # 导入 Locke_dataset 手稿数据集
python manage.py createsuperuser       # 可选：创建后台管理员
python manage.py runserver 127.0.0.1:8000
```

后端运行于 `http://127.0.0.1:8000`，Django Admin 位于 `/admin/`。

### 2. 前端（Vue3）

```powershell
cd frontend
npm install
npm run dev
```

前端运行于 `http://localhost:5173`，已配置 `/api` 与 `/media` 代理到后端，直接访问即可。

---

## 五、配置 Agnes 识别接口

手稿识别使用 Agnes AI 的 OpenAI 兼容多模态接口。请在 `backend/.env` 中填写：

```
AGNES_API_KEY=你的密钥          # 默认留空，需自行填写
AGNES_BASE_URL=https://apihub.agnes-ai.com/v1
AGNES_MODEL=gpt-4o             # 具备视觉能力的模型名称
```

> 未配置密钥时，识别接口会返回明确的提示，其余功能不受影响。
> 识别逻辑封装于 `backend/workspace/agnes.py`，若接口约定不同，只需在此调整请求 / 解析方式。

---

## 六、主要 API 一览

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| POST | `/api/auth/register/` | 注册（返回用户与 JWT） |
| POST | `/api/auth/login/` | 登录获取 token |
| POST | `/api/auth/refresh/` | 刷新 access token |
| GET/PUT | `/api/auth/me/` | 读取 / 更新个人档案 |
| PUT | `/api/auth/me/avatar/` | 上传头像 |
| GET | `/api/collections/` | 系统手稿集列表 |
| GET | `/api/collections/{slug}/pages/` | 集合内手稿页（支持 `?search=`） |
| GET | `/api/pages/{id}/` | 手稿页详情（影像 + 转写） |
| GET/POST/DELETE | `/api/folders/` | 工作区文件夹 |
| GET/POST/DELETE | `/api/images/` | 工作区图片（`?folder=` 过滤，POST 支持多图） |
| POST | `/api/images/{id}/recognize/` | 单张识别 |
| POST | `/api/images/batch_recognize/` | 批量识别（body: `{"ids": [...]}`） |

---

## 七、技术栈

- 后端：Django 5、Django REST Framework、SimpleJWT、django-cors-headers、Pillow、requests
- 前端：Vue 3、Vite、Vue Router、Pinia、axios
- 数据库：SQLite
- 字体：Cormorant Garamond / EB Garamond / Noto Serif SC（衬线，营造古典人文质感）
