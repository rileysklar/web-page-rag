"""
Pydantic models for API requests and responses.
"""
from typing import List, Optional
from pydantic import BaseModel, Field

class ChatMessage(BaseModel):
    """A chat message model."""
    role: str = Field(..., description="The role of the message sender (user or assistant)")
    content: str = Field(..., description="The content of the message")

class Source(BaseModel):
    """A source document model."""
    url: str = Field(..., description="The URL of the source document")
    title: str = Field(..., description="The title of the source document")

class ChatRequest(BaseModel):
    """Chat request model."""
    message: str = Field(..., description="The user's message")
    conversation_id: Optional[str] = Field(None, description="Optional conversation ID for context")
    
class ChatResponse(BaseModel):
    """Chat response model."""
    answer: str = Field(..., description="The assistant's response")
    sources: List[Source] = Field(default_factory=list, description="List of sources used for the response")
    
class IndexRequest(BaseModel):
    """Request to index a new website."""
    url: str = Field(..., description="The URL to index")
    index_name: str = Field(..., description="The name of the index to use")
    
class IndexResponse(BaseModel):
    """Response from indexing operation."""
    status: str = Field(..., description="Status of the indexing operation")
    documents_processed: int = Field(..., description="Number of documents processed")
    
class StatusResponse(BaseModel):
    """Response for status check."""
    status: str = Field(..., description="Current status of the system")
    index_stats: dict = Field(..., description="Statistics about the current index") 