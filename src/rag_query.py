"""
RAG query module for handling retrieval-augmented generation operations.
"""
from typing import Optional, Dict, Any
from langchain_community.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores import Pinecone
from langchain_community.embeddings import OpenAIEmbeddings
import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

class RAGQueryEngine:
    """A class to handle RAG operations for question answering."""
    
    def __init__(
        self,
        index_name: str,
        model_name: str = "gpt-3.5-turbo",
        temperature: float = 0.0
    ):
        """
        Initialize the RAG query engine.
        
        Args:
            index_name (str): Name of the Pinecone index
            model_name (str): Name of the OpenAI model to use
            temperature (float): Temperature for response generation
        """
        load_dotenv()
        
        self.index_name = index_name
        self.embeddings = OpenAIEmbeddings()
        self.llm = ChatOpenAI(
            model_name=model_name,
            temperature=temperature
        )
        
        # Create custom prompt template with conversation context
        template = """Use the following pieces of context to answer the question at the end. 
        If you don't know the answer, just say that you don't know, don't try to make up an answer.
        
        Previous conversation context:
        {context}
        
        Relevant documents:
        {documents}
        
        Question: {question}
        
        Answer: """
        
        self.prompt = PromptTemplate(
            template=template,
            input_variables=["context", "documents", "question"]
        )
    
    def setup_retrieval_qa(
        self,
        namespace: Optional[str] = None
    ) -> RetrievalQA:
        """
        Set up the retrieval QA chain.
        
        Args:
            namespace (str, optional): Namespace to search in
            
        Returns:
            RetrievalQA: Configured retrieval QA chain
        """
        # Initialize vector store
        vectorstore = Pinecone.from_existing_index(
            index_name=self.index_name,
            embedding=self.embeddings,
            namespace=namespace
        )
        
        # Create retrieval QA chain
        return RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=vectorstore.as_retriever(),
            return_source_documents=True,
            chain_type_kwargs={"prompt": self.prompt}
        )

    def query(
        self,
        question: str,
        context: Optional[str] = None,
        namespace: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Query the RAG system with a question.
        
        Args:
            question (str): Question to ask
            context (str, optional): Previous conversation context
            namespace (str, optional): Namespace to search in
            
        Returns:
            Dict[str, Any]: Answer and source documents
        """
        try:
            logger.info(f"Processing query: {question}")
            
            # Set up retrieval QA chain
            qa_chain = self.setup_retrieval_qa(namespace)
            
            # Get response
            response = qa_chain({
                "query": question,
                "context": context or "No previous context.",
                "documents": ""  # This will be filled by the chain
            })
            
            logger.info("Successfully generated response")
            
            return {
                "answer": response["result"],
                "source_documents": response["source_documents"]
            }
            
        except Exception as e:
            logger.error(f"Error during query processing: {str(e)}")
            raise 