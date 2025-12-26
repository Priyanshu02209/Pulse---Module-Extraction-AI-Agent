# Quick Start Guide

## Installation (5 minutes)

### Step 1: Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd Pulsegen

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Run the Application

**Option A: Streamlit UI (Recommended for first-time users)**

```bash
streamlit run src/app.py
```

Open `http://localhost:8501` in your browser.

**Option B: API Server**

```bash
# Windows
python -m uvicorn src.api:app --host 0.0.0.0 --port 8000 --reload

# Or use the script
run_api.bat  # Windows
./run_api.sh  # Linux/Mac
```

API docs available at `http://localhost:8000/docs`

**Option C: Command Line**

```bash
python -m src.pipeline --urls https://support.neo.space/hc/en-us --max-pages 20 --output result.json
```

## First Extraction

### Using Streamlit UI

1. Open `http://localhost:8501`
2. Paste a URL in the text area:
   ```
   https://support.neo.space/hc/en-us
   ```
3. Click "Run Extraction"
4. Wait for results (usually 30-60 seconds)
5. Review modules and submodules
6. Click "Download JSON" to save results

### Using API

```bash
curl -X POST "http://localhost:8000/extract" \
  -H "Content-Type: application/json" \
  -d '{
    "urls": ["https://support.neo.space/hc/en-us"],
    "max_pages": 20,
    "max_depth": 2
  }'
```

### Using CLI

```bash
python -m src.pipeline \
  --urls https://support.neo.space/hc/en-us \
  --max-pages 20 \
  --max-depth 2 \
  --output my_results.json
```

## Testing

Run the test suite:

```bash
pytest tests/ -v
```

Run sample extraction on 4 URLs:

```bash
python samples/run_samples.py
```

Check results in `samples/output/sample_output.json`

## Docker Quick Start

```bash
# Build image
docker build -t pulsegen .

# Run UI
docker run -p 8501:8501 pulsegen

# Run API
docker run -p 8000:8000 pulsegen python -m uvicorn src.api:app --host 0.0.0.0 --port 8000

# Or use docker-compose for both
docker-compose up
```

## Troubleshooting

### Issue: "ModuleNotFoundError"

**Solution**: Make sure virtual environment is activated and dependencies are installed:
```bash
pip install -r requirements.txt
```

### Issue: "Connection timeout" or "Failed to fetch"

**Solution**: 
- Check your internet connection
- Verify the URL is accessible
- Try reducing `max_pages` or `max_depth`
- Some sites may block automated requests

### Issue: "No modules found"

**Solution**:
- The site may use JavaScript to render content (not supported)
- Try a different documentation site
- Increase `max_pages` to crawl more content
- Check the logs for errors

### Issue: Port already in use

**Solution**: 
- Change the port: `streamlit run src/app.py --server.port 8502`
- Or stop the process using the port

## Next Steps

1. Read the [README.md](README.md) for detailed documentation
2. Check [ARCHITECTURE.md](ARCHITECTURE.md) for technical details
3. Review sample outputs in `samples/output/`
4. Customize extraction parameters for your use case

## Getting Help

- Check the logs for error messages
- Review the test files for usage examples
- Read the code comments for implementation details

