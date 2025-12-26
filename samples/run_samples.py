import json
import os
from pathlib import Path

from src.pipeline import run_extraction


SAMPLE_URLS = [
    "https://support.neo.space/hc/en-us",
    "https://wordpress.org/documentation/",
    "https://help.zluri.com/",
    "https://www.chargebee.com/docs/2.0/",
]


def main() -> None:
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    result = run_extraction(SAMPLE_URLS, max_pages=60, max_depth=3)
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
    target = output_dir / "sample_output.json"
    target.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {target}")


if __name__ == "__main__":
    main()

