import aiohttp
import logging
from typing import Optional
from .base import BaseScraper
from ..models.url_types import RegularURL

logger = logging.getLogger(__name__)

class HTTPScraper(BaseScraper):
    """Scraper for regular HTTP/HTTPS URLs."""

    def __init__(self, url_obj: RegularURL, timeout: int = 10, retries: int = 3):
        super().__init__(url_obj, timeout, retries)
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    async def fetch_content(self, url: str) -> str:
        """Fetch content from regular HTTP/HTTPS URLs."""
        # Check if URL is directly pointing to an M3U file
        is_m3u_file = url.lower().endswith(('.m3u', '.m3u8'))
        if is_m3u_file:
            logger.info(f"Detected direct M3U file URL: {url}")
        else:
            logger.info(f"Fetching HTTP content from: {url}")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, 
                                     headers=self.headers,
                                     timeout=self.timeout) as response:
                    response.raise_for_status()
                    content = await response.text()
                    
                    # If it's an M3U file, validate and log appropriately
                    if is_m3u_file:
                        if content.strip().startswith('#EXTM3U') or 'acestream://' in content:
                            logger.info(f"Successfully fetched M3U file content ({len(content)} bytes)")
                        else:
                            logger.warning(f"Content doesn't appear to be a valid M3U file. First 100 chars: {content[:100]}")
                    
                    return content
        except Exception as e:
            content_type = getattr(response, 'headers', {}).get('Content-Type', 'unknown')
            logger.error(f"Error fetching content from {url}: {str(e)}. Content-Type: {content_type}")
            raise