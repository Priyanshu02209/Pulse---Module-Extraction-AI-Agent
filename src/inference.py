import re
from collections import defaultdict
from typing import Dict, List, Set

from .cleaner import extract_sections, summarize_text
from .models import Module, Section, Submodule
from .utils import dedupe_preserve_order, get_logger

logger = get_logger()


def normalize_title(title: str) -> str:
    """Normalize titles for better grouping (lowercase, strip extra spaces)."""
    return " ".join(title.lower().split())


def is_valid_module_title(title: str) -> bool:
    """Filter out noise titles."""
    if not title or len(title) < 3:
        return False
    # Skip common navigation/UI elements
    noise_patterns = [
        r"^(home|menu|search|login|sign|account|profile|settings|help|support|contact|about|privacy|terms|cookie)",
        r"^(skip|jump|back|next|previous|top|bottom)",
        r"^(page \d+|page\d+|\d+ of \d+)",
    ]
    title_lower = title.lower().strip()
    for pattern in noise_patterns:
        if re.match(pattern, title_lower):
            return False
    return True


def merge_similar_titles(titles: List[str], threshold: float = 0.8) -> Dict[str, str]:
    """
    Merge similar titles using simple string similarity.
    Returns mapping from original -> canonical title.
    """
    from difflib import SequenceMatcher
    
    canonical: Dict[str, str] = {}
    for title in titles:
        canonical[title] = title
    
    for i, title1 in enumerate(titles):
        for title2 in titles[i + 1 :]:
            norm1, norm2 = normalize_title(title1), normalize_title(title2)
            similarity = SequenceMatcher(None, norm1, norm2).ratio()
            if similarity >= threshold:
                # Use the shorter, more specific title as canonical
                canonical_title = title1 if len(title1) <= len(title2) else title2
                canonical[title1] = canonical_title
                canonical[title2] = canonical_title
    
    return canonical


def infer_from_sections(sections: List[Section], source_url: str) -> Dict[str, List[Section]]:
    """Group sections by normalized title, filtering noise."""
    grouped: Dict[str, List[Section]] = defaultdict(list)
    for section in sections:
        if not is_valid_module_title(section.title):
            continue
        key = section.title
        grouped[key].append(section)
    return grouped


def module_description(section: Section) -> str:
    """Generate description from section content and immediate children."""
    content = section.text.strip()
    # Collect text from direct children (submodules)
    child_texts = []
    for child in section.children[:5]:  # Limit to top 5 to avoid noise
        if child.text.strip():
            child_texts.append(child.text.strip())
    
    full_content = " ".join([content] + child_texts)
    if not full_content.strip():
        # Fallback: use title if no content
        return f"Module for {section.title}."
    
    return summarize_text(full_content, max_sentences=3)


def submodule_description(section: Section) -> str:
    """Generate description for submodule."""
    if section.text.strip():
        return summarize_text(section.text, max_sentences=2)
    # Fallback to title-based description
    return f"Functionality related to {section.title}."


def calculate_confidence(section: Section, is_module: bool = True) -> float:
    """Calculate confidence score based on content quality."""
    base = 0.6 if is_module else 0.5
    text_length = len(section.text.split())
    
    # Boost confidence for longer, more detailed content
    length_bonus = min(0.2, text_length * 0.01)
    
    # Boost if has children (more structured)
    structure_bonus = 0.1 if section.children else 0
    
    # Penalize very short titles
    title_penalty = 0.1 if len(section.title.split()) < 2 else 0
    
    confidence = base + length_bonus + structure_bonus - title_penalty
    return min(0.95, max(0.3, confidence))


def infer_modules(pages: Dict[str, str]) -> List[Module]:
    """
    Infer modules and submodules from crawled pages.
    
    Improved algorithm:
    1. Extract sections from all pages
    2. Group by normalized titles, merging similar ones
    3. Identify top-level modules (level 1-2 headings)
    4. Identify submodules (level 3-4 headings under modules)
    5. Generate descriptions and confidence scores
    """
    if not pages:
        logger.warning("No pages provided for inference")
        return []
    
    module_sections: Dict[str, List[Section]] = defaultdict(list)
    section_sources: Dict[str, Set[str]] = defaultdict(set)
    all_titles: List[str] = []

    # Extract sections from all pages
    for url, html in pages.items():
        try:
            sections = extract_sections(html)
            grouped = infer_from_sections(sections, url)
            for title, secs in grouped.items():
                # Only consider level 1-2 sections as potential modules
                valid_secs = [s for s in secs if s.level <= 2]
                if valid_secs:
                    module_sections[title].extend(valid_secs)
                    section_sources[title].add(url)
                    all_titles.append(title)
        except Exception as e:
            logger.warning("Failed to extract sections from %s: %s", url, e)
            continue

    if not module_sections:
        logger.warning("No valid modules found")
        return []

    # Merge similar titles
    title_mapping = merge_similar_titles(list(module_sections.keys()))
    
    # Reorganize by canonical titles
    merged_modules: Dict[str, List[Section]] = defaultdict(list)
    merged_sources: Dict[str, Set[str]] = defaultdict(set)
    
    for orig_title, sections in module_sections.items():
        canonical = title_mapping[orig_title]
        merged_modules[canonical].extend(sections)
        merged_sources[canonical].update(section_sources[orig_title])

    # Build modules with submodules
    modules: List[Module] = []
    for title, secs in merged_modules.items():
        if not secs:
            continue
        
        # Use the first section as primary
        top_section = secs[0]
        
        # Collect unique submodules from all sections
        submodule_map: Dict[str, Submodule] = {}
        for section in secs:
            for child in section.children:
                if child.level <= 4 and is_valid_module_title(child.title):
                    # Deduplicate submodules by title
                    if child.title not in submodule_map:
                        submodule_map[child.title] = Submodule(
                            name=child.title,
                            description=submodule_description(child),
                            source_urls=dedupe_preserve_order(list(merged_sources[title])),
                            confidence=calculate_confidence(child, is_module=False),
                        )
        
        modules.append(
            Module(
                name=title,
                description=module_description(top_section),
                submodules=list(submodule_map.values()),
                source_urls=dedupe_preserve_order(list(merged_sources[title])),
                confidence=calculate_confidence(top_section, is_module=True),
            )
        )
    
    # Sort by confidence (highest first)
    modules.sort(key=lambda m: m.confidence, reverse=True)
    
    logger.info("Inferred %d modules from %d pages", len(modules), len(pages))
    return modules

