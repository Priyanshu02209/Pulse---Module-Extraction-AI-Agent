import logging
import re
from typing import Iterable, List, Set
from urllib.parse import urlparse, urljoin

import tldextract

LOGGER_NAME = "pulsegen"


def get_logger(name: str = LOGGER_NAME) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(message)s", "%H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


def normalize_url(base_url: str, link: str) -> str:
    parsed_base = urlparse(base_url)
    joined = urljoin(base_url, link)
    parsed = urlparse(joined)
    if parsed.scheme not in {"http", "https"}:
        return ""
    # Drop fragments
    normalized = parsed._replace(fragment="").geturl()
    return normalized


def is_same_domain(url: str, other: str) -> bool:
    def domain_parts(target: str) -> str:
        ext = tldextract.extract(target)
        return f"{ext.domain}.{ext.suffix}"

    return domain_parts(url) == domain_parts(other)


def dedupe_preserve_order(items: Iterable[str]) -> List[str]:
    seen: Set[str] = set()
    result: List[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def looks_like_binary(content_type: str) -> bool:
    if not content_type:
        return False
    return bool(
        re.search(
            r"(application/(pdf|zip|octet-stream)|image/|audio/|video/)", content_type,
            re.IGNORECASE,
        )
    )

