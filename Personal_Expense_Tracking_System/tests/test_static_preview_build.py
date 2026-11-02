import re
import sys
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent.parent
REPOSITORY_DIR = PROJECT_DIR.parent
if str(REPOSITORY_DIR) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_DIR))

from build_static_preview import PAGES, build


class _PageInspector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.enabled_controls = []
        self.forms = 0
        self.links = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "form":
            self.forms += 1
        if tag in {"input", "select", "textarea", "button"}:
            if "disabled" not in attributes:
                self.enabled_controls.append(tag)
        if tag == "a":
            self.links.append(attributes.get("href", ""))


class StaticPreviewBuildTests(unittest.TestCase):
    def test_build_renders_read_only_pages_and_assets(self):
        with tempfile.TemporaryDirectory(prefix="expense-preview-test-") as temp_dir:
            output = Path(temp_dir)
            build(output)

            for relative_path in PAGES.values():
                page = output / relative_path
                self.assertTrue(page.is_file(), relative_path)
                html = page.read_text(encoding="utf-8")
                self.assertIn("Static preview", html)
                inspector = _PageInspector()
                inspector.feed(html)
                self.assertFalse(inspector.enabled_controls, relative_path)
                self.assertGreater(inspector.forms, 0)
                self.assertFalse(
                    any(re.search(r"/export\.csv|/expenses/\d+/edit", href)
                        for href in inspector.links),
                    relative_path,
                )

            dashboard = (output / PAGES["/"]).read_text(encoding="utf-8")
            self.assertIn('data-static-preview="true"', dashboard)
            self.assertTrue((output / "static" / "css" / "style.css").is_file())
            self.assertTrue((output / "static" / "js" / "app.js").is_file())


if __name__ == "__main__":
    unittest.main()
