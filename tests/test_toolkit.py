"""Tests for the ai-toolkit validator and installer. Run: python3 -m unittest discover -s tests -v"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPTS = REPO / "scripts"
sys.path.insert(0, str(SCRIPTS))

from validate_structure import validate  # noqa: E402


def run_script(script: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / script), *args],
        capture_output=True,
        text=True,
    )


class ValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self.copy = self.tmp / "repo"
        shutil.copytree(REPO, self.copy, ignore=shutil.ignore_patterns(".git", "__pycache__"))
        self.skill_md = self.copy / "skills" / "example-skill" / "SKILL.md"

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp)

    def test_repository_is_valid(self) -> None:
        self.assertEqual(validate(REPO), [])

    def test_missing_description_is_reported(self) -> None:
        self.skill_md.write_text(self.skill_md.read_text(encoding="utf-8").replace("description:", "summary:", 1), encoding="utf-8")
        errors = validate(self.copy)
        self.assertTrue(any("missing field 'description'" in error for error in errors), errors)

    def test_link_outside_skill_is_reported(self) -> None:
        self.skill_md.write_text(self.skill_md.read_text(encoding="utf-8") + "\n[bad](../../README.md)\n", encoding="utf-8")
        errors = validate(self.copy)
        self.assertTrue(any("outside the skill directory" in error for error in errors), errors)

    def test_undeclared_shared_link_is_reported(self) -> None:
        self.skill_md.write_text(self.skill_md.read_text(encoding="utf-8") + "\n[x](_shared/rules/missing.md)\n", encoding="utf-8")
        errors = validate(self.copy)
        self.assertTrue(any("not declared in the skill's dependencies" in error for error in errors), errors)


class InstallerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self.target = self.tmp / "skills"
        self.skill = self.target / "example-skill"

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp)

    def install(self, *args: str) -> subprocess.CompletedProcess:
        return run_script("install_skills.py", "--target", str(self.target), *args)

    def uninstall(self, *args: str) -> subprocess.CompletedProcess:
        return run_script("uninstall_skills.py", "--target", str(self.target), *args)

    def test_install_creates_self_contained_skill(self) -> None:
        result = self.install("example-skill", "--yes")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue((self.skill / "SKILL.md").is_file())
        self.assertTrue((self.skill / "_shared" / "rules" / "accuracy.md").is_file())
        self.assertTrue((self.skill / "_shared" / "templates" / "document-template.md").is_file())
        self.assertTrue((self.skill / ".ai-toolkit-manifest.json").is_file())

    def test_dry_run_changes_nothing(self) -> None:
        result = self.install("example-skill", "--dry-run")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse(self.target.exists())

    def test_reinstall_is_up_to_date(self) -> None:
        self.assertEqual(self.install("example-skill", "--yes").returncode, 0)
        result = self.install("example-skill", "--yes")
        self.assertEqual(result.returncode, 0)
        self.assertIn("[up-to-date]", result.stdout)

    def test_local_change_is_conflict_and_force_keeps_backup(self) -> None:
        self.assertEqual(self.install("example-skill", "--yes").returncode, 0)
        (self.skill / "SKILL.md").write_text((self.skill / "SKILL.md").read_text(encoding="utf-8") + "\nmy note\n", encoding="utf-8")

        conflict = self.install("example-skill", "--yes")
        self.assertEqual(conflict.returncode, 2, conflict.stdout + conflict.stderr)
        self.assertIn("local changes", conflict.stdout)
        self.assertIn("my note", (self.skill / "SKILL.md").read_text(encoding="utf-8"))

        forced = self.install("example-skill", "--yes", "--force")
        self.assertEqual(forced.returncode, 0, forced.stdout + forced.stderr)
        self.assertNotIn("my note", (self.skill / "SKILL.md").read_text(encoding="utf-8"))
        backups = list((self.target.parent / "ai-toolkit-backups").glob("example-skill-*"))
        self.assertEqual(len(backups), 1)
        self.assertIn("my note", (backups[0] / "SKILL.md").read_text(encoding="utf-8"))

    def test_unmanaged_directory_is_refused(self) -> None:
        self.skill.mkdir(parents=True)
        (self.skill / "SKILL.md").write_text("user's own skill\n", encoding="utf-8")
        result = self.install("example-skill", "--yes")
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertEqual((self.skill / "SKILL.md").read_text(encoding="utf-8"), "user's own skill\n")

    def test_uninstall_removes_only_managed_skill(self) -> None:
        self.assertEqual(self.install("example-skill", "--yes").returncode, 0)
        self.assertEqual(self.uninstall("example-skill", "--yes").returncode, 0)
        self.assertFalse(self.skill.exists())

    def test_uninstall_refuses_unmanaged_directory(self) -> None:
        self.skill.mkdir(parents=True)
        (self.skill / "SKILL.md").write_text("user's own skill\n", encoding="utf-8")
        result = self.uninstall("example-skill", "--yes")
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertTrue(self.skill.exists())

    def test_non_interactive_install_without_yes_is_cancelled(self) -> None:
        result = self.install("example-skill")
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertFalse(self.skill.exists())


if __name__ == "__main__":
    unittest.main()
