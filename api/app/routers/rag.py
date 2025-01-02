"""
Router for RAG operations.
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Optional, List
from pydantic import BaseModel, HttpUrl
import logging

from app.core.config import settings
from app.core.security import verify_api_key
from app.models.rag import (
    QueryRequest,
    QueryResponse,
    IndexRequest,
    IndexResponse,
    IndexStatus
)
from app.services.rag_service import RAGService

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Initialize RAG service
rag_service = RAGService()

class QueryRequest(BaseModel):
    """Query request model."""
    question: str
    namespace: Optional[str] = None
    model_name: Optional[str] = settings.DEFAULT_MODEL_NAME
    temperature: Optional[float] = settings.DEFAULT_TEMPERATURE

class QueryResponse(BaseModel):
    """Query response model."""
    answer: str
    sources: List[str]

class IndexRequest(BaseModel):
    """Index request model."""
    url: HttpUrl
    namespace: Optional[str] = None

class IndexResponse(BaseModel):
    """Index response model."""
    status: str
    message: str
    task_id: Optional[str] = None

class IndexStatus(BaseModel):
    """Index status model."""
    status: str
    progress: Optional[float] = None
    message: Optional[str] = None

@router.post("/query", response_model=QueryResponse)
async def query(
    request: QueryRequest,
    api_key: str = Depends(verify_api_key)
) -> QueryResponse:
    """
    Query the RAG system.
    
    Args:
        request: Query request containing question and optional parameters
        api_key: API key for authentication
        
    Returns:
        QueryResponse: Answer and source documents
    """
    try:
        logger.info(f"Processing query: {request.question}")
        
        result = await rag_service.query(
            question=request.question,
            namespace=request.namespace,
            model_name=request.model_name,
            temperature=request.temperature
        )
        
        return QueryResponse(
            answer=result["answer"],
            sources=[doc.metadata["source"] for doc in result["source_documents"]]
        )
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )

@router.post("/index", response_model=IndexResponse)
async def index(
    request: IndexRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(verify_api_key)
) -> IndexResponse:
    """
    Index a website for RAG.
    
    Args:
        request: Index request containing URL and optional namespace
        background_tasks: FastAPI background tasks
        api_key: API key for authentication
        
    Returns:
        IndexResponse: Status of indexing task
    """
    try:
        logger.info(f"Starting indexing for URL: {request.url}")
        
        # Start indexing in background
        task_id = await rag_service.start_indexing(
            url=str(request.url),
            namespace=request.namespace
        )
        
        background_tasks.add_task(
            rag_service.run_indexing,
            task_id=task_id
        )
        
        return IndexResponse(
            status="started",
            message="Indexing started successfully",
            task_id=task_id
        )
        
    except Exception as e:
        logger.error(f"Error starting indexing: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error starting indexing: {str(e)}"
        )

@router.get("/index/{task_id}", response_model=IndexStatus)
async def get_index_status(
    task_id: str,
    api_key: str = Depends(verify_api_key)
) -> IndexStatus:
    """
    Get status of indexing task.
    
    Args:
        task_id: ID of indexing task
        api_key: API key for authentication
        
    Returns:
        IndexStatus: Current status of indexing task
    """
    try:
        logger.info(f"Getting status for task: {task_id}")
        
        status = await rag_service.get_indexing_status(task_id)
        return IndexStatus(**status)
        
    except Exception as e:
        logger.error(f"Error getting index status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting index status: {str(e)}"
        ) 