"""Tests for the recipe-generator card renderer (HTML output, binder layout)."""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path

TOOL = Path(__file__).resolve().parent.parent / "tools" / "render_card.py"
spec = importlib.util.spec_from_file_location("render_card", TOOL)
render_card = importlib.util.module_from_spec(spec)
spec.loader.exec_module(render_card)

DATA = {
    "title": "Ciasto & Co",
    "date": "2026-10-18",
    "meta": {"prep_time": "10 min", "total_time": "1 h", "servings": "4"},
    "tools": ["miska 50% pojemności"],
    "ingredients": ["180 g mąki"],
    "optional_ingredients": "",
    "description": ["Krótki opis."],
    "steps": ["Wymieszaj składniki."],
    "control_point": "",
    "storage": "",
    "nutrition": {"basis": "na porcję", "energy_kcal": "320"},
    "sources": [],
    "photo": "",
}


class ValidationTests(unittest.TestCase):
    def test_valid_data_has_no_errors(self) -> None:
        self.assertEqual(render_card.validate(DATA), [])

    def test_missing_title_and_steps_are_errors(self) -> None:
        errors = render_card.validate({**DATA, "title": "", "steps": []})
        self.assertIn("title is empty", errors)
        self.assertIn("steps are empty", errors)

    def test_bad_date_is_an_error(self) -> None:
        self.assertIn(
            "date must be in RRRR-MM-DD format",
            render_card.validate({**DATA, "date": "18.10.2026"}),
        )


class StepGroupTests(unittest.TestCase):
    GROUPED = {**DATA, "steps": [
        {"heading": "Dzień 0", "steps": ["Przebierz winogrona.", "Zgnieć jagody."]},
        "Odciśnij sok.",
    ]}

    def test_grouped_steps_are_valid(self) -> None:
        self.assertEqual(render_card.validate(self.GROUPED), [])

    def test_group_without_heading_or_steps_is_an_error(self) -> None:
        bad = {**DATA, "steps": [{"heading": "", "steps": ["Krok."]}, {"heading": "Dzień 3", "steps": []}]}
        errors = render_card.validate(bad)
        self.assertIn("each step group needs a heading and at least one step", errors)

    def test_only_empty_groups_count_as_no_steps(self) -> None:
        errors = render_card.validate({**DATA, "steps": [{"heading": "Dzień 0", "steps": []}]})
        self.assertIn("steps are empty", errors)

    def test_binder_renders_headings_without_numbering(self) -> None:
        content = render_card.TEMPLATES["binder"].read_text(encoding="utf-8")
        self.assertIn("'group', s.heading", content)
        self.assertIn(".steps li.group::before { content: none; }", content)


class LayoutTests(unittest.TestCase):
    def test_binder_is_the_only_template(self) -> None:
        self.assertEqual(sorted(render_card.TEMPLATES), ["binder"])
        self.assertTrue(render_card.TEMPLATES["binder"].is_file())

    def test_sources_are_printed_in_the_bottom_margin_of_every_page(self) -> None:
        content = render_card.TEMPLATES["binder"].read_text(encoding="utf-8")
        self.assertIn("@bottom-center", content)
        self.assertIn(".footer { display: none; }", content)

    def test_binder_hides_nutrition_section_when_no_values(self) -> None:
        # The section is hidden by the template itself, so an empty nutrition object leaves no section.
        content = render_card.TEMPLATES["binder"].read_text(encoding="utf-8")
        self.assertIn("nutrition.style.display = 'none'", content)


class InjectTests(unittest.TestCase):
    def test_inject_contains_title_and_page_size(self) -> None:
        html = render_card.inject(DATA, "A5", None, "binder")
        self.assertIn("Ciasto & Co", html)  # json.dumps does not escape &
        self.assertIn("A5 portrait", html)
        self.assertNotIn("<!-- RECIPE_DATA_PLACEHOLDER -->", html)
        self.assertIn("window.RECIPE =", html)

    def test_inject_includes_photo_name(self) -> None:
        html = render_card.inject(DATA, "A5", "moje-ciasto.jpg", "binder")
        self.assertIn("moje-ciasto.jpg", html)

    def test_inject_a4_sets_page_size(self) -> None:
        html = render_card.inject(DATA, "A4", None, "binder")
        self.assertIn("A4 portrait", html)

    def test_nutrition_value_present_in_injected_json(self) -> None:
        html = render_card.inject(DATA, "A5", None, "binder")
        self.assertIn("320", html)

    def test_nutrition_absent_when_empty(self) -> None:
        empty = {**DATA, "nutrition": {}}
        html = render_card.inject(empty, "A5", None, "binder")
        # injected JSON contains nutrition key but with empty dict
        self.assertIn('"nutrition": {}', html)


class EndToEndTests(unittest.TestCase):
    def test_renders_html_binder(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            recipe = Path(tmp) / "recipe.json"
            recipe.write_text(json.dumps(DATA, ensure_ascii=False), encoding="utf-8")
            output = Path(tmp) / "segregator.html"
            with contextlib.redirect_stdout(io.StringIO()):
                code = render_card.main([str(recipe), str(output), "--template", "binder"])
            self.assertEqual(code, 0)
            content = output.read_text(encoding="utf-8")
            self.assertIn("<!doctype html>", content)
            self.assertIn("window.RECIPE =", content)
            self.assertIn('class="hole top"', content)

    def test_binder_is_default_template(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            recipe = Path(tmp) / "recipe.json"
            recipe.write_text(json.dumps(DATA, ensure_ascii=False), encoding="utf-8")
            output = Path(tmp) / "default.html"
            with contextlib.redirect_stdout(io.StringIO()):
                render_card.main([str(recipe), str(output)])
            self.assertIn('class="hole top"', output.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
