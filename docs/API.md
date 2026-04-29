# RAG 智能问答系统 - API 接口文档

## 基础信息

- **Base URL**: `http://localhost:5000/api`
- **Content-Type**: `application/json`
- **认证方式**: 无（当前版本）

## 对话接口

### 1. 发送消息

**POST** `/chat`

发送用户消息并获取AI回复。

**Request Body:**
```json
{
  "message": "string (必需)",
  "session_id": "number (可选)",
  "knowledge_base_id": "number (可选)"
}
```

**Response:**
```json
{
  "answer": "string (AI回答)",
  "sources": [
    {
      "content": "string (相关片段)",
      "source": "string (来源文件)",
      "score": "number (相关性分数)"
    }
  ],
  "session_id": "number (会话ID)"
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "什么是RAG?", "knowledge_base_id": 1}'
```

---

### 2. 获取会话列表

**GET** `/chat/sessions`

**Query Parameters:**
| 参数 | 类型 | 描述 |
|------|------|------|
| knowledge_base_id | number | 可选，按知识库筛选 |

**Response:**
```json
{
  "sessions": [
    {
      "id": 1,
      "title": "对话 2024-01-15 10:30",
      "knowledge_base_id": 1,
      "created_at": "2024-01-15T10:30:00",
      "updated_at": "2024-01-15T10:35:00"
    }
  ]
}
```

---

### 3. 创建新会话

**POST** `/chat/sessions`

**Request Body:**
```json
{
  "title": "string (可选)",
  "knowledge_base_id": "number (可选)"
}
```

**Response:**
```json
{
  "session_id": 1,
  "message": "Session created"
}
```

---

### 4. 获取会话详情

**GET** `/chat/sessions/{session_id}`

**Response:**
```json
{
  "session": {
    "id": 1,
    "title": "对话 2024-01-15 10:30",
    "knowledge_base_id": 1,
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-15T10:35:00"
  }
}
```

---

### 5. 获取聊天历史

**GET** `/chat/history/{session_id}`

**Response:**
```json
{
  "messages": [
    {
      "id": 1,
      "session_id": 1,
      "role": "user",
      "content": "用户消息",
      "sources": "[]",
      "created_at": "2024-01-15T10:30:00"
    },
    {
      "id": 2,
      "session_id": 1,
      "role": "assistant",
      "content": "AI回复",
      "sources": "[{\"content\": \"...\", \"source\": \"doc.pdf\", \"score\": 0.95}]",
      "created_at": "2024-01-15T10:30:05"
    }
  ]
}
```

---

### 6. 删除会话

**DELETE** `/chat/sessions/{session_id}`

**Response:**
```json
{
  "message": "Session deleted"
}
```

---

## 文档接口

### 1. 上传文档

**POST** `/documents/upload`

**Content-Type:** `multipart/form-data`

**Form Data:**
| 参数 | 类型 | 描述 |
|------|------|------|
| file | File | 必需，上传的文件 |
| knowledge_base_id | number | 必需，知识库ID |

**Response:**
```json
{
  "id": 1,
  "filename": "document.pdf",
  "file_size": 1024000,
  "status": "uploaded",
  "message": "Document uploaded successfully"
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/api/documents/upload \
  -F "file=@/path/to/document.pdf" \
  -F "knowledge_base_id=1"
```

---

### 2. 处理文档

**POST** `/documents/{doc_id}/process`

触发文档的向量化处理过程。

**Response:**
```json
{
  "id": 1,
  "status": "completed",
  "message": "Document processed successfully"
}
```

---

### 3. 获取文档列表

**GET** `/documents`

**Query Parameters:**
| 参数 | 类型 | 描述 |
|------|------|------|
| knowledge_base_id | number | 可选，按知识库筛选 |

**Response:**
```json
{
  "documents": [
    {
      "id": 1,
      "knowledge_base_id": 1,
      "filename": "document.pdf",
      "file_path": "/path/to/file",
      "file_size": 1024000,
      "file_type": "pdf",
      "status": "completed",
      "chunk_count": 50,
      "created_at": "2024-01-15T10:00:00",
      "processed_at": "2024-01-15T10:00:30"
    }
  ]
}
```

---

### 4. 获取单个文档

**GET** `/documents/{doc_id}`

**Response:**
```json
{
  "document": {
    "id": 1,
    "knowledge_base_id": 1,
    "filename": "document.pdf",
    "file_path": "/path/to/file",
    "file_size": 1024000,
    "file_type": "pdf",
    "status": "completed",
    "chunk_count": 50,
    "created_at": "2024-01-15T10:00:00",
    "processed_at": "2024-01-15T10:00:30"
  }
}
```

---

### 5. 删除文档

**DELETE** `/documents/{doc_id}`

**Response:**
```json
{
  "message": "Document deleted successfully"
}
```

---

## 知识库接口

### 1. 创建知识库

**POST** `/knowledge-bases`

**Request Body:**
```json
{
  "name": "string (必需)",
  "description": "string (可选)"
}
```

**Response:**
```json
{
  "id": 1,
  "name": "技术文档",
  "description": "技术文档知识库",
  "message": "Knowledge base created successfully"
}
```

---

### 2. 获取知识库列表

**GET** `/knowledge-bases`

**Response:**
```json
{
  "knowledge_bases": [
    {
      "id": 1,
      "name": "技术文档",
      "description": "技术文档知识库",
      "document_count": 5,
      "completed_count": 4,
      "created_at": "2024-01-15T10:00:00",
      "updated_at": "2024-01-15T10:00:00"
    }
  ]
}
```

---

### 3. 获取单个知识库

**GET** `/knowledge-bases/{kb_id}`

**Response:**
```json
{
  "knowledge_base": {
    "id": 1,
    "name": "技术文档",
    "description": "技术文档知识库",
    "document_count": 5,
    "completed_count": 4,
    "created_at": "2024-01-15T10:00:00",
    "updated_at": "2024-01-15T10:00:00"
  }
}
```

---

### 4. 删除知识库

**DELETE** `/knowledge-bases/{kb_id}`

会同时删除知识库中的所有文档和向量数据。

**Response:**
```json
{
  "message": "Knowledge base deleted successfully"
}
```

---

## 系统接口

### 1. 健康检查

**GET** `/health`

**Response:**
```json
{
  "status": "healthy",
  "database": "/path/to/database",
  "chroma_db": "/path/to/chroma"
}
```

---

### 2. 根路径

**GET** `/`

**Response:**
```json
{
  "name": "RAG 智能问答系统",
  "version": "1.0.0",
  "status": "running",
  "endpoints": {
    "chat": "/api/chat",
    "documents": "/api/documents",
    "knowledge_bases": "/api/knowledge-bases",
    "health": "/api/health"
  }
}
```

---

## 错误响应

所有接口的错误响应格式：

```json
{
  "error": "错误描述"
}
```

常见HTTP状态码：
- `200` - 成功
- `400` - 请求参数错误
- `404` - 资源不存在
- `413` - 文件过大
- `500` - 服务器内部错误
