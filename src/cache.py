"""Persistent caching for crawled pages."""
import hashlib
import json
import logging
from pathlib import Path
from typing import Optional

from .crawler import Page
from .utils import get_logger

logger = get_logger()


class PersistentCache:
    """Disk-based cache for crawled pages."""

    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _url_to_key(self, url: str) -> str:
        """Convert URL to cache key (filename-safe hash)."""
        return hashlib.sha256(url.encode()).hexdigest()

    def _get_cache_path(self, url: str) -> Path:
        """Get file path for cached URL."""
        key = self._url_to_key(url)
        return self.cache_dir / f"{key}.json"

    def get(self, url: str) -> Optional[Page]:
        """Retrieve cached page if available."""
        cache_path = self._get_cache_path(url)
        if not cache_path.exists():
            return None

        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return Page(url=data["url"], html=data["html"], status=data["status"])
        except Exception as e:
            logger.warning("Failed to load cache for %s: %s", url, e)
            return None

    def set(self, url: str, page: Page) -> None:
        """Store page in cache."""
        cache_path = self._get_cache_path(url)
        try:
            data = {
                "url": page.url,
                "html": page.html,
                "status": page.status,
            }
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False)
        except Exception as e:
            logger.warning("Failed to cache %s: %s", url, e)

    def clear(self) -> None:
        """Clear all cached files."""
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                cache_file.unlink()
            except Exception as e:
                logger.warning("Failed to delete cache file %s: %s", cache_file, e)
        logger.info("Cache cleared")

    def size(self) -> int:
        """Return number of cached items."""
        return len(list(self.cache_dir.glob("*.json")))

