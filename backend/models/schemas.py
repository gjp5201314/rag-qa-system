from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class KnowledgeBaseCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = ""

class KnowledgeBaseResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    created_at: str
    updated_at: str

class DocumentResponse(BaseModel):
    id: int
    knowledge_base_id: int
    filename: str
    file_path: str
    file_size: int
    file_type: str
    status: str
    chunk_count: int
    created_at: str
    processed_at: Optional[str]

class ChatSessionCreate(BaseModel):
    title: Optional[str] = ""
    knowledge_base_id: Optional[int] = None

class ChatSessionResponse(BaseModel):
    id: int
    title: str
    knowledge_base_id: Optional[int]
    created_at: str
    updated_at: str

class ChatMessageCreate(BaseModel):
    session_id: int
    content: str
    role: str = "user"

class ChatMessageResponse(BaseModel):
    id: int
    session_id: int
    role: str
    content: str
    sources: Optional[str]
    created_at: str

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    session_id: Optional[int] = None
    knowledge_base_id: Optional[int] = None

class ChatResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]] = []
    session_id: int
    message_id: int

class UploadResponse(BaseModel):
    id: int
    filename: str
    status: str
    message: str

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
