# Technical Architecture

## System Overview

Pulse Module Extraction Agent is a Python-based web crawler and content analyzer that extracts structured module/submodule information from documentation websites.

## Component Architecture

```
┌─────────────────┐
│  Streamlit UI   │  ──┐
│   (src/app.py)  │    │
└─────────────────┘    │
                       │
┌─────────────────┐    │    ┌──────────────┐
│   FastAPI API   │  ──┼───▶│   Pipeline   │
│   (src/api.py)  │    │    │(src/pipeline)│
└─────────────────┘    │    └──────┬───────┘
                       │           │
                       │           ▼
┌─────────────────┐    │    ┌──────────────┐
│   CLI Tool      │  ──┘    │   Crawler    │
│ (src/pipeline)  │         │(src/crawler) │
└─────────────────┘         └──────┬───────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
            ┌──────────┐    ┌──────────┐   ┌──────────┐
            │ Cleaner  │    │ Inference │   │  Cache   │
            │(cleaner) │    │(inference)│   │ (cache)  │
            └──────────┘    └──────────┘   └──────────┘
```

## Data Flow

1. **Input**: User provides one or more documentation URLs
2. **Crawling**: Crawler fetches pages, extracts links, follows them up to depth limit
3. **Cleaning**: HTML is stripped of noise, sections are extracted with hierarchy
4. **Inference**: Modules/submodules are inferred from heading structure
5. **Output**: Structured JSON with modules, submodules, descriptions, confidence scores

## Key Design Decisions

### 1. Heuristic-Based Inference

**Decision**: Use HTML structure heuristics rather than ML models.

**Rationale**:
- No external dependencies (no API keys, no model downloads)
- Deterministic and explainable results
- Fast execution
- Works offline

**Trade-offs**:
- Less sophisticated than ML-based approaches
- May miss subtle patterns
- Requires well-structured HTML

### 2. Persistent Caching

**Decision**: Implement disk-based cache with JSON serialization.

**Rationale**:
- Avoids re-fetching pages across runs
- Reduces network load
- Faster subsequent runs
- Simple implementation

**Trade-offs**:
- Cache can become stale
- Disk space usage
- No automatic expiration (manual clear required)

### 3. Sequential Crawling

**Decision**: Crawl pages one at a time (not parallel).

**Rationale**:
- Simpler implementation
- Respects server resources
- Easier error handling
- No race conditions

**Trade-offs**:
- Slower for large sites
- Could be parallelized for better performance

### 4. Content-Only Descriptions

**Decision**: Generate descriptions only from extracted content, no external knowledge.

**Rationale**:
- Ensures accuracy (no hallucinations)
- Respects source material
- No API costs
- Works offline

**Trade-offs**:
- Descriptions may be less polished than LLM-generated
- Limited context (only what's on the page)

## Module Details

### Crawler (`src/crawler.py`)

**Responsibilities**:
- Fetch web pages via HTTP
- Extract links from HTML
- Follow links up to depth limit
- Handle redirects, errors, timeouts
- Integrate with persistent cache

**Key Methods**:
- `fetch(url)`: Fetch a single page
- `extract_links(base_url, html)`: Extract and normalize links
- `crawl(roots)`: Main crawling loop

**Error Handling**:
- Timeouts: Logged and skipped
- HTTP errors: Logged and skipped
- Invalid URLs: Filtered out
- Binary content: Detected and skipped

### Cleaner (`src/cleaner.py`)

**Responsibilities**:
- Remove HTML noise (scripts, styles, nav, footer)
- Extract text blocks (headings, paragraphs, lists)
- Build section hierarchy from heading levels
- Summarize text content

**Key Methods**:
- `strip_noise(html)`: Remove non-content elements
- `extract_text_blocks(soup)`: Extract structured text
- `build_sections(blocks)`: Create hierarchical sections
- `summarize_text(text)`: Generate summaries

**Assumptions**:
- HTML uses semantic headings (h1-h4)
- Content is primarily text-based
- Structure follows logical hierarchy

### Inference (`src/inference.py`)

**Responsibilities**:
- Identify modules from top-level headings
- Identify submodules from nested headings
- Merge similar/duplicate modules
- Generate descriptions
- Calculate confidence scores

**Key Methods**:
- `infer_modules(pages)`: Main inference logic
- `merge_similar_titles(titles)`: Deduplicate modules
- `calculate_confidence(section)`: Score quality
- `module_description(section)`: Generate module descriptions

**Heuristics**:
- Modules: Level 1-2 headings
- Submodules: Level 3-4 headings under modules
- Confidence: Based on content length, structure, title quality

### Cache (`src/cache.py`)

**Responsibilities**:
- Store fetched pages on disk
- Retrieve cached pages
- Manage cache directory
- Provide cache statistics

**Key Methods**:
- `get(url)`: Retrieve cached page
- `set(url, page)`: Store page in cache
- `clear()`: Remove all cached files
- `size()`: Count cached items

**Storage Format**:
- JSON files
- Filename: SHA-256 hash of URL
- Content: URL, HTML, status code

### Pipeline (`src/pipeline.py`)

**Responsibilities**:
- Orchestrate crawl → parse → inference
- Handle errors gracefully
- Provide CLI interface
- Format output as JSON

**Key Methods**:
- `run_extraction(urls, ...)`: Main pipeline function
- `main()`: CLI entry point

**Error Handling**:
- Empty URLs: Returns empty result
- Crawl failures: Logged, continues with available pages
- Inference failures: Logged, returns partial results

## Performance Characteristics

### Time Complexity

- **Crawling**: O(P × L) where P = pages, L = average links per page
- **Cleaning**: O(N) where N = HTML size
- **Inference**: O(M × S) where M = modules, S = submodules per module

### Space Complexity

- **In-memory**: O(P × H) where H = average HTML size
- **Disk cache**: O(P × H) (persistent)

### Typical Performance

- Small site (10-20 pages): 10-30 seconds
- Medium site (40-60 pages): 1-3 minutes
- Large site (100+ pages): 5-10+ minutes (depends on server response times)

## Scalability Considerations

### Current Limitations

1. **Sequential Crawling**: Single-threaded, could be parallelized
2. **Memory**: All pages loaded in memory; could stream for very large sites
3. **Cache**: No expiration; could add TTL-based expiration
4. **Rate Limiting**: No built-in rate limiting; could add delays

### Potential Improvements

1. **Async Crawling**: Use `aiohttp` for parallel requests
2. **Streaming**: Process pages as they're fetched, not all at once
3. **Distributed**: Use Celery/Redis for distributed crawling
4. **Incremental**: Only crawl new/changed pages

## Security Considerations

1. **Input Validation**: URLs are validated before fetching
2. **No Code Execution**: No `eval()` or dynamic code execution
3. **HTTPS**: Prefers HTTPS when available
4. **User-Agent**: Identifies itself as a crawler
5. **Rate Limiting**: Should respect robots.txt (not implemented yet)

## Testing Strategy

### Unit Tests

- `tests/test_cleaner.py`: HTML parsing, section building, summarization
- `tests/test_inference.py`: Module detection, title merging, confidence scoring
- `tests/test_utils.py`: URL normalization, domain matching, binary detection

### Integration Tests

- End-to-end pipeline tests (not yet implemented)
- API endpoint tests (not yet implemented)

### Manual Testing

- Run on sample URLs
- Verify output structure
- Check cache behavior

## Deployment Options

### 1. Local Development

```bash
streamlit run src/app.py
```

### 2. Docker

```bash
docker build -t pulsegen .
docker run -p 8501:8501 pulsegen
```

### 3. Docker Compose

```bash
docker-compose up
```

### 4. Cloud Deployment

- **Streamlit Cloud**: Deploy `src/app.py`
- **Heroku**: Use Procfile with `streamlit run`
- **AWS/GCP**: Container-based deployment

## Monitoring & Logging

- **Logging**: Python `logging` module, INFO level by default
- **Error Tracking**: Exceptions logged with stack traces
- **Metrics**: Cache size, pages crawled, modules found

## Future Enhancements

1. **ML Summarization**: Use transformers for better descriptions
2. **Playwright Integration**: Support JavaScript-heavy sites
3. **Rate Limiting**: Respect robots.txt and add delays
4. **Incremental Updates**: Only crawl changed pages
5. **Multi-language**: Support non-English documentation
6. **Export Formats**: CSV, Markdown, Excel exports

