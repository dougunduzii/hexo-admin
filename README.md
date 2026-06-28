# Hexo Blog Admin

> 🤖 **AI 生成声明**：本项目由 AI（Claude Code）辅助生成，包括但不限于代码编写、文档撰写和项目结构设计。使用者请根据实际需求审阅和调整代码。

基于 **Vue3 + FastAPI + SQLite** 的 Hexo 博客后台管理系统，支持文章管理、主题配置、图片管理、一键部署。

## 功能总览

| 功能 | 路由 | 说明 |
|------|------|------|
| 📊 **仪表盘** | `/`  | 文章/分类/标签统计，文件同步，一键部署 |
| 📄 **文章管理** | `/posts` | 文章列表、搜索、分页、创建、编辑、删除 |
| ✏️ **文章编辑器** | `/posts/new` / `/posts/:id/edit` | Markdown 编辑 + 实时预览 + 图片插入 |
| ⚙️ **网站设置** | `/settings` | 可视化编辑 Butterfly 主题配置 |
| 🖼️ **图片管理** | `/images` | 浏览、上传、删除、灯箱预览、复制路径 |
| 🔐 **认证登录** | `/login` | HMAC 签名 Token，24 小时过期 |

## 页面截图

### 🖼️ 图片管理 — 灯箱预览
- 全屏黑色灯箱，键盘 ← → 切换，Esc 关闭
- 点击图片 1.8x 缩放，支持复制 URL / Markdown

### ⚙️ 网站设置（5 个 Tab）
| Tab | 可配置项 |
|-----|---------|
| 🎨 外观 | 背景图、横幅、头像、favicon、主题颜色、显示模式 |
| 📋 导航 | 导航菜单项增删改（名称、链接、图标） |
| 🏠 首页 | 副标题、布局列数、摘要字数 |
| 📌 侧边栏 | 公告、最新文章、标签云、归档等卡片开关 |
| 📃 页脚 | 建站年份、版权信息 |

### ✏️ 文章编辑器
- 编辑工具栏：粗体、斜体、代码、链接、代码块
- 🖼️ 图片插入面板（从博客图片库选择）
- Markdown 实时预览（含 XSS 净化）

## 项目结构

```
hexo-admin/
├── backend/                       # FastAPI 后端
│   ├── main.py                    # API 路由入口
│   ├── auth.py                    # 管理员认证（HMAC-SHA256）
│   ├── crud.py                    # 数据库 CRUD 操作
│   ├── database.py                # SQLite 数据库配置
│   ├── hexo_utils.py              # Hexo .md 文件读写 + front matter 解析
│   ├── models.py                  # SQLAlchemy ORM 模型
│   ├── schemas.py                 # Pydantic 请求/响应模型
│   ├── settings_utils.py          # Butterfly YAML 配置读写 + 图片管理
│   ├── config.json                # 管理员密码（.gitignore 排除）
│   └── requirements.txt
├── frontend/                      # Vue3 前端
│   ├── src/
│   │   ├── api/index.js           # Axios 封装 + 认证拦截
│   │   ├── router/index.js        # 路由 + 导航守卫
│   │   ├── composables/useToast.js
│   │   ├── components/Sidebar.vue
│   │   └── views/
│   │       ├── Dashboard.vue      # 仪表盘
│   │       ├── PostList.vue       # 文章列表
│   │       ├── PostEditor.vue     # 文章编辑器
│   │       ├── Settings.vue       # 网站设置
│   │       ├── Images.vue         # 图片管理
│   │       └── Login.vue          # 登录页
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
├── deploy/
│   ├── nginx.conf                 # Nginx 配置参考
│   └── hexo-admin.service         # systemd 服务参考
├── .gitignore
└── README.md
```

## 技术栈

| 层 | 技术 |
|--|--|
| 前端 | Vue 3 (Composition API), Vue Router 4, Axios, Marked, DOMPurify |
| 后端 | FastAPI, SQLAlchemy, Pydantic, PyYAML |
| 数据库 | SQLite |
| 构建 | Vite |
| 认证 | HMAC-SHA256 签名 Token |

## 快速开始

### 1. 后端

```bash
cd backend
pip install -r requirements.txt

# 启动（开发模式）
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

首次启动会自动：
- 创建 SQLite 数据库
- 从 `../blog-hexo/source/_posts/` 同步文章

### 2. 前端

```bash
cd frontend
npm install
npm run dev          # 开发模式（代理 API 到 8000）
# 或
npm run build        # 生产构建
```

### 3. 访问

- 前端：`http://localhost:5173`
- API 文档：`http://localhost:8000/docs`

## 配置文件

### 管理员密码

```bash
# 方式一：config.json（推荐，热更新无需重启）
backend/config.json
{"admin_password": "你的密码"}

# 方式二：环境变量（优先级更高）
export ADMIN_PASSWORD=你的密码
```

### Hexo 博客路径

后端默认假设博客在 `../blog-hexo/` 目录，可通过环境变量指定：

```bash
export HEXO_BLOG_PATH=/path/to/blog-hexo
```

### CORS 域名

```bash
export ALLOWED_ORIGINS=https://yourdomain.com,http://localhost:5173
```

## API 端点

| 方法 | 端点 | 认证 | 说明 |
|------|------|------|------|
| POST | `/api/auth/login` | — | 登录获取 Token |
| GET | `/api/auth/check` | — | 检查 Token 有效期 |
| GET | `/api/health` | — | 健康检查 |
| GET | `/api/stats` | — | 文章/分类/标签统计 |
| GET | `/api/posts` | — | 文章列表（分页+搜索） |
| GET | `/api/posts/{id}` | — | 文章详情 |
| POST | `/api/posts` | ✅ | 创建文章 |
| PUT | `/api/posts/{id}` | ✅ | 更新文章 |
| DELETE | `/api/posts/{id}` | ✅ | 删除文章 |
| POST | `/api/sync` | ✅ | 从文件系统同步 |
| POST | `/api/deploy` | ✅ | 一键 hexo g -d |
| GET | `/api/settings` | ✅ | 读取 Butterfly 配置 |
| PUT | `/api/settings` | ✅ | 部分更新配置 |
| GET | `/api/images?dir=` | — | 列出图片 |
| POST | `/api/images/upload` | ✅ | 上传图片 |
| DELETE | `/api/images` | ✅ | 删除图片 |
| GET | `/api/images/file` | — | 获取图片文件 |

> 标记 ✅ 的接口需要 `Authorization: Bearer <token>` 请求头

## 部署参考

### Nginx

```nginx
location /admin {
    alias /path/to/frontend/dist;
    index index.html;
    try_files $uri $uri/ /admin/index.html;
}

location /api {
    proxy_pass http://127.0.0.1:8000;
    proxy_read_timeout 120s;
}
```

### systemd

参考 `deploy/hexo-admin.service`，修改路径后启用：

```bash
cp deploy/hexo-admin.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now hexo-admin
```

## 安全说明

- 密码存储在 `backend/config.json`（已被 `.gitignore` 排除）
- Token 24 小时过期，HMAC-SHA256 签名
- 图片文件路径有目录穿越防护
- Nginx 层禁止直接访问敏感文件（`.json`、`.yaml`、`.db`）
- 写操作接口均需登录认证
