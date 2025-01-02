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
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from .models import (
    ChatRequest, 
    ChatResponse, 
    IndexRequest, 
    IndexResponse, 
    StatusResponse,
    Source
)
from ..rag_query import RAGQueryEngine
from ..web_scraper import WebScraper
from ..vector_store import VectorStore

# Load environment variables
load_dotenv()

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
    """
    try:
        # Get fresh response
        response = rag_engine.query(chat_request.message)
        
        # Convert source documents to Source models
        sources = [
            Source(
                url=doc.metadata.get('source', 'Unknown source'),
                title=doc.metadata.get('title', 'Unknown title')
            )
            for doc in response["source_documents"]
        ]
        
        # Create response
        chat_response = ChatResponse(
            answer=response["answer"],
            sources=sources
        )
        
        return chat_response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )

@app.get("/health")
@limiter.limit("100/minute")  # Rate limit: 100 requests per minute
async def health_check(request: Request):  # for rate limiter
    """
    Health check endpoint.
    Rate limited to 100 requests per minute.
    """
    return {"status": "healthy"} 