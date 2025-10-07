import asyncio
import aiohttp
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse
import re
from config import Config

class WebCrawler:
    def __init__(self):
        self.timeout = Config.REQUEST_TIMEOUT
        self.max_content_length = Config.MAX_CONTENT_LENGTH
        
    def clean_text(self, text: str) -> str:
        """Clean and normalize text content"""
        if not text:
            return ""
        
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', '', text)
        
        # Limit length
        if len(text) > self.max_content_length:
            text = text[:self.max_content_length] + "..."
            
        return text
    
    def extract_content(self, html: str, url: str) -> Dict[str, str]:
        """Extract relevant content from HTML"""
        try:
            soup = BeautifulSoup(html, 'lxml')
            
            # Remove script, style, and other non-content elements
            for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'iframe']):
                element.decompose()
            
            # Extract title
            title_tag = soup.find('title')
            title = self.clean_text(title_tag.get_text()) if title_tag else ""
            
            # Extract meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            description = ""
            if meta_desc:
                description = self.clean_text(meta_desc.get('content', ''))
            
            # Extract main content
            content_selectors = [
                'main', 'article', '[role="main"]', '.content', '.main-content',
                '.post-content', '.entry-content', '.article-content', '.page-content'
            ]
            
            main_content = ""
            for selector in content_selectors:
                content_element = soup.select_one(selector)
                if content_element:
                    main_content = self.clean_text(content_element.get_text())
                    break
            
            # If no main content found, extract from body
            if not main_content:
                body = soup.find('body')
                if body:
                    # Remove common non-content elements
                    for element in body.find_all(['nav', 'header', 'footer', 'aside']):
                        element.decompose()
                    main_content = self.clean_text(body.get_text())
            
            # Extract headings
            headings = []
            for h_tag in soup.find_all(['h1', 'h2', 'h3']):
                heading_text = self.clean_text(h_tag.get_text())
                if heading_text:
                    headings.append(heading_text)
            
            return {
                'title': title,
                'description': description,
                'content': main_content,
                'headings': ' | '.join(headings[:5]),  # Top 5 headings
                'url': url,
                'word_count': len(main_content.split()) if main_content else 0
            }
            
        except Exception as e:
            print(f"Error extracting content from {url}: {e}")
            return {
                'title': '',
                'description': '',
                'content': '',
                'headings': '',
                'url': url,
                'word_count': 0
            }
    
    async def fetch_url_async(self, session: aiohttp.ClientSession, url: str) -> Dict[str, str]:
        """Asynchronously fetch and extract content from a URL"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            async with session.get(url, headers=headers, timeout=self.timeout) as response:
                if response.status == 200:
                    html = await response.text()
                    content_data = self.extract_content(html, url)
                    content_data['status'] = 'success'
                    content_data['status_code'] = response.status
                    return content_data
                else:
                    return {
                        'title': '',
                        'description': '',
                        'content': '',
                        'headings': '',
                        'url': url,
                        'word_count': 0,
                        'status': 'error',
                        'status_code': response.status
                    }
                    
        except asyncio.TimeoutError:
            return {
                'title': '',
                'description': '',
                'content': '',
                'headings': '',
                'url': url,
                'word_count': 0,
                'status': 'timeout',
                'status_code': 0
            }
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return {
                'title': '',
                'description': '',
                'content': '',
                'headings': '',
                'url': url,
                'word_count': 0,
                'status': 'error',
                'status_code': 0
            }
    
    async def crawl_urls(self, urls: List[str]) -> List[Dict[str, str]]:
        """Crawl multiple URLs concurrently"""
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        connector = aiohttp.TCPConnector(limit=Config.MAX_CONCURRENT_REQUESTS)
        
        async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
            tasks = [self.fetch_url_async(session, url) for url in urls]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle exceptions
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    processed_results.append({
                        'title': '',
                        'description': '',
                        'content': '',
                        'headings': '',
                        'url': urls[i],
                        'word_count': 0,
                        'status': 'exception',
                        'status_code': 0
                    })
                else:
                    processed_results.append(result)
            
            return processed_results
    
    def crawl_urls_sync(self, urls: List[str]) -> List[Dict[str, str]]:
        """Synchronous wrapper for crawling URLs - only use outside async contexts"""
        return asyncio.run(self.crawl_urls(urls))
    
    async def crawl_urls_async_safe(self, urls: List[str]) -> List[Dict[str, str]]:
        """Async-safe method for use within async contexts like FastAPI"""
        return await self.crawl_urls(urls) 