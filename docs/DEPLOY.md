# RAG 智能问答系统 - 免费公网部署指南

本指南详细说明如何将 RAG 智能问答系统部署到免费的公网平台，让他人可以访问。

## 部署方案概览

| 平台 | 免费额度 | 前端 | 后端 | 数据库 | 适配度 |
|------|---------|------|------|--------|--------|
| **Render** | 750小时/月 | ✅ | ✅ | ✅ SQLite | ⭐⭐⭐⭐⭐ |
| **Vercel** | 无限 | ✅ | ❌ 需要适配 | ❌ | ⭐⭐ |
| **Hugging Face** | 无限 | ✅ | ✅ | ⚠️ 有限 | ⭐⭐⭐⭐ |
| **Railway** | $5/月 | ✅ | ✅ | ✅ | ⭐⭐⭐⭐ |

**推荐方案：Render** - 对 Python 后端支持最好

---

## 方案一：Render 部署（推荐）

Render 提供完整的 Python/Node.js 支持，适合本项目的 Flask 后端 + React 前端架构。

### 前置准备

1. **GitHub 账号** - 代码需要托管在 GitHub
2. **Render 账号** - 使用 GitHub 登录 https://render.com
3. **通义千问 API Key** - 免费额度申请 https://dashscope.console.aliyun.com

### 第一步：准备代码

1. 创建 GitHub 仓库并上传代码：

```bash
cd RAGLearn
git init
git add .
git commit -m "Initial commit - RAG System"
git branch -M main
git remote add origin https://github.com/你的用户名/rag-system.git
git push -u origin main
```

2. 创建 `backend/render.yaml` 部署配置文件：

```yaml
# backend/render.yaml
services:
  - type: web
    name: rag-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python run.py
    healthCheckPath: /api/health
    plan: free
    envVars:
      - key: FLASK_ENV
        value: production
      - key: DEBUG
        value: false
      - key: DASHSCOPE_API_KEY
        sync: false
```

3. 创建 `frontend/vite.config.js` 的生产配置：

```javascript
// frontend/vite.config.js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: '/',
  build: {
    outDir: 'dist',
    base: '/'
  },
  server: {
    proxy: {
      '/api': {
        target: process.env.API_URL || 'http://localhost:5000',
        changeOrigin: true
      }
    }
  }
})
```

### 第二步：部署后端

1. 登录 Render Dashboard，点击 **"New +"** → **"Web Service"**
2. 连接 GitHub 仓库
3. 配置服务：
   - **Name**: `rag-api`
   - **Region**: Singapore (离中国近)
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python run.py`
4. 添加环境变量：
   - `FLASK_ENV`: `production`
   - `DEBUG`: `false`
   - `DASHSCOPE_API_KEY`: 你的API密钥
5. 点击 **"Create Web Service"** 开始部署

### 第三步：部署前端

1. 在 Render 创建 **"Static Site"**
2. 连接同一个 GitHub 仓库
3. 配置：
   - **Name**: `rag-frontend`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`
4. 添加环境变量：
   - `API_URL`: `https://rag-api.onrender.com` (后端服务URL)
5. 部署完成后，访问 `https://rag-frontend.onrender.com`

### 第四步：配置跨域

后端默认已配置 CORS，如需修改，在 Render 环境变量中添加：

```
CORS_ORIGINS=https://rag-frontend.onrender.com
```

---

## 方案二：Hugging Face Spaces 部署

Hugging Face Spaces 提供免费的 GPU 和无服务器部署。

### 部署步骤

1. 创建 Hugging Face 账号：https://huggingface.co

2. 创建新 Space：
   - 点击 **"Create new Space"**
   - 选择 **"Docker"** 模板（需要完整 Linux 环境）
   - 选择 **"Blank"** Docker image

3. 创建 `Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .
COPY frontend/dist ./frontend/dist

ENV PORT=7860
ENV FLASK_ENV=production

EXPOSE 7860

CMD ["python", "run.py"]
```

4. 创建 `README.md` 在 Space 根目录：

```yaml
---
title: RAG QA System
emoji: 🤖
colorFrom: purple
colorTo: blue
sdk: docker
app_port: 7860
---

# RAG 智能问答系统
```

5. 上传代码到 Space 仓库

6. 等待 Docker 镜像构建（约10-15分钟）

---

## 方案三：本地开发调试

### 环境要求

- Python 3.10+
- Node.js 18+
- npm 或 yarn

### 后端启动

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 启动服务
python run.py
```

后端服务将在 http://localhost:5000 启动。

### 前端启动

```bash
cd frontend

# 安装依赖
npm install

# 开发模式启动
npm run dev
```

前端服务将在 http://localhost:3000 启动。

### 配置 API Key

在 `backend/.env` 文件中配置：

```env
DASHSCOPE_API_KEY=your_api_key_here
FLASK_ENV=development
DEBUG=true
```

---

## 常见问题排查

### 1. 文档处理失败

检查日志：
```bash
tail -f logs/rag_system_*.log
```

常见原因：
- 文件格式不支持
- 文件过大（超过50MB）
- 文档内容为空

### 2. 向量检索无结果

可能原因：
- 文档未处理完成（状态不是 completed）
- 知识库为空
- embedding 模型未加载

### 3. API 调用失败

检查：
- CORS 配置是否正确
- API Key 是否有效
- 网络连接是否正常

### 4. 部署后样式丢失

前端 build 后需要正确配置：
- `vite.config.js` 的 `base` 路径
- 静态资源路径

---

## 环境变量参考

| 变量名 | 描述 | 默认值 | 必填 |
|--------|------|--------|------|
| `DASHSCOPE_API_KEY` | 通义千问API密钥 | - | 是 |
| `FLASK_ENV` | 运行环境 | development | 否 |
| `DEBUG` | 调试模式 | true | 否 |
| `PORT` | 服务端口 | 5000 | 否 |
| `CHUNK_SIZE` | 文本分块大小 | 500 | 否 |
| `TOP_K` | 检索数量 | 5 | 否 |
| `BGE_MODEL` | Embedding模型 | BAAI/bge-large-zh-v1.5 | 否 |

---

## 性能优化建议

### 1. 使用 GPU 加速

如果部署平台提供 GPU，可以显著加速 embedding 过程：

```python
# 在 embedder.py 中确保使用 GPU
import torch
device = "cuda" if torch.cuda.is_available() else "cpu"
```

### 2. 缓存机制

对于频繁检索的内容，可以添加 Redis 缓存：

```python
# 在 search 方法中添加缓存
from functools import lru_cache

@lru_cache(maxsize=1000)
def cached_search(query, kb_id):
    return search(query, kb_id)
```

### 3. 异步处理

文档处理可以使用异步任务队列：

```python
# 使用 Celery 进行异步处理
from celery import Celery

celery_app = Celery('tasks', broker='redis://localhost:6379')

@celery_app.task
def process_document_async(doc_id, kb_id):
    doc_service.process_document(doc_id, kb_id)
```
