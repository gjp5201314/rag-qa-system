# RAG智能问答系统 - 项目架构文档

## 1. 系统架构图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           RAG 智能问答系统架构                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────────┐         ┌──────────────────────────────────────┐ │
│  │                  │         │              后端服务层                 │ │
│  │    React 前端     │◄───────►│  ┌─────────────┐  ┌────────────────┐ │ │
│  │    (现代化UI)     │ HTTP    │  │  Flask API  │  │  Waitress WSGI │ │ │
│  │                  │  JSON   │  └──────┬──────┘  └───────┬────────┘ │ │
│  └──────────────────┘         │         │                  │          │ │
│                               │  ┌──────▼──────────────────▼────────┐  │ │
│                               │  │         业务逻辑层 (Services)      │  │ │
│                               │  │  ┌─────────┐ ┌────────────────┐  │  │ │
│                               │  │  │文档服务  │ │  对话服务       │  │  │ │
│                               │  │  │Document │ │  ChatService   │  │  │ │
│                               │  │  │Service  │ │                │  │  │ │
│                               │  │  └────┬────┘ └───────┬────────┘  │  │ │
│                               │  └───────┼──────────────┼───────────┘  │ │
│                               │          │              │              │ │
│                               │  ┌───────▼──────────────▼───────────┐  │ │
│                               │  │           RAG 核心引擎              │  │ │
│                               │  │  ┌────────┐ ┌─────────────────┐  │  │ │
│                               │  │  │文档处理 │ │   混合检索引擎    │  │  │ │
│                               │  │  │Pipeline│ │HybridSearch      │  │  │ │
│                               │  │  └────┬───┘ └────────┬────────┘  │  │ │
│                               │  │       │              │           │  │ │
│                               │  │  ┌────▼────────────────▼─────┐   │  │ │
│                               │  │  │  向量数据库 (Chroma)        │   │  │ │
│                               │  │  │  + BM25 混合检索           │   │  │ │
│                               │  │  │  + Rerank 重排序          │   │  │ │
│                               │  │  └───────────────────────────┘   │  │ │
│                               │  └───────────────────────────────────┘  │ │
│                               └──────────────────────────────────────┘ │
│                                          │                              │
│  ┌──────────────────┐         ┌──────────▼───────────────────────────┐ │
│  │   LLM API       │◄────────│         大模型层                      │ │
│  │  (通义千问/豆包)  │         │  ┌─────────┐ ┌─────────────────────┐ │ │
│  └──────────────────┘         │  │Embedding│ │   LLM Generation    │ │ │
│                               │  │  BGE    │ │   (Qwen/Doubao)     │ │ │
│                               │  └─────────┘ └─────────────────────┘ │ │
│                               └──────────────────────────────────────┘ │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                        数据持久化层                                 │  │
│  │  ┌─────────────────┐        ┌─────────────────────────────────┐  │  │
│  │  │  SQLite 数据库   │        │       Chroma 向量存储            │  │  │
│  │  │  - 用户对话记录  │        │       - 文档向量索引             │  │  │
│  │  │  - 知识库元数据  │        │       - 分块向量                 │  │  │
│  │  │  - 会话历史     │        │       - 元数据存储               │  │  │
│  │  └─────────────────┘        └─────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## 2. 项目目录结构

```
RAGLearn/
├── backend/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── chat.py           # 对话相关API
│   │   ├── document.py       # 文档管理API
│   │   └── knowledge_base.py # 知识库管理API
│   ├── models/
│   │   ├── __init__.py
│   │   ├── database.py       # SQLite数据库模型
│   │   └── schemas.py       # Pydantic数据模型
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── chunker.py        # 智能文本分块
│   │   ├── embedder.py       # BGE嵌入向量生成
│   │   ├── hybrid_search.py  # 混合检索(向量+BM25)
│   │   ├── reranker.py       # Rerank重排序
│   │   └── document_processor.py # 文档解析处理
│   ├── services/
│   │   ├── __init__.py
│   │   ├── chat_service.py   # 对话服务
│   │   ├── document_service.py # 文档服务
│   │   └── llm_service.py    # LLM调用服务
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── config.py         # 配置文件
│   │   └── logger.py         # 日志工具
│   ├── app.py                # Flask应用入口
│   ├── requirements.txt      # Python依赖
│   └── run.py                # 启动脚本
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatMessage.jsx      # 聊天消息组件
│   │   │   ├── ChatInput.jsx        # 聊天输入组件
│   │   │   ├── DocumentList.jsx     # 文档列表组件
│   │   │   ├── KnowledgeBaseSelector.jsx # 知识库选择器
│   │   │   └── FileUpload.jsx       # 文件上传组件
│   │   ├── pages/
│   │   │   ├── HomePage.jsx         # 首页
│   │   │   ├── ChatPage.jsx         # 对话页面
│   │   │   └── AdminPage.jsx        # 管理页面
│   │   ├── services/
│   │   │   └── api.js               # API调用服务
│   │   ├── store/
│   │   │   └── index.js             # 状态管理
│   │   ├── styles/
│   │   │   └── App.css              # 全局样式
│   │   ├── App.jsx                  # 根组件
│   │   └── main.jsx                 # 入口文件
│   ├── package.json
│   ├── vite.config.js
│   └── index.html
├── data/
│   ├── knowledge_bases/       # 原始文档存储
│   └── chroma_db/            # Chroma向量数据库
├── docs/                      # 项目文档
│   ├── API.md                 # 接口文档
│   ├── DEPLOY.md              # 部署指南
│   └── INTERVIEW.md           # 面试介绍
├── logs/                      # 日志文件
└── README.md                  # 项目说明
```

## 3. 技术栈详情

### 后端技术栈
| 技术 | 用途 | 特点 |
|------|------|------|
| Flask | Web框架 | 轻量、灵活、易扩展 |
| Waitress | WSGI服务器 | 生产级、高性能、跨平台 |
| LangChain | RAG编排 | 模块化、.chain()链式调用 |
| BGE Embedding | 向量化模型 | 中文优化、高精度 |
| Chroma DB | 向量数据库 | 轻量、无服务器、易部署 |
| SQLite | 关系数据库 | 零配置、文件型、无需服务 |
| BM25 | 关键词检索 | 成熟的稀疏检索算法 |
| BGE Reranker | 重排序 | 提升检索精度 |

### 前端技术栈
| 技术 | 用途 | 特点 |
|------|------|------|
| React 18 | UI框架 | 组件化、生态丰富 |
| Axios | HTTP客户端 | Promise化、易使用 |
| Vite | 构建工具 | 快速热更新 |
| CSS Variables | 样式主题 | 统一管理、动态切换 |

## 4. RAG 流程图

```
用户问题
    │
    ▼
┌─────────────────┐
│  文本向量化       │ ◄── BGE Embedding
│  (Embedding)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────┐
│  向量相似度检索   │     │   BM25 检索      │
│  (Chroma DB)    │     │  (关键词匹配)     │
└────────┬────────┘     └────────┬────────┘
         │                       │
         └───────────┬───────────┘
                     ▼
          ┌─────────────────────┐
          │     混合检索融合      │
          │   (Hybrid Search)   │
          └──────────┬──────────┘
                     │
                     ▼
          ┌─────────────────────┐
          │     Rerank 重排序    │
          │   (BGE Reranker)    │
          └──────────┬──────────┘
                     │
                     ▼
          ┌─────────────────────┐
          │   构建Prompt模板     │
          │  (Context + Query)  │
          └──────────┬──────────┘
                     │
                     ▼
          ┌─────────────────────┐
          │    调用 LLM API      │
          │ (通义千问/豆包)       │
          └──────────┬──────────┘
                     │
                     ▼
                 生成回答
```

## 5. 数据库表结构

### SQLite 表设计

```sql
-- 知识库表
CREATE TABLE knowledge_bases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 文档表
CREATE TABLE documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    knowledge_base_id INTEGER NOT NULL,
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(512) NOT NULL,
    file_size INTEGER,
    file_type VARCHAR(50),
    status VARCHAR(50) DEFAULT 'pending',
    chunk_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP,
    FOREIGN KEY (knowledge_base_id) REFERENCES knowledge_bases(id)
);

-- 对话会话表
CREATE TABLE chat_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(255),
    knowledge_base_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (knowledge_base_id) REFERENCES knowledge_bases(id)
);

-- 聊天消息表
CREATE TABLE chat_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    role VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    sources TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES chat_sessions(id)
);
```

## 6. API 接口规范

### 对话接口
- `POST /api/chat` - 发送消息并获取回复
- `GET /api/chat/history/{session_id}` - 获取会话历史
- `GET /api/chat/sessions` - 获取所有会话列表

### 文档接口
- `POST /api/documents/upload` - 上传文档
- `GET /api/documents` - 获取文档列表
- `DELETE /api/documents/{id}` - 删除文档

### 知识库接口
- `POST /api/knowledge-bases` - 创建知识库
- `GET /api/knowledge-bases` - 获取知识库列表
- `DELETE /api/knowledge-bases/{id}` - 删除知识库

详见: [API.md](docs/API.md)

## 7. 部署架构

```
                    ┌─────────────────┐
                    │   用户浏览器     │
                    └────────┬────────┘
                             │
                             ▼
                 ┌─────────────────────────┐
                 │   Render/Vercel/HF      │
                 │   (免费托管平台)         │
                 │  ┌─────────────────┐   │
                 │  │  React Frontend │   │
                 │  └────────┬────────┘   │
                 │           │            │
                 │  ┌────────▼────────┐   │
                 │  │  Flask Backend  │   │
                 │  │   + Waitress    │   │
                 │  └────────┬────────┘   │
                 │           │            │
                 │  ┌────────▼────────┐   │
                 │  │   SQLite DB     │   │
                 │  │   Chroma DB     │   │
                 │  └─────────────────┘   │
                 └─────────────────────────┘
                             │
                             ▼
                 ┌─────────────────────────┐
                 │    通义千问/豆包 API      │
                 │    (国内免费LLM)         │
                 └─────────────────────────┘
```

## 8. 项目亮点

### 技术亮点
1. **混合检索策略**: 结合向量检索和BM25关键词检索，提升召回率
2. **Rerank重排序**: 使用BGE-Reranker对结果进行精细排序
3. **智能文本分块**: 基于语义的分块策略，保证上下文完整性
4. **流式输出**: 支持打字机效果的流式响应

### 工程亮点
1. **模块化设计**: 清晰的层次结构，便于维护扩展
2. **生产级部署**: 使用Waitress替代开发服务器
3. **日志规范**: 完整的日志记录和异常处理
4. **零成本部署**: 完全使用免费服务和数据库

### 面试亮点
1. RAG核心原理：Embedding、向量检索、混合检索
2. LLM应用架构：Prompt工程、上下文管理
3. 向量数据库原理：近似最近邻(ANN)、HNSW算法
4. 生产环境部署：WSGI服务器、高并发处理
