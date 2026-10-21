"""Tests for the recipe-generator index tool."""

from __future__ import annotations

import contextlib
import importlib.util
import io
import tempfile
import unittest
from pathlib import Path

TOOL = Path(__file__).resolve().parent.parent / "tools" / "update_index.py"
spec = importlib.util.spec_from_file_location("update_index", TOOL)
update_index = importlib.util.module_from_spec(spec)
spec.loader.exec_module(update_index)


class IndexTests(unittest.TestCase):
    def test_lists_recipe_pdfs_sorted_with_title_and_date(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            (folder / "wino-z-winogron.pdf").write_bytes(b"%PDF")
            (folder / "ogorki-kiszone.pdf").write_bytes(b"%PDF")
            (folder / "notatki.md").write_text("working file", encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(update_index.main([str(folder)]), 0)
            index = (folder / "README.md").read_text(encoding="utf-8")

        self.assertIn("# Przepisy kuchenne", index)
        self.assertIn("| Przepis | Ostatnia zmiana |", index)
        self.assertIn("| [Ogorki kiszone](ogorki-kiszone.pdf) |", index)
        self.assertIn("| [Wino z winogron](wino-z-winogron.pdf) |", index)
        self.assertLess(index.index("Ogorki"), index.index("Wino"))
        self.assertNotIn("notatki", index)

    def test_empty_folder_gets_placeholder_text(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with contextlib.redirect_stdout(io.StringIO()):
                update_index.main([tmp])
            index = (Path(tmp) / "README.md").read_text(encoding="utf-8")
        self.assertIn("Brak przepisów w tym katalogu.", index)

    def test_index_is_regenerated_not_appended(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            (folder / "ogorki-kiszone.pdf").write_bytes(b"%PDF")
            with contextlib.redirect_stdout(io.StringIO()):
                update_index.main([str(folder)])
                update_index.main([str(folder)])
            index = (folder / "README.md").read_text(encoding="utf-8")
        self.assertEqual(index.count("| [Ogorki kiszone]"), 1)

    def test_missing_folder_is_a_usage_error(self) -> None:
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(update_index.main(["/nonexistent-recipe-folder"]), 2)


if __name__ == "__main__":
    unittest.main()
