"""Legal crawler service - web scraping for legal documents"""
import httpx
from typing import List, Dict, Any

class LegalCrawler:
    """Scrape legal documents from public sources"""
    
    def __init__(self):
        self.client = httpx.AsyncClient()
    
    async def crawl_laws(self, query: str) -> List[Dict[str, Any]]:
        """Crawl laws from public sources"""
        return []
    
    async def close(self):
        """Close the crawler"""
        await self.client.aclose()
"""Fallback crawler service used by legal_agent.

This stub keeps imports valid in environments where CrawlKit is not configured.
"""


class LegalCrawler:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key

    async def crawl_url(self, url: str) -> dict:
        return {
            "success": False,
            "url": url,
            "error": "Crawler service chưa được cấu hình",
        }
