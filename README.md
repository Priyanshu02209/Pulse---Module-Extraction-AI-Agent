# Pulse - Module Extraction AI Agent

An AI-powered Streamlit application that extracts structured information from documentation-based help websites. The tool identifies key modules and submodules and generates detailed, accurate descriptions for each—entirely based on the content from the URLs provided.

## Overview

Video : https://drive.google.com/file/d/1DKdiZS9dAyiZbw43ENzUj7gFKa-s63tb/view?usp=sharing

This project crawls help documentation websites, analyzes their structure and content, and automatically infers:
- **Modules**: Major documentation categories (e.g., "User Management", "API Documentation")
- **Submodules**: Specific functionalities under each module (e.g., "Create User", "Delete Account")
- **Descriptions**: Concise summaries generated from the actual documentation content
- **Confidence Scores**: Quality indicators for each extracted module/submodule

## Features

-  **Intelligent Crawling**: Breadth-first crawling with depth/page limits, URL normalization, and redirect handling
-  **Content Extraction**: Strips navigation/headers/footers, preserves document hierarchy
-  **Module Inference**: Heuristic-based detection of modules and submodules from HTML structure
-  **Description Generation**: Automatic summarization from extracted content
-  **Persistent Caching**: Disk-based cache to avoid re-fetching pages across runs
-  **Streamlit UI**: User-friendly web interface for interactive extraction
-  **REST API**: FastAPI endpoint for programmatic access
-  **Docker Support**: Containerized deployment with docker-compose
-  **Unit Tests**: Comprehensive test suite for core functionality

## Quick Start

### Prerequisites

- Python 3.10 or higher
- pip package manager

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd Pulsegen
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv .venv
   
   # Windows
   .venv\Scripts\activate
   
   # Linux/Mac
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Streamlit UI

```bash
streamlit run src/app.py
```

Open your browser to `http://localhost:8501` and:
1. Paste one or more help documentation URLs (comma or newline separated)
2. Adjust max pages and depth if needed
3. Click "Run Extraction"
4. View results and download as JSON

### Running the API Server

```bash
python -m uvicorn src.api:app --host 0.0.0.0 --port 8000
```

API documentation available at `http://localhost:8000/docs`

**Example API Request**:
```bash
curl -X POST "http://localhost:8000/extract" \
  -H "Content-Type: application/json" \
  -d '{
    "urls": ["https://support.neo.space/hc/en-us"],
    "max_pages": 40,
    "max_depth": 3
  }'
```

### CLI Usage

```bash
python -m src.pipeline --urls https://support.neo.space/hc/en-us https://wordpress.org/documentation/ --max-pages 40 --max-depth 3 --output output.json
```

## Docker Deployment

### Build and Run

```bash
# Build the image
docker build -t pulsegen .

# Run Streamlit UI
docker run -p 8501:8501 pulsegen

# Run API server
docker run -p 8000:8000 pulsegen python -m uvicorn src.api:app --host 0.0.0.0 --port 8000
```

### Docker Compose

```bash
# Start both UI and API
docker-compose up

# UI: http://localhost:8501
# API: http://localhost:8000
```

## Testing

Run the test suite:

```bash
pytest tests/ -v
```

Run with coverage:

```bash
pytest tests/ --cov=src --cov-report=html
```

### Sample Extraction

Test on the four suggested B2B documentation sites:

```bash
python samples/run_samples.py
```

Results are written to `samples/output/sample_output.json`.

## Architecture

### Core Components

1. **Crawler** (`src/crawler.py`):
   - Breadth-first web crawling
   - URL normalization and domain filtering
   - Binary content detection
   - Redirect handling
   - Persistent caching support

2. **Cleaner** (`src/cleaner.py`):
   - HTML noise removal (scripts, styles, nav, footer)
   - Text block extraction
   - Section hierarchy building
   - Content summarization

3. **Inference** (`src/inference.py`):
   - Module/submodule detection from headings
   - Title normalization and deduplication
   - Description generation
   - Confidence scoring

4. **Pipeline** (`src/pipeline.py`):
   - Orchestrates crawl → parse → inference
   - Error handling and logging
   - CLI interface

5. **Cache** (`src/cache.py`):
   - Persistent disk-based caching
   - SHA-256 URL hashing for filenames
   - JSON serialization

6. **API** (`src/api.py`):
   - FastAPI REST endpoint
   - Request/response validation
   - Cache management endpoints

7. **Streamlit App** (`src/app.py`):
   - Interactive web UI
   - Real-time extraction
   - JSON download

## Output Format

The tool generates JSON in the following structure:

```json
{
  "modules": [
    {
      "name": "User Management",
      "description": "Manage users, roles, and permissions in the system.",
      "confidence": 0.85,
      "source_urls": ["https://example.com/docs/users"],
      "submodules": [
        {
          "name": "Create User",
          "description": "How to create a new user account.",
          "confidence": 0.75,
          "source_urls": ["https://example.com/docs/users/create"]
        }
      ]
    }
  ]
}
```

## Design Rationale

### Approach

1. **Heuristic-Based Inference**: Uses HTML structure (heading hierarchy) rather than ML models to keep the solution lightweight and deterministic.

2. **Content-Only Descriptions**: All descriptions are generated from actual documentation content, ensuring accuracy and relevance.

3. **Modular Architecture**: Clean separation of concerns allows easy extension (e.g., adding ML summarization, different crawlers).

4. **Resilient Crawling**: Handles edge cases like redirects, broken links, binary content, and rate limiting gracefully.

### Assumptions

- Documentation sites use semantic HTML with proper heading hierarchy (h1-h4)
- Content is primarily text-based (not heavily image/video dependent)
- Sites are accessible via HTTP/HTTPS (no authentication required)
- Reasonable crawl limits prevent excessive resource usage

### Limitations

1. **JavaScript-Heavy Sites**: Single-page applications (SPAs) that render content client-side may not be fully crawled. Consider using Playwright/Selenium for such sites.

2. **PDF/Binary Content**: Only HTML pages are processed. PDFs and other binary formats are skipped.

3. **Authentication**: Sites requiring login are not supported in the current implementation.

4. **Rate Limiting**: No built-in rate limiting; respect robots.txt and site policies.

5. **Language**: Optimized for English content; may need adjustments for other languages.

6. **Heuristic Summarization**: Descriptions use simple sentence extraction; ML-based summarization would improve quality but adds complexity.

## Configuration

### Environment Variables

- `PULSE_DEFAULT_URLS`: Default URLs for Streamlit UI (newline-separated)
- `PULSE_CACHE_DIR`: Cache directory path (default: `cache/`)

### Crawler Parameters

- `max_pages`: Maximum pages to crawl (default: 40)
- `max_depth`: Maximum crawl depth (default: 3)
- `timeout`: Request timeout in seconds (default: 12)

## Performance Considerations

- **Caching**: Enable persistent cache to avoid re-fetching pages across runs
- **Parallel Crawling**: Current implementation is sequential; parallel fetching would improve speed
- **Memory**: Large sites may consume significant memory; adjust `max_pages` accordingly

## Known Issues & Future Improvements

### Planned Enhancements

- [ ] Parallel/async crawling for better performance
- [ ] ML-based summarization (e.g., using transformers)
- [ ] Support for authenticated sites
- [ ] Playwright integration for JavaScript-heavy sites
- [ ] Rate limiting and robots.txt respect
- [ ] Multi-language support
- [ ] Export to other formats (CSV, Markdown)

### Bug Reports

Please report issues via GitHub issues with:
- URL(s) that failed
- Error messages/logs
- Expected vs actual behavior

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

[Specify your license here]

## Acknowledgments

Built for Pulsegen company assignment. Uses:
- [Streamlit](https://streamlit.io/) for UI
- [FastAPI](https://fastapi.tiangolo.com/) for API
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) for HTML parsing
- [Requests](https://requests.readthedocs.io/) for HTTP client

## Contact

[Your contact information]
