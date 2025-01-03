"""
Web scraping module for recursively loading web pages and processing their content.
"""
from typing import List, Dict, Any, Set
from bs4 import BeautifulSoup
import validators
from urllib.parse import urljoin, urlparse
import requests
import logging
import re
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebScraper:
    """A class to handle recursive web scraping operations."""
    
    def __init__(self, base_url: str, max_depth: int = 10, delay: float = 1.0):
        """
        Initialize the web scraper with a base URL.
        
        Args:
            base_url (str): The starting URL for scraping
            max_depth (int): Maximum depth for recursive scraping
            delay (float): Delay between requests in seconds
        """
        if not validators.url(base_url):
            raise ValueError(f"Invalid URL provided: {base_url}")
            
        self.base_url = base_url.rstrip('/')
        self.domain = urlparse(base_url).netloc
        self.max_depth = max_depth
        self.delay = delay
        self.visited_urls: Set[str] = set()
        
        # Initialize Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # Initialize the WebDriver
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        
        # Set page load timeout
        self.driver.set_page_load_timeout(30)

    def __del__(self):
        """Cleanup method to ensure the browser is closed."""
        if hasattr(self, 'driver'):
            self.driver.quit()

    def _wait_for_content(self, timeout: int = 10) -> None:
        """
        Wait for dynamic content to load.
        
        Args:
            timeout (int): Maximum time to wait in seconds
        """
        try:
            # Wait for common content indicators
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "main"))
                or EC.presence_of_element_located((By.TAG_NAME, "article"))
                or EC.presence_of_element_located((By.CLASS_NAME, "content"))
            )
        except TimeoutException:
            logger.warning("Timeout waiting for content to load")

    def _is_valid_url(self, url: str) -> bool:
        """
        Check if URL is valid and belongs to the same domain.
        
        Args:
            url (str): URL to check
            
        Returns:
            bool: True if URL is valid and belongs to same domain
        """
        try:
            parsed = urlparse(url)
            return (
                bool(parsed.netloc) and
                parsed.netloc == self.domain and
                parsed.scheme in ['http', 'https'] and
                not any(ext in url.lower() for ext in [
                    '.jpg', '.jpeg', '.png', '.gif', '.pdf', 
                    '.doc', '.docx', '.mp3', '.mp4', '.zip'
                ]) and
                (not '#' in url or url.endswith('.jsx'))  # Allow JSX files but ignore other anchor links
            )
        except Exception:
            return False

    def _clean_text(self, html_content: str) -> str:
        """
        Clean the HTML content and extract meaningful text.
        
        Args:
            html_content (str): Raw HTML content
            
        Returns:
            str: Cleaned text content
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove unwanted elements
        for element in soup.find_all([
            'script', 'style', 'nav', 'meta', 'link', 
            'noscript', 'iframe', 'svg', 'path'
        ]):
            element.decompose()
            
        # Remove comments
        for comment in soup.find_all(string=lambda text: isinstance(text, str) and '<!--' in text):
            comment.extract()

        # Extract text from sections we want to keep
        content_sections = []
        
        # Find main content areas
        main_content = soup.find('main') or soup.find(id=re.compile(r'content|main', re.I))
        if main_content:
            content_sections.append(main_content.get_text(separator='\n', strip=True))
        
        # Find article content
        articles = soup.find_all('article') or soup.find_all(class_=re.compile(r'post|article|content', re.I))
        for article in articles:
            content_sections.append(article.get_text(separator='\n', strip=True))
        
        # If no specific content areas found, get all text
        if not content_sections:
            content_sections.append(soup.get_text(separator='\n', strip=True))

        # Join all content
        text = '\n\n'.join(content_sections)
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        # Remove any remaining HTML entities
        text = re.sub(r'&[a-zA-Z]+;', ' ', text)
        
        return text.strip()

    def _extract_links(self, html_content: str, current_url: str) -> List[str]:
        """
        Extract valid links from the page.
        
        Args:
            html_content (str): Raw HTML content
            current_url (str): Current page URL
            
        Returns:
            List[str]: List of valid URLs
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        links = set()
        
        # Look for links in HTML
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            if href and not href.startswith(('javascript:', 'mailto:', 'tel:')):
                absolute_url = urljoin(current_url, href)
                if self._is_valid_url(absolute_url):
                    links.add(absolute_url)
        
        # Look for links in JavaScript objects and JSON data
        scripts = soup.find_all(['script', 'div'], {
            'type': ['application/json', 'text/javascript', 'module'],
            'id': re.compile(r'.*-json$', re.I)  # Match IDs ending in -json
        })
        
        for script in scripts:
            try:
                if script.string:
                    # Try to extract JSON from the script content
                    json_matches = re.finditer(r'\{(?:[^{}]|(?R))*\}', script.string)
                    for json_match in json_matches:
                        try:
                            data = json.loads(json_match.group())
                            self._extract_links_from_json(data, current_url, links)
                            # Also extract and store text content
                            text_content = self._extract_text_from_json(data)
                            if text_content:
                                logger.info(f"Found JSON content: {text_content[:100]}...")
                        except json.JSONDecodeError:
                            continue
            except Exception as e:
                logger.debug(f"Error processing script: {str(e)}")

        # Look for React components with JSON data
        for tag in soup.find_all(True):  # Search all tags
            # Check for data attributes that might contain JSON
            json_attrs = [attr for attr in tag.attrs if 
                         attr.startswith('data-') and 
                         isinstance(tag[attr], str) and 
                         tag[attr].startswith('{')]
            
            for attr in json_attrs:
                try:
                    data = json.loads(tag[attr])
                    self._extract_links_from_json(data, current_url, links)
                    # Extract and store text content
                    text_content = self._extract_text_from_json(data)
                    if text_content:
                        logger.info(f"Found component data: {text_content[:100]}...")
                except:
                    continue
        
        return list(links)

    def _extract_links_from_json(self, data: Any, current_url: str, links: Set[str]) -> None:
        """
        Recursively extract links from JSON data.
        
        Args:
            data: JSON data to process
            current_url (str): Current page URL
            links (Set[str]): Set to store found links
        """
        if isinstance(data, dict):
            for value in data.values():
                if isinstance(value, str) and value.startswith(('http://', 'https://')):
                    absolute_url = urljoin(current_url, value)
                    if self._is_valid_url(absolute_url):
                        links.add(absolute_url)
                elif isinstance(value, (dict, list)):
                    self._extract_links_from_json(value, current_url, links)
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, (dict, list)):
                    self._extract_links_from_json(item, current_url, links)

    def _extract_text_from_json(self, data: Any) -> str:
        """
        Extract text content from JSON data structures.
        
        Args:
            data: JSON data to process
            
        Returns:
            str: Extracted text content
        """
        text_content = []
        
        def extract_text(item: Any) -> None:
            if isinstance(item, dict):
                # Look for common text fields
                text_fields = ['question', 'answer', 'title', 'content', 'description', 'text']
                for field in text_fields:
                    if field in item and isinstance(item[field], str):
                        text_content.append(item[field])
                # Recursively process nested objects
                for value in item.values():
                    extract_text(value)
            elif isinstance(item, list):
                for value in item:
                    extract_text(value)
            elif isinstance(item, str):
                text_content.append(item)
        
        extract_text(data)
        return '\n'.join(text_content)

    def _scrape_url(self, url: str, depth: int = 0) -> List[Dict[str, str]]:
        """
        Scrape a single URL and its linked pages recursively.
        
        Args:
            url (str): URL to scrape
            depth (int): Current depth in recursive scraping
            
        Returns:
            List[Dict]: List of documents with text content
        """
        if depth >= self.max_depth or url in self.visited_urls:
            return []
        
        self.visited_urls.add(url)
        documents = []
        
        try:
            logger.info(f"Scraping URL (depth {depth}): {url}")
            
            # Respect crawl delay
            time.sleep(self.delay)
            
            # Load the page with Selenium
            self.driver.get(url)
            
            # Wait for dynamic content
            self._wait_for_content()
            
            # Get the rendered page source
            html_content = self.driver.page_source
            
            # Extract and clean text
            text_content = self._clean_text(html_content)
            
            if text_content:
                # Get page title
                title = self.driver.title or url
                
                documents.append({
                    'page_content': text_content,
                    'metadata': {
                        'source': url,
                        'title': title,
                        'depth': depth
                    }
                })
            
            # Extract and process links
            links = self._extract_links(html_content, url)
            
            # Check for JSX files
            if url.endswith('.jsx'):
                try:
                    response = requests.get(url)
                    if response.ok:
                        # Extract JSON data from JSX file
                        jsx_content = response.text
                        json_matches = re.finditer(r'const\s+(\w+)\s*=\s*({[\s\S]*?});', jsx_content)
                        for match in json_matches:
                            try:
                                json_data = json.loads(match.group(2))
                                text_content = self._extract_text_from_json(json_data)
                                if text_content:
                                    documents.append({
                                        'page_content': text_content,
                                        'metadata': {
                                            'source': url,
                                            'title': f"JSX Component: {match.group(1)}",
                                            'depth': depth
                                        }
                                    })
                            except:
                                continue
                except:
                    logger.warning(f"Failed to process JSX file: {url}")
            
            # Process found links
            for link in links:
                if link not in self.visited_urls:
                    documents.extend(self._scrape_url(link, depth + 1))
                
        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}")

        return documents

    def scrape(self) -> List[Dict[Any, Any]]:
        """
        Scrape the website recursively starting from the base URL.
        
        Returns:
            List[Dict]: List of documents with text content and metadata
        """
        try:
            logger.info(f"Starting recursive scraping from: {self.base_url}")
            documents = self._scrape_url(self.base_url)
            logger.info(f"Successfully scraped {len(documents)} documents")
            logger.info(f"Total unique URLs visited: {len(self.visited_urls)}")
            return documents
            
        except Exception as e:
            logger.error(f"Error during scraping: {str(e)}")
            raise
        finally:
            self.driver.quit() 