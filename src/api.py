"""FastAPI endpoint for Pulse module extraction."""
import json
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, HttpUrl

from .cache import PersistentCache
from .crawler import Crawler
from .pipeline import run_extraction

app = FastAPI(
    title="Pulse Module Extraction API",
    description="API for extracting modules and submodules from documentation websites",
    version="1.0.0",
)


class ExtractionRequest(BaseModel):
    urls: List[HttpUrl]
    max_pages: Optional[int] = 40
    max_depth: Optional[int] = 3
    use_cache: Optional[bool] = True


class ExtractionResponse(BaseModel):
    modules: List[dict]
    stats: dict


@app.get("/")
def root():
    """API root endpoint."""
    return {
        "name": "Pulse Module Extraction API",
        "version": "1.0.0",
        "endpoints": {
            "/extract": "POST - Extract modules from URLs",
            "/health": "GET - Health check",
            "/cache/stats": "GET - Cache statistics",
            "/cache/clear": "POST - Clear cache",
        },
    }


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/extract", response_model=ExtractionResponse)
def extract_modules(request: ExtractionRequest):
    """
    Extract modules and submodules from provided URLs.
    
    Args:
        request: Extraction request with URLs and options
        
    Returns:
        ExtractionResponse with modules and statistics
    """
    try:
        # Convert HttpUrl objects to strings
        url_strings = [str(url) for url in request.urls]
        
        if not url_strings:
            raise HTTPException(status_code=400, detail="At least one URL is required")
        
        # Setup persistent cache if enabled
        persistent_cache = None
        if request.use_cache:
            persistent_cache = PersistentCache()
        
        # Run extraction
        result = run_extraction(
            url_strings,
            max_pages=request.max_pages or 40,
            max_depth=request.max_depth or 3,
        )
        
        # Build response payload
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
        
        stats = {
            "total_modules": len(result.modules),
            "total_submodules": sum(len(m.submodules) for m in result.modules),
            "urls_processed": len(url_strings),
        }
        
        return ExtractionResponse(modules=payload["modules"], stats=stats)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")


@app.get("/cache/stats")
def cache_stats():
    """Get cache statistics."""
    cache = PersistentCache()
    return {
        "cached_items": cache.size(),
        "cache_dir": str(cache.cache_dir),
    }


@app.post("/cache/clear")
def clear_cache():
    """Clear the persistent cache."""
    cache = PersistentCache()
    cache.clear()
    return {"message": "Cache cleared successfully"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

