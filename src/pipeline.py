import argparse
import json
from typing import Dict, List, Optional

from .cache import PersistentCache
from .crawler import Crawler
from .inference import infer_modules
from .models import ExtractionResult
from .utils import dedupe_preserve_order, get_logger

logger = get_logger()


def run_extraction(
    urls: List[str],
    max_pages: int = 40,
    max_depth: int = 3,
    use_cache: bool = True,
) -> ExtractionResult:
    """Run the full extraction pipeline with error handling."""
    if not urls:
        logger.error("No URLs provided")
        return ExtractionResult(modules=[])
    
    try:
        persistent_cache = PersistentCache() if use_cache else None
        crawler = Crawler(
            max_pages=max_pages,
            max_depth=max_depth,
            persistent_cache=persistent_cache,
        )
        pages = crawler.crawl(dedupe_preserve_order(urls))
        
        if not pages:
            logger.warning("No pages were successfully crawled")
            return ExtractionResult(modules=[])
        
        html_map: Dict[str, str] = {page.url: page.html for page in pages if page.html}
        
        if not html_map:
            logger.warning("No valid HTML content extracted")
            return ExtractionResult(modules=[])
        
        modules = infer_modules(html_map)
        logger.info("Extraction complete: %d modules found", len(modules))
        return ExtractionResult(modules=modules)
    except Exception as e:
        logger.error("Extraction failed: %s", e, exc_info=True)
        return ExtractionResult(modules=[])


def main() -> None:
    parser = argparse.ArgumentParser(description="Pulse module extraction agent")
    parser.add_argument(
        "--urls",
        nargs="+",
        required=True,
        help="One or more help/documentation URLs",
    )
    parser.add_argument("--max-pages", type=int, default=40, help="Maximum pages to crawl")
    parser.add_argument("--max-depth", type=int, default=3, help="Maximum crawl depth")
    parser.add_argument("--output", type=str, default="", help="Optional path to write JSON")
    args = parser.parse_args()

    result = run_extraction(args.urls, max_pages=args.max_pages, max_depth=args.max_depth)
    payload = {
        "modules": [
            {
                "name": m.name,
                "description": m.description,
                "confidence": m.confidence,
                "source_urls": m.source_urls,
                "submodules": [
                    {
                        "name": sm.name,
                        "description": sm.description,
                        "confidence": sm.confidence,
                        "source_urls": sm.source_urls,
                    }
                    for sm in m.submodules
                ],
            }
            for m in result.modules
        ]
    }
    json_str = json.dumps(payload, indent=2, ensure_ascii=False)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(json_str)
        logger.info("Wrote output to %s", args.output)
    else:
        print(json_str)


if __name__ == "__main__":
    main()

