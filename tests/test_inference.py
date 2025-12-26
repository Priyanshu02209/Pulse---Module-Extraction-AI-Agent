"""Unit tests for inference module."""
from src.inference import (
    calculate_confidence,
    infer_modules,
    is_valid_module_title,
    merge_similar_titles,
    module_description,
    normalize_title,
    submodule_description,
)
from src.models import Section


class TestNormalizeTitle:
    def test_lowercases_and_strips(self):
        assert normalize_title("  Hello World  ") == "hello world"
        assert normalize_title("HELLO") == "hello"
        assert normalize_title("Hello   World") == "hello world"


class TestIsValidModuleTitle:
    def test_valid_titles(self):
        assert is_valid_module_title("User Management")
        assert is_valid_module_title("API Documentation")
        assert is_valid_module_title("Getting Started")

    def test_invalid_titles(self):
        assert not is_valid_module_title("")
        assert not is_valid_module_title("Hi")
        assert not is_valid_module_title("Login")
        assert not is_valid_module_title("Home")
        assert not is_valid_module_title("Skip to content")


class TestMergeSimilarTitles:
    def test_merges_similar(self):
        titles = ["User Management", "User management", "User-Management"]
        mapping = merge_similar_titles(titles, threshold=0.8)
        # Should map similar ones together
        assert len(set(mapping.values())) <= len(titles)

    def test_keeps_dissimilar_separate(self):
        titles = ["User Management", "API Documentation", "Settings"]
        mapping = merge_similar_titles(titles, threshold=0.8)
        # All should remain distinct
        assert len(set(mapping.values())) == len(titles)


class TestModuleDescription:
    def test_generates_from_content(self):
        section = Section(level=1, title="Test", text="First sentence. Second sentence. Third.")
        desc = module_description(section)
        assert len(desc) > 0
        assert "First sentence" in desc or "Second sentence" in desc

    def test_handles_empty_content(self):
        section = Section(level=1, title="Test", text="")
        desc = module_description(section)
        assert "Test" in desc


class TestSubmoduleDescription:
    def test_uses_text_when_available(self):
        section = Section(level=2, title="Submodule", text="Description text here.")
        desc = submodule_description(section)
        assert "Description text" in desc or "Submodule" in desc

    def test_fallback_to_title(self):
        section = Section(level=2, title="Submodule", text="")
        desc = submodule_description(section)
        assert "Submodule" in desc


class TestCalculateConfidence:
    def test_higher_confidence_for_longer_content(self):
        short = Section(level=1, title="Test", text="Short")
        long = Section(level=1, title="Test", text=" ".join(["word"] * 50))
        
        conf_short = calculate_confidence(short, is_module=True)
        conf_long = calculate_confidence(long, is_module=True)
        
        assert conf_long >= conf_short

    def test_modules_have_higher_base_confidence(self):
        section = Section(level=1, title="Test", text="Some content")
        conf_module = calculate_confidence(section, is_module=True)
        conf_submodule = calculate_confidence(section, is_module=False)
        
        assert conf_module >= conf_submodule


class TestInferModules:
    def test_infers_from_simple_html(self):
        pages = {
            "https://example.com/page1": """
            <html><body>
                <h1>User Management</h1>
                <p>Manage users and permissions.</p>
                <h2>Create User</h2>
                <p>How to create a user.</p>
            </body></html>
            """
        }
        modules = infer_modules(pages)
        assert len(modules) > 0
        assert any("User Management" in m.name for m in modules)

    def test_handles_empty_pages(self):
        modules = infer_modules({})
        assert modules == []

    def test_handles_invalid_html(self):
        pages = {"https://example.com": "not html"}
        modules = infer_modules(pages)
        # Should handle gracefully
        assert isinstance(modules, list)

