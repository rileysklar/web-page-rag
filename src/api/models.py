"""
Pydantic models for API requests and responses.
"""
from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from datetime import datetime

class ChatMessage(BaseModel):
    """A chat message model."""
    role: str = Field(..., description="The role of the message sender (user or assistant)")
    content: str = Field(..., description="The content of the message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of the message")
    sources: Optional[List[Dict[str, str]]] = Field(None, description="Sources used for this message")

class Source(BaseModel):
    """A source document model."""
    url: str = Field(..., description="The URL of the source document")
    title: str = Field(..., description="The title of the source document")

class ChatRequest(BaseModel):
    """Chat request model."""
    message: str = Field(..., description="The user's message")
    conversation_id: Optional[str] = Field(None, description="Optional conversation ID for context")
    metadata: Optional[Dict] = Field(default_factory=dict, description="Additional metadata for the conversation")
    
class ChatResponse(BaseModel):
    """Chat response model."""
    answer: str = Field(..., description="The assistant's response")
    sources: List[Source] = Field(default_factory=list, description="List of sources used for the response")
    conversation_id: str = Field(..., description="The ID of the conversation")
    history: List[ChatMessage] = Field(default_factory=list, description="Previous messages in the conversation")
    
class ConversationMetadata(BaseModel):
    """Metadata for a conversation."""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    title: Optional[str] = Field(None, description="Auto-generated title for the conversation")
    summary: Optional[str] = Field(None, description="Auto-generated summary of the conversation")
    
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