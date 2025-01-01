"""
Vector store module for managing Pinecone operations and embeddings.
"""
from typing import List, Optional
from langchain.schema import Document
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Pinecone
from pinecone import Pinecone as PineconeClient
import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

class VectorStore:
    """A class to handle vector store operations with Pinecone."""
    
    def __init__(
        self,
        index_name: str,
        dimension: int = 1536  # OpenAI embedding dimension
    ):
        """
        Initialize the vector store.
        
        Args:
            index_name (str): Name of the Pinecone index
            dimension (int): Dimension of the vectors
        """
        load_dotenv()
        
        # Initialize Pinecone
        pc = PineconeClient(api_key=os.getenv('PINECONE_API_KEY'))
        
        # Create index if it doesn't exist
        if index_name not in pc.list_indexes().names():
            pc.create_index(
                name=index_name,
                dimension=dimension,
                metric='cosine'
            )
        
        self.index_name = index_name
        self.embeddings = OpenAIEmbeddings()

    def index_documents(
        self,
        documents: List[Document],
        namespace: Optional[str] = None
    ) -> None:
        """
        Index documents in Pinecone.
        
        Args:
            documents (List[Document]): Documents to index
            namespace (str, optional): Namespace for the vectors
        """
        try:
            logger.info(f"Indexing {len(documents)} documents in Pinecone")
            
            # Create Pinecone vector store
            Pinecone.from_documents(
                documents,
                self.embeddings,
                index_name=self.index_name,
                namespace=namespace
            )
            
            logger.info("Successfully indexed documents")
            
        except Exception as e:
            logger.error(f"Error during indexing: {str(e)}")
            raise

    def similarity_search(
        self,
        query: str,
        k: int = 4,
        namespace: Optional[str] = None
    ) -> List[Document]:
        """
        Perform similarity search in the vector store.
        
        Args:
            query (str): Query text
            k (int): Number of results to return
            namespace (str, optional): Namespace to search in
            
        Returns:
            List[Document]: Similar documents
        """
        try:
            # Initialize vector store for searching
            vectorstore = Pinecone.from_existing_index(
                index_name=self.index_name,
                embedding=self.embeddings,
                namespace=namespace
            )
            
            # Perform similarity search
            results = vectorstore.similarity_search(query, k=k)
            logger.info(f"Found {len(results)} similar documents")
            
            return results
            
        except Exception as e:
            logger.error(f"Error during similarity search: {str(e)}")
            raise 