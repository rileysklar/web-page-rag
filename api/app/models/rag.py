"""
Pydantic models for RAG operations.
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, HttpUrl

class IndexingTask(BaseModel):
    """Model for tracking indexing tasks."""
    id: str
    url: str
    namespace: Optional[str] = None
    status: str
    progress: float = 0.0
    error: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class QueryRequest(BaseModel):
    """Model for query requests."""
    question: str
    namespace: Optional[str] = None
    model_name: Optional[str] = None
    temperature: Optional[float] = None

class QueryResponse(BaseModel):
    """Model for query responses."""
    answer: str
    sources: List[str]

class IndexRequest(BaseModel):
    """Model for index requests."""
    url: HttpUrl
    namespace: Optional[str] = None

class IndexResponse(BaseModel):
    """Model for index responses."""
    status: str
    message: str
    task_id: str

class IndexStatus(BaseModel):
    """Model for index status."""
    status: str
    progress: float
    message: str
    error: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None 