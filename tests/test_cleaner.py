"""Unit tests for cleaner module."""
import pytest

from src.cleaner import (
    build_sections,
    extract_sections,
    extract_text_blocks,
    strip_noise,
    summarize_text,
)
from src.models import Section


class TestStripNoise:
    def test_removes_script_and_style(self):
        html = "<html><body><script>alert('hi')</script><p>Content</p><style>body {}</style></body></html>"
        soup = strip_noise(html)
        assert soup.find("script") is None
        assert soup.find("style") is None
        assert soup.find("p") is not None

    def test_removes_nav_footer(self):
        html = "<html><body><nav>Nav</nav><main>Content</main><footer>Footer</footer></body></html>"
        soup = strip_noise(html)
        assert soup.find("nav") is None
        assert soup.find("footer") is None
        assert soup.find("main") is not None


class TestExtractTextBlocks:
    def test_extracts_headings_and_paragraphs(self):
        html = "<html><body><h1>Title</h1><p>Paragraph</p><h2>Subtitle</h2></body></html>"
        soup = strip_noise(html)
        blocks = extract_text_blocks(soup)
        assert len(blocks) == 3
        assert blocks[0] == ("h1", "Title")
        assert blocks[1] == ("p", "Paragraph")
        assert blocks[2] == ("h2", "Subtitle")

    def test_skips_empty_blocks(self):
        html = "<html><body><h1></h1><p>Content</p><h2>  </h2></body></html>"
        soup = strip_noise(html)
        blocks = extract_text_blocks(soup)
        assert len(blocks) == 1
        assert blocks[0][0] == "p"


class TestBuildSections:
    def test_builds_hierarchy(self):
        blocks = [
            ("h1", "Module 1"),
            ("p", "Description"),
            ("h2", "Submodule 1.1"),
            ("p", "Sub description"),
            ("h1", "Module 2"),
        ]
        sections = build_sections(blocks)
        assert len(sections) == 2
        assert sections[0].title == "Module 1"
        assert len(sections[0].children) == 1
        assert sections[0].children[0].title == "Submodule 1.1"

    def test_handles_text_without_headings(self):
        blocks = [("p", "Some text")]
        sections = build_sections(blocks)
        assert len(sections) == 1
        assert sections[0].title == "Overview"
        assert sections[0].text == "Some text"


class TestSummarizeText:
    def test_summarizes_multiple_sentences(self):
        text = "First sentence. Second sentence. Third sentence. Fourth sentence."
        summary = summarize_text(text, max_sentences=2)
        assert "First sentence" in summary
        assert "Second sentence" in summary
        assert "Fourth sentence" not in summary

    def test_handles_short_text(self):
        text = "Short."
        summary = summarize_text(text)
        assert summary == "Short."

    def test_handles_empty_text(self):
        assert summarize_text("") == ""
        assert summarize_text("   ") == ""

    def test_fallback_to_char_limit(self):
        text = "A" * 500
        summary = summarize_text(text, max_sentences=1)
        assert len(summary) <= 203  # 200 + "..."


class TestExtractSections:
    def test_full_pipeline(self):
        html = """
        <html>
            <body>
                <h1>Main Title</h1>
                <p>Main description here.</p>
                <h2>Subsection</h2>
                <p>Subsection content.</p>
            </body>
        </html>
        """
        sections = extract_sections(html)
        assert len(sections) == 1
        assert sections[0].title == "Main Title"
        assert len(sections[0].children) == 1
        assert sections[0].children[0].title == "Subsection"

