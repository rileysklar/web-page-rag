"""
Web scraping module for recursively loading web pages and processing their content.
"""
from typing import List, Dict, Any
from langchain_community.document_loaders import RecursiveUrlLoader
from bs4 import BeautifulSoup
import validators
from tqdm import tqdm
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebScraper:
    """A class to handle recursive web scraping operations."""
    
    def __init__(self, base_url: str):
        """
        Initialize the web scraper with a base URL.
        
        Args:
            base_url (str): The starting URL for scraping
        """
        if not validators.url(base_url):
            raise ValueError(f"Invalid URL provided: {base_url}")
        self.base_url = base_url

    def _clean_text(self, soup: BeautifulSoup) -> str:
        """
        Clean the HTML content and extract meaningful text.
        
        Args:
            soup (BeautifulSoup): BeautifulSoup object of the page
            
        Returns:
            str: Cleaned text content
        """
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
            
        # Get text and normalize whitespace
        text = soup.get_text(separator=' ', strip=True)
        return ' '.join(text.split())

    def scrape(self) -> List[Dict[Any, Any]]:
        """
        Scrape the website recursively starting from the base URL.
        
        Returns:
            List[Dict]: List of documents with text content and metadata
        """
        try:
            logger.info(f"Starting recursive scraping from: {self.base_url}")
            loader = RecursiveUrlLoader(
                url=self.base_url,
                max_depth=2,  # Adjust based on needs
                extractor=lambda x: self._clean_text(BeautifulSoup(x, 'html.parser'))
            )
            docs = loader.load()
            logger.info(f"Successfully scraped {len(docs)} documents")
            return docs
            
        except Exception as e:
            logger.error(f"Error during scraping: {str(e)}")
            raise 