import re
from typing import List, Tuple

from bs4 import BeautifulSoup

from .models import Section


def strip_noise(html: str) -> BeautifulSoup:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript", "header", "footer", "nav", "aside"]):
        tag.decompose()
    return soup


def extract_text_blocks(soup: BeautifulSoup) -> List[Tuple[str, str]]:
    """
    Returns list of (tag_name, text) preserving order.
    """
    blocks: List[Tuple[str, str]] = []
    for element in soup.find_all(["h1", "h2", "h3", "h4", "p", "li"]):
        text = " ".join(element.get_text(" ", strip=True).split())
        if not text:
            continue
        blocks.append((element.name, text))
    return blocks


def build_sections(blocks: List[Tuple[str, str]]) -> List[Section]:
    level_map = {"h1": 1, "h2": 2, "h3": 3, "h4": 4}
    root: List[Section] = []
    stack: List[Section] = []

    for tag, text in blocks:
        if tag in level_map:
            level = level_map[tag]
            section = Section(level=level, title=text, text="", children=[])
            while stack and stack[-1].level >= level:
                stack.pop()
            if stack:
                stack[-1].children.append(section)
            else:
                root.append(section)
            stack.append(section)
        else:
            # Text block: attach to nearest section
            if stack:
                stack[-1].text += (" " + text) if stack[-1].text else text
            else:
                # No heading yet; treat as pseudo section
                root.append(Section(level=1, title="Overview", text=text, children=[]))
    return root


def extract_sections(html: str) -> List[Section]:
    soup = strip_noise(html)
    blocks = extract_text_blocks(soup)
    sections = build_sections(blocks)
    return sections


def summarize_text(text: str, max_sentences: int = 2) -> str:
    """Extract first N sentences from text, with fallback to character limit."""
    if not text or not text.strip():
        return ""
    
    # Split by sentence endings
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    # Filter out very short fragments that aren't real sentences
    sentences = [s for s in sentences if len(s.split()) >= 3]
    
    if sentences:
        summary = " ".join(sentences[:max_sentences]).strip()
        if summary:
            return summary
    
    # Fallback: first 200 characters
    return text[:200].strip() + ("..." if len(text) > 200 else "")

