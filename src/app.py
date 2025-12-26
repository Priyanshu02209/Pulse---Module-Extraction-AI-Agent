import json
import os
from typing import List

import streamlit as st

# Use absolute imports so running via `streamlit run src/app.py` works
from src.pipeline import run_extraction
from src.utils import dedupe_preserve_order


def parse_input_urls(raw: str) -> List[str]:
    parts = [p.strip() for chunk in raw.splitlines() for p in chunk.split(",")]
    return [p for p in parts if p]


st.set_page_config(page_title="Pulse Module Extraction Agent", layout="wide")
st.title("Pulse - Module Extraction AI Agent")
st.write(
    "Crawl help documentation URLs to infer modules, submodules, and descriptions using only the source content."
)

default_urls = os.environ.get(
    "PULSE_DEFAULT_URLS",
    "https://support.neo.space/hc/en-us\nhttps://wordpress.org/documentation/",
)

url_input = st.text_area("Enter one or more URLs", value=default_urls, height=120)
col1, col2 = st.columns(2)
max_pages = col1.number_input("Max pages to crawl", min_value=5, max_value=200, value=40, step=5)
max_depth = col2.number_input("Max depth", min_value=1, max_value=6, value=3, step=1)

if st.button("Run Extraction", type="primary"):
    urls = dedupe_preserve_order(parse_input_urls(url_input))
    if not urls:
        st.error("Please enter at least one URL.")
    else:
        with st.spinner("Crawling and extracting..."):
            result = run_extraction(urls, max_pages=max_pages, max_depth=max_depth)
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
        st.success(f"Extraction complete. Found {len(result.modules)} modules.")
        st.json(payload)
        st.download_button(
            label="Download JSON",
            data=json.dumps(payload, indent=2, ensure_ascii=False),
            file_name="pulse_modules.json",
            mime="application/json",
        )

