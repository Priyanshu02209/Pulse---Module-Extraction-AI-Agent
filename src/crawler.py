import re
from collections import deque
from dataclasses import dataclass
from typing import Dict, List, Optional, Set
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from .utils import get_logger, is_same_domain, looks_like_binary, normalize_url

# Import here to avoid circular dependency
try:
    from .cache import PersistentCache
except ImportError:
    PersistentCache = None

logger = get_logger()


@dataclass
class Page:
    url: str
    html: str
    status: int


class Crawler:
    def __init__(
        self,
        max_pages: int = 40,
        max_depth: int = 3,
        timeout: int = 12,
        allow_cross_domain: bool = False,
        persistent_cache: Optional["PersistentCache"] = None,
    ) -> None:
        self.max_pages = max_pages
        self.max_depth = max_depth
        self.timeout = timeout
        self.allow_cross_domain = allow_cross_domain
        self.cache: Dict[str, Page] = {}
        self.persistent_cache = persistent_cache

    def fetch(self, url: str) -> Page | None:
        # Check in-memory cache first
        if url in self.cache:
            return self.cache[url]
        
        # Check persistent cache
        if self.persistent_cache:
            cached_page = self.persistent_cache.get(url)
            if cached_page:
                self.cache[url] = cached_page
                return cached_page
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
        }
        try:
            resp = requests.get(url, headers=headers, timeout=self.timeout, allow_redirects=True)
            resp.raise_for_status()
        except requests.exceptions.Timeout:
            logger.warning("Timeout fetching %s", url)
            return None
        except requests.exceptions.TooManyRedirects:
            logger.warning("Too many redirects for %s", url)
            return None
        except requests.exceptions.HTTPError as e:
            logger.warning("HTTP error %s for %s", e.response.status_code, url)
            return None
        except requests.RequestException as exc:
            logger.warning("Fetch failed %s (%s)", url, exc)
            return None
        
        content_type = resp.headers.get("Content-Type", "").lower()
        if looks_like_binary(content_type):
            logger.debug("Skip binary content %s (%s)", url, content_type)
            return None
        
        # Check if response is actually HTML
        if not content_type.startswith("text/html"):
            logger.debug("Skip non-HTML content %s (%s)", url, content_type)
            return None
        
        # Validate HTML content (basic check)
        html_text = resp.text
        if len(html_text) < 100:  # Too short to be useful
            logger.debug("Skip very short content %s (%d chars)", url, len(html_text))
            return None
        
        page = Page(url=resp.url, html=html_text, status=resp.status_code)
        self.cache[url] = page
        
        # Store in persistent cache
        if self.persistent_cache:
            self.persistent_cache.set(url, page)
        
        return page

    def extract_links(self, base_url: str, html: str) -> List[str]:
        """Extract and normalize links from HTML, filtering out common non-content URLs."""
        try:
            soup = BeautifulSoup(html, "html.parser")
        except Exception as e:
            logger.warning("Failed to parse HTML from %s: %s", base_url, e)
            return []
        
        links: List[str] = []
        skip_patterns = [
            r"\.(pdf|zip|docx?|xlsx?|pptx?|jpg|jpeg|png|gif|svg|mp4|mp3)$",
            r"mailto:",
            r"javascript:",
            r"#",
            r"/api/",
            r"/login",
            r"/logout",
            r"/signup",
            r"/register",
        ]
        
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if not href or href.strip() == "#":
                continue
            
            # Skip common non-content patterns
            if any(re.search(pattern, href, re.IGNORECASE) for pattern in skip_patterns):
                continue
            
            normalized = normalize_url(base_url, href)
            if not normalized:
                continue
            
            if not self.allow_cross_domain and not is_same_domain(base_url, normalized):
                continue
            
            links.append(normalized)
        
        return links

    def crawl(self, roots: List[str]) -> List[Page]:
        queue = deque([(root, 0) for root in roots])
        visited: Set[str] = set()
        pages: List[Page] = []

        while queue and len(pages) < self.max_pages:
            url, depth = queue.popleft()
            if url in visited or depth > self.max_depth:
                continue
            visited.add(url)

            parsed = urlparse(url)
            if parsed.scheme not in {"http", "https"}:
                continue

            page = self.fetch(url)
            if not page:
                continue
            pages.append(page)

            links = self.extract_links(url, page.html)
            for link in links:
                if link not in visited:
                    queue.append((link, depth + 1))
        return pages

