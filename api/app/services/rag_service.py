"""
Service for handling RAG operations.
"""
from typing import Dict, Any, Optional
import logging
import uuid
import asyncio
from datetime import datetime

from app.core.config import settings
from app.models.rag import IndexingTask
from app.services.web_scraper import WebScraper
from app.services.text_processor import TextProcessor
from app.services.vector_store import VectorStore

logger = logging.getLogger(__name__)

class RAGService:
    """Service for handling RAG operations."""
    
    def __init__(self):
        """Initialize RAG service."""
        self.tasks: Dict[str, IndexingTask] = {}
        self.vector_store = VectorStore(
            api_key=settings.PINECONE_API_KEY,
            environment=settings.PINECONE_ENVIRONMENT
        )
        self.text_processor = TextProcessor()

    async def query(
        self,
        question: str,
        namespace: Optional[str] = None,
        model_name: Optional[str] = settings.DEFAULT_MODEL_NAME,
        temperature: Optional[float] = settings.DEFAULT_TEMPERATURE
    ) -> Dict[str, Any]:
        """
        Query the RAG system.
        
        Args:
            question: Question to ask
            namespace: Optional namespace to search in
            model_name: Name of the model to use
            temperature: Temperature for response generation
            
        Returns:
            Dict[str, Any]: Answer and source documents
        """
        try:
            logger.info(f"Processing query: {question}")
            
            # Get response from vector store
            response = await self.vector_store.query(
                question=question,
                namespace=namespace,
                model_name=model_name,
                temperature=temperature
            )
            
            logger.info("Successfully generated response")
            return response
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            raise

    async def start_indexing(
        self,
        url: str,
        namespace: Optional[str] = None
    ) -> str:
        """
        Start indexing a website.
        
        Args:
            url: URL to index
            namespace: Optional namespace for the index
            
        Returns:
            str: Task ID for tracking progress
        """
        try:
            # Generate task ID
            task_id = str(uuid.uuid4())
            
            # Create task
            self.tasks[task_id] = IndexingTask(
                id=task_id,
                url=url,
                namespace=namespace,
                status="pending",
                created_at=datetime.utcnow(),
                progress=0.0
            )
            
            logger.info(f"Created indexing task {task_id} for URL: {url}")
            return task_id
            
        except Exception as e:
            logger.error(f"Error starting indexing task: {str(e)}")
            raise

    async def run_indexing(self, task_id: str) -> None:
        """
        Run indexing task in background.
        
        Args:
            task_id: ID of the task to run
        """
        task = self.tasks.get(task_id)
        if not task:
            logger.error(f"Task {task_id} not found")
            return
            
        try:
            logger.info(f"Starting indexing for task {task_id}")
            task.status = "running"
            task.started_at = datetime.utcnow()
            
            # Initialize scraper
            scraper = WebScraper(task.url)
            
            # Scrape website
            task.status = "scraping"
            documents = await asyncio.to_thread(scraper.scrape)
            task.progress = 0.3
            
            # Process text
            task.status = "processing"
            chunks = await asyncio.to_thread(
                self.text_processor.process_documents,
                documents
            )
            task.progress = 0.6
            
            # Index documents
            task.status = "indexing"
            await asyncio.to_thread(
                self.vector_store.index_documents,
                chunks,
                task.namespace
            )
            
            # Update task status
            task.status = "completed"
            task.progress = 1.0
            task.completed_at = datetime.utcnow()
            logger.info(f"Completed indexing task {task_id}")
            
        except Exception as e:
            logger.error(f"Error during indexing task {task_id}: {str(e)}")
            task.status = "failed"
            task.error = str(e)
            
        finally:
            # Clean up task after 1 hour
            await asyncio.sleep(3600)
            self.tasks.pop(task_id, None)

    async def get_indexing_status(self, task_id: str) -> Dict[str, Any]:
        """
        Get status of indexing task.
        
        Args:
            task_id: ID of the task to check
            
        Returns:
            Dict[str, Any]: Task status information
        """
        task = self.tasks.get(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")
            
        return {
            "status": task.status,
            "progress": task.progress,
            "message": f"Task is {task.status}",
            "error": task.error if task.status == "failed" else None,
            "created_at": task.created_at,
            "started_at": task.started_at,
            "completed_at": task.completed_at
        } 