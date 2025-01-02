"""
FastAPI application for RAG operations.
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from typing import List, Optional
import os
from dotenv import load_dotenv

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

# Initialize FastAPI app
app = FastAPI(
    title="Web Page RAG API",
    description="API for retrieval-augmented generation on web content",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this with your frontend URL in production
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
async def query_rag(
    request: ChatRequest,
    api_key: str = Depends(verify_api_key)
) -> ChatResponse:
    """
    Query the RAG system with a user message.
    """
    try:
        response = rag_engine.query(request.message)
        
        # Convert source documents to Source models
        sources = [
            Source(
                url=doc.metadata.get('source', 'Unknown source'),
                title=doc.metadata.get('title', 'Unknown title')
            )
            for doc in response["source_documents"]
        ]
        
        return ChatResponse(
            answer=response["answer"],
            sources=sources
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )

@app.post("/api/rag/index", response_model=IndexResponse)
async def index_website(
    request: IndexRequest,
    api_key: str = Depends(verify_api_key)
) -> IndexResponse:
    """
    Index a new website for RAG operations.
    """
    try:
        # Initialize scraper and vector store
        scraper = WebScraper(request.url)
        vector_store = VectorStore(request.index_name)
        
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
async def get_status(
    api_key: str = Depends(verify_api_key)
) -> StatusResponse:
    """
    Get the current status of the RAG system.
    """
    try:
        # Get index statistics from Pinecone
        vector_store = VectorStore("web-page-rag")
        stats = vector_store.get_stats()
        
        return StatusResponse(
            status="operational",
            index_stats=stats
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting status: {str(e)}"
        )

@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {"status": "healthy"} 