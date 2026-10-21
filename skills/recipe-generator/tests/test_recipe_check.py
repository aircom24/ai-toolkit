"""Tests for the recipe-generator check tool."""

from __future__ import annotations

import contextlib
import copy
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path

TOOL = Path(__file__).resolve().parent.parent / "tools" / "check_recipe.py"
spec = importlib.util.spec_from_file_location("check_recipe", TOOL)
check_recipe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check_recipe)

VALID = {
    "title": "Test recipe",
    "date": "2026-10-18",
    "meta": {"prep_time": "", "total_time": "10 min", "servings": "2"},
    "tools": ["miska"],
    "ingredients": ["180 g mąki"],
    "description": ["Krótki opis."],
    "steps": ["Nagrzej piekarnik do 180 °C."],
    "sources": ["Example cookbook, https://example.com"],
}


def run_check(data: dict) -> tuple[int, str]:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "recipe.json"
        path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = check_recipe.main([str(path)])
    return code, output.getvalue()


def with_change(**changes) -> dict:
    data = copy.deepcopy(VALID)
    data.update(changes)
    return data


class RecipeCheckTests(unittest.TestCase):
    def test_valid_recipe_passes(self) -> None:
        code, output = run_check(VALID)
        self.assertEqual(code, 0, output)
        self.assertIn("0 error(s)", output)

    def test_leftover_placeholder_is_an_error(self) -> None:
        code, output = run_check(with_change(steps=["Dodaj [nazwa składnika]."]))
        self.assertEqual(code, 1)
        self.assertIn("unfilled template placeholder", output)

    def test_note_about_source_is_an_error(self) -> None:
        code, output = run_check(with_change(description=["Czas aktywnej pracy: źródło nie podaje."]))
        self.assertEqual(code, 1)
        self.assertIn("note about the source or a gap", output)

    def test_empty_steps_is_an_error(self) -> None:
        code, output = run_check(with_change(steps=[]))
        self.assertEqual(code, 1)
        self.assertIn("'steps' is empty", output)

    def test_status_is_not_checked_any_more(self) -> None:
        code, output = run_check(with_change(status="Dobry"))
        self.assertEqual(code, 0, output)

    def test_date_must_be_iso(self) -> None:
        code, output = run_check(with_change(date="18.10.2026"))
        self.assertEqual(code, 1)
        self.assertIn("RRRR-MM-DD", output)

    def test_invalid_json_is_an_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "recipe.json"
            path.write_text("{not json", encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(check_recipe.main([str(path)]), 1)


if __name__ == "__main__":
    unittest.main()
