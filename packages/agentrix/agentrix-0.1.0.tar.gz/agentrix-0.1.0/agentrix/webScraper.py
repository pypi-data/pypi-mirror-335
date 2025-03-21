import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import time
import random
from .core import Tool

class WebScraper:
    def __init__(self, user_agent=None, delay=1):
        """
        Initialize the web scraper with configurable parameters.
        
        Args:
            user_agent (str): Custom user agent string to use for requests
            delay (float): Delay between requests in seconds to respect rate limits
        """
        self.session = requests.Session()
        self.delay = delay
        self.last_request_time = 0
        
        # Set default user agent if none provided
        default_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        self.session.headers.update({"User-Agent": user_agent or default_ua})
    
    def _respect_rate_limits(self):
        """Add delay between requests to avoid overloading servers"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.delay:
            sleep_time = self.delay - time_since_last
            # Add small random delay to avoid predictable patterns
            sleep_time += random.uniform(0, 0.5)
            time.sleep(sleep_time)
            
        self.last_request_time = time.time()
    
    def fetch_page(self, url, timeout=10):
        """
        Fetch a webpage and return its content.
        
        Args:
            url (str): URL to fetch
            timeout (int): Request timeout in seconds
            
        Returns:
            dict: Dictionary containing status, content, and metadata
        """
        self._respect_rate_limits()
        
        try:
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            
            # Extract domain for context
            domain = urlparse(url).netloc
            
            return {
                "status": "success",
                "status_code": response.status_code,
                "content": response.text,
                "url": response.url,
                "domain": domain,
                "headers": dict(response.headers)
            }
        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "error_type": type(e).__name__,
                "error_message": str(e),
                "url": url
            }
    
    def extract_text(self, html_content, selector=None):
        """
        Extract text content from HTML, optionally using a CSS selector.
        
        Args:
            html_content (str): HTML content to parse
            selector (str): Optional CSS selector to target specific elements
            
        Returns:
            str: Extracted text content
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.extract()
        
        if selector:
            elements = soup.select(selector)
            text = "\n".join([el.get_text(separator=' ', strip=True) for el in elements])
        else:
            # Get text from entire document
            text = soup.get_text(separator=' ', strip=True)
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        text = '\n'.join(line for line in lines if line)
        
        return text
    
    def extract_links(self, html_content, base_url=None, selector=None):
        """
        Extract links from HTML content.
        
        Args:
            html_content (str): HTML content to parse
            base_url (str): Base URL for resolving relative links
            selector (str): Optional CSS selector to target specific elements
            
        Returns:
            list: List of extracted links
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        if selector:
            elements = soup.select(selector)
            links = [a.get('href') for el in elements for a in el.find_all('a', href=True)]
        else:
            links = [a.get('href') for a in soup.find_all('a', href=True)]
        
        # Filter out None values and empty strings
        links = [link for link in links if link]
        
        # Resolve relative URLs if base_url is provided
        if base_url:
            from urllib.parse import urljoin
            links = [urljoin(base_url, link) for link in links]
        
        return links
    
    def extract_metadata(self, html_content):
        """
        Extract metadata from HTML content (title, description, etc.)
        
        Args:
            html_content (str): HTML content to parse
            
        Returns:
            dict: Dictionary of metadata
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        metadata = {}
        
        # Extract title
        title_tag = soup.find('title')
        if title_tag:
            metadata['title'] = title_tag.get_text(strip=True)
        
        # Extract meta tags
        for meta in soup.find_all('meta'):
            name = meta.get('name', '').lower()
            property = meta.get('property', '').lower()
            content = meta.get('content')
            
            if name and content:
                metadata[name] = content
            elif property and content:
                metadata[property] = content
        
        return metadata

# Create Tool functions for the agent framework

def fetch_webpage(url, selector=None):
    """Fetch a webpage and return its content"""
    scraper = WebScraper()
    result = scraper.fetch_page(url)
    
    if result["status"] == "error":
        return f"Error fetching {url}: {result['error_message']}"
    
    # Extract text if requested with selector
    if selector:
        content = scraper.extract_text(result["content"], selector)
    else:
        content = scraper.extract_text(result["content"])
    
    # Add metadata
    metadata = scraper.extract_metadata(result["content"])
    
    # Create a more structured and concise result that's easier to process
    summary = {
        "title": metadata.get('title', 'Unknown'),
        "description": metadata.get('description', ''),
        "main_content": content,
        "domain": result["domain"],
        "url": result["url"]
    }
    
    # Return a JSON-formatted string instead of raw HTML content
    return f"""
WEBSITE CONTENT SUMMARY:
Title: {summary['title']}
Domain: {summary['domain']}
URL: {summary['url']}
Description: {summary['description']}

MAIN CONTENT PREVIEW:
{summary['main_content']}
"""

def extract_webpage_links(url, selector=None):
    """Extract links from a webpage"""
    scraper = WebScraper()
    result = scraper.fetch_page(url)
    
    if result["status"] == "error":
        return f"Error fetching {url}: {result['error_message']}"
    
    links = scraper.extract_links(result["content"], base_url=url, selector=selector)
    
    # Format the links nicely
    if not links:
        return "No links found on the page."
    
    return f"Found {len(links)} links:\n" + "\n".join(links)

# Create tools for the Agent framework
webpage_fetch_tool = Tool(
    name="fetch_webpage",
    description="Fetch and extract content from a webpage. Optional CSS selector to extract specific content.",
    function=fetch_webpage,
    inputs={
        "url": ["string", "The URL of the webpage to fetch"],
        "selector": ["string", "Optional CSS selector to extract specific content (e.g., 'article', '.content', '#main')"]
    }
)

webpage_links_tool = Tool(
    name="extract_webpage_links",
    description="Extract all links from a webpage. Optional CSS selector to extract links from specific elements.",
    function=extract_webpage_links,
    inputs={
        "url": ["string", "The URL of the webpage to fetch links from"],
        "selector": ["string", "Optional CSS selector to extract links from specific elements (e.g., 'nav', '.sidebar')"]
    }
)

# Export the tools so they can be imported elsewhere
web_scraper_tools = [webpage_fetch_tool, webpage_links_tool]