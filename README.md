# RAG 智能问答系统

一个基于检索增强生成（RAG）技术的智能问答全栈项目，支持文档上传、知识库管理、智能问答。

## 项目简介

本项目是一个**工业级、可部署**的 RAG 智能问答系统，采用前后端分离架构：

- **前端**：React 现代化 UI
- **后端**：Python Flask + Waitress
- **数据库**：SQLite（零配置、无需服务）
- **向量数据库**：Chroma（轻量级向量存储）
- **Embedding**：BGE 中文模型
- **LLM**：通义千问 / 豆包 API

## 核心功能

- 📚 **多知识库管理**：创建和管理多个知识库
- 📄 **文档上传**：支持 PDF、TXT、Markdown、DOC 格式
- 🔍 **混合检索**：向量检索 + BM25 关键词检索
- 🎯 **Rerank 重排序**：BGE-Reranker 精细排序
- 💬 **智能对话**：基于文档内容的精准问答
- 📊 **来源追溯**：每个回答可查看参考片段

## 项目架构

```
RAGLearn/
├── backend/              # Flask 后端
│   ├── api/             # API 路由
│   ├── models/          # 数据模型
│   ├── rag/             # RAG 核心引擎
│   │   ├── document_processor.py   # 文档处理
│   │   ├── embedder.py            # BGE 向量化
│   │   ├── vector_store.py        # Chroma 存储
│   │   ├── bm25.py               # BM25 检索
│   │   └── reranker.py           # 重排序
│   ├── services/        # 业务逻辑
│   ├── utils/           # 工具模块
│   ├── app.py          # 应用入口
│   └── run.py          # 启动脚本
├── frontend/            # React 前端
│   ├── src/
│   │   ├── components/ # UI 组件
│   │   ├── pages/      # 页面
│   │   ├── services/   # API 调用
│   │   └── store/      # 状态管理
│   └── package.json
├── docs/               # 项目文档
│   ├── ARCHITECTURE.md # 架构文档
│   ├── API.md         # 接口文档
│   ├── DEPLOY.md      # 部署指南
│   └── INTERVIEW.md   # 面试介绍
└── data/               # 数据存储
    ├── knowledge_bases/    # 原始文档
    └── chroma_db/         # 向量数据库
```

## 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+
- 通义千问 API Key（免费申请）

### 后端启动

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
# 创建 .env 文件，添加：DASHSCOPE_API_KEY=your_api_key

# 启动服务
python run.py
```

后端运行在 http://localhost:5000

### 前端启动

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端运行在 http://localhost:3000

## 免费部署

项目支持部署到以下免费平台：

- **Render**（推荐）：完整支持 Python 后端
- **Hugging Face Spaces**：支持 Docker 部署
- **Railway**：$5 免费额度

详细部署步骤请参考 [部署指南](docs/DEPLOY.md)。

## RAG 技术亮点

### 1. 混合检索策略

```
向量检索 (语义相似)
    +
BM25 检索 (关键词匹配)
    ↓
分数融合 (α=0.7)
    ↓
Rerank 重排序
```

### 2. 智能文本分块

- 基于句子边界切分，保证语义完整
- 相邻块保留重叠上下文，避免信息丢失
- 可配置块大小和重叠大小

### 3. 级联检索架构

```
用户查询
    ↓
Embedding 向量化
    ↓
HNSW 向量检索 (O(log n))
    ↓
BM25 关键词检索
    ↓
混合分数融合
    ↓
Rerank 精细排序
    ↓
Top-K 结果
```

## 项目文档

- [架构文档](docs/ARCHITECTURE.md) - 详细的系统架构说明
- [接口文档](docs/API.md) - API 接口规范
- [部署指南](docs/DEPLOY.md) - 免费公网部署教程
- [面试介绍](docs/INTERVIEW.md) - 面试级项目解析

## 技术栈

### 后端

| 技术 | 用途 |
|------|------|
| Flask | Web 框架 |
| Waitress | 生产级 WSGI 服务器 |
| Chroma | 向量数据库 |
| BGE | 中文 Embedding |
| LangChain | RAG 编排 |
| SQLite | 关系数据库 |
| BM25 | 关键词检索 |

### 前端

| 技术 | 用途 |
|------|------|
| React 18 | UI 框架 |
| Axios | HTTP 客户端 |
| Vite | 构建工具 |

## 面试亮点

1. **RAG 核心原理**：Embedding、向量检索、混合检索、Rerank
2. **系统设计能力**：模块化架构、服务分离
3. **工程实践**：日志规范、异常处理、配置管理
4. **生产部署**：多平台部署、跨域配置

## License

MIT License
