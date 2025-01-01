"""
Main script demonstrating the complete RAG workflow with web scraping.
"""
import argparse
from typing import Optional
import logging
from dotenv import load_dotenv

from web_scraper import WebScraper
from text_processor import TextProcessor
from vector_store import VectorStore
from rag_query import RAGQueryEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_argparse() -> argparse.ArgumentParser:
    """Set up command line argument parsing."""
    parser = argparse.ArgumentParser(
        description='Web scraping and RAG system'
    )
    parser.add_argument(
        '--url',
        type=str,
        required=True,
        help='URL to scrape'
    )
    parser.add_argument(
        '--index-name',
        type=str,
        required=True,
        help='Name for the Pinecone index'
    )
    parser.add_argument(
        '--namespace',
        type=str,
        help='Optional namespace for vectors'
    )
    parser.add_argument(
        '--query',
        type=str,
        help='Optional query to run after indexing'
    )
    return parser

def main():
    """Main function to run the complete workflow."""
    # Load environment variables
    load_dotenv()
    
    # Parse command line arguments
    parser = setup_argparse()
    args = parser.parse_args()
    
    try:
        # Step 1: Web Scraping
        logger.info("Starting web scraping...")
        scraper = WebScraper(args.url)
        documents = scraper.scrape()
        
        # Step 2: Text Processing
        logger.info("Processing text...")
        processor = TextProcessor()
        processed_docs = processor.process_documents(documents)
        
        # Step 3: Vector Storage
        logger.info("Storing vectors in Pinecone...")
        vector_store = VectorStore(args.index_name)
        vector_store.index_documents(
            processed_docs,
            namespace=args.namespace
        )
        
        # Step 4: Query (if provided)
        if args.query:
            logger.info("Running query...")
            rag_engine = RAGQueryEngine(args.index_name)
            result = rag_engine.query(
                args.query,
                namespace=args.namespace
            )
            
            print("\nQuery:", args.query)
            print("\nAnswer:", result["answer"])
            print("\nSources:")
            for i, doc in enumerate(result["source_documents"], 1):
                print(f"\n{i}. {doc.metadata.get('source', 'Unknown source')}")
        
        logger.info("Workflow completed successfully")
        
    except Exception as e:
        logger.error(f"Error in main workflow: {str(e)}")
        raise

if __name__ == "__main__":
    main() 