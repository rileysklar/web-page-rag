"""
Text processing module for chunking and preprocessing text content.
"""
from typing import List, Dict, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
import logging

logger = logging.getLogger(__name__)

class TextProcessor:
    """A class to handle text processing and chunking operations."""
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ):
        """
        Initialize the text processor.
        
        Args:
            chunk_size (int): The size of text chunks
            chunk_overlap (int): The overlap between chunks
        """
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )

    def process_documents(
        self,
        documents: List[Dict[Any, Any]]
    ) -> List[Document]:
        """
        Process and chunk documents into smaller pieces.
        
        Args:
            documents (List[Dict]): List of documents to process
            
        Returns:
            List[Document]: List of processed and chunked documents
        """
        try:
            logger.info(f"Processing {len(documents)} documents")
            
            # Convert to LangChain documents if needed
            docs = []
            for doc in documents:
                if isinstance(doc, Document):
                    docs.append(doc)
                else:
                    # Assume dict with 'page_content' and 'metadata'
                    docs.append(Document(
                        page_content=doc.get('page_content', ''),
                        metadata=doc.get('metadata', {})
                    ))
            
            # Split documents into chunks
            chunked_docs = self.text_splitter.split_documents(docs)
            logger.info(f"Created {len(chunked_docs)} chunks")
            
            return chunked_docs
            
        except Exception as e:
            logger.error(f"Error during text processing: {str(e)}")
            raise 