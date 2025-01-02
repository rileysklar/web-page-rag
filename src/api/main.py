"""
FastAPI application for RAG operations.
"""
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from typing import List, Optional
import os
from dotenv import load_dotenv
import json
from redis import Redis
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from datetime import timedelta

from .models import (
    ChatRequest, 
    ChatResponse, 
    IndexRequest, 
    IndexResponse, 
    StatusResponse,
    Source,
    ChatMessage,
    ConversationMetadata
)
from .conversation import ConversationManager
from ..rag_query import RAGQueryEngine
from ..web_scraper import WebScraper
from ..vector_store import VectorStore

# Load environment variables
load_dotenv()

# Initialize Redis for caching
redis_client = Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=0,
    decode_responses=True
)

# Initialize conversation manager
conversation_manager = ConversationManager(redis_client)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Initialize FastAPI app
app = FastAPI(
    title="Web Page RAG API",
    description="API for retrieval-augmented generation on web content",
    version="1.0.0"
)

# Add rate limiter error handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Key security
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

async def verify_api_key(api_key: str = Depends(api_key_header)):
    """Verify the API key."""
    if api_key != os.getenv("API_KEY"):
        raise HTTPException(
            status_code=403,
            detail="Invalid API key"
        )
    return api_key

# Initialize RAG engine
rag_engine = RAGQueryEngine(
    index_name="web-page-rag",
    model_name="gpt-3.5-turbo",
    temperature=0.7
)

@app.post("/api/rag/query", response_model=ChatResponse)
@limiter.limit("20/minute")  # Rate limit: 20 requests per minute
async def query_rag(
    request: Request,  # for rate limiter
    chat_request: ChatRequest,
    api_key: str = Depends(verify_api_key)
) -> ChatResponse:
    """
    Query the RAG system with a user message.
    Rate limited to 20 requests per minute.
    Responses are cached for 1 hour.
    """
    try:
        # Get or create conversation ID
        conversation_id = chat_request.conversation_id or conversation_manager.create_conversation()
        
        # Add user message to conversation
        user_message = ChatMessage(
            role="user",
            content=chat_request.message
        )
        conversation_manager.add_message(conversation_id, user_message)
        
        # Get conversation history
        history = conversation_manager.get_messages(conversation_id)
        
        # Check cache first
        cache_key = f"chat:{conversation_id}:{chat_request.message}"
        cached_response = redis_client.get(cache_key)
        
        if cached_response:
            return ChatResponse(**json.loads(cached_response))
        
        # Get fresh response
        response = rag_engine.query(
            chat_request.message,
            context="\n".join([msg.content for msg in history[-5:]])  # Use last 5 messages for context
        )
        
        # Convert source documents to Source models
        sources = [
            Source(
                url=doc.metadata.get('source', 'Unknown source'),
                title=doc.metadata.get('title', 'Unknown title')
            )
            for doc in response["source_documents"]
        ]
        
        # Add assistant message to conversation
        assistant_message = ChatMessage(
            role="assistant",
            content=response["answer"],
            sources=[{"url": s.url, "title": s.title} for s in sources]
        )
        conversation_manager.add_message(conversation_id, assistant_message)
        
        # Create response
        chat_response = ChatResponse(
            answer=response["answer"],
            sources=sources,
            conversation_id=conversation_id,
            history=conversation_manager.get_messages(conversation_id)
        )
        
        # Cache response for 1 hour
        redis_client.setex(
            cache_key,
            timedelta(hours=1),
            json.dumps(chat_response.dict())
        )
        
        return chat_response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )

@app.get("/api/conversations", response_model=List[ConversationMetadata])
@limiter.limit("60/minute")  # Rate limit: 60 requests per minute
async def list_conversations(
    request: Request,  # for rate limiter
    limit: int = 10,
    offset: int = 0,
    api_key: str = Depends(verify_api_key)
) -> List[ConversationMetadata]:
    """
    List recent conversations.
    Rate limited to 60 requests per minute.
    """
    try:
        return conversation_manager.list_conversations(limit, offset)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error listing conversations: {str(e)}"
        )

@app.get("/api/conversations/{conversation_id}", response_model=List[ChatMessage])
@limiter.limit("60/minute")  # Rate limit: 60 requests per minute
async def get_conversation(
    request: Request,  # for rate limiter
    conversation_id: str,
    api_key: str = Depends(verify_api_key)
) -> List[ChatMessage]:
    """
    Get messages in a conversation.
    Rate limited to 60 requests per minute.
    """
    try:
        messages = conversation_manager.get_messages(conversation_id)
        if not messages:
            raise HTTPException(
                status_code=404,
                detail="Conversation not found"
            )
        return messages
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting conversation: {str(e)}"
        )

@app.delete("/api/conversations/{conversation_id}")
@limiter.limit("30/minute")  # Rate limit: 30 requests per minute
async def delete_conversation(
    request: Request,  # for rate limiter
    conversation_id: str,
    api_key: str = Depends(verify_api_key)
):
    """
    Delete a conversation.
    Rate limited to 30 requests per minute.
    """
    try:
        conversation_manager.delete_conversation(conversation_id)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting conversation: {str(e)}"
        )

@app.post("/api/rag/index", response_model=IndexResponse)
@limiter.limit("5/hour")  # Rate limit: 5 requests per hour
async def index_website(
    request: Request,  # for rate limiter
    index_request: IndexRequest,
    api_key: str = Depends(verify_api_key)
) -> IndexResponse:
    """
    Index a new website for RAG operations.
    Rate limited to 5 requests per hour due to resource intensity.
    """
    try:
        # Initialize scraper and vector store
        scraper = WebScraper(index_request.url)
        vector_store = VectorStore(index_request.index_name)
        
        # Scrape and index documents
        documents = scraper.scrape()
        vector_store.index_documents(documents)
        
        return IndexResponse(
            status="success",
            documents_processed=len(documents)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error indexing website: {str(e)}"
        )

@app.get("/api/rag/status", response_model=StatusResponse)
@limiter.limit("60/minute")  # Rate limit: 60 requests per minute
async def get_status(
    request: Request,  # for rate limiter
    api_key: str = Depends(verify_api_key)
) -> StatusResponse:
    """
    Get the current status of the RAG system.
    Rate limited to 60 requests per minute.
    Status is cached for 1 minute.
    """
    try:
        # Check cache first
        cache_key = "system:status"
        cached_status = redis_client.get(cache_key)
        
        if cached_status:
            return StatusResponse(**json.loads(cached_status))
        
        # Get fresh status
        vector_store = VectorStore("web-page-rag")
        stats = vector_store.get_stats()
        
        # Create response
        status_response = StatusResponse(
            status="operational",
            index_stats=stats
        )
        
        # Cache status for 1 minute
        redis_client.setex(
            cache_key,
            timedelta(minutes=1),
            json.dumps(status_response.dict())
        )
        
        return status_response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting status: {str(e)}"
        )

@app.get("/health")
@limiter.limit("100/minute")  # Rate limit: 100 requests per minute
async def health_check(request: Request):  # for rate limiter
    """
    Health check endpoint.
    Rate limited to 100 requests per minute.
    """
    return {"status": "healthy"} 