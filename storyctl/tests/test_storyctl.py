import json
import subprocess
import tempfile
import unittest
from pathlib import Path


CLI = Path(__file__).parents[1] / "storyctl.py"


class StoryCtlTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.cli("init")

    def tearDown(self):
        self.tmp.cleanup()

    def cli(self, *args, ok=True):
        p = subprocess.run(["python3", str(CLI), "--root", str(self.root), *args], text=True, capture_output=True)
        if ok and p.returncode != 0:
            self.fail(p.stderr)
        return p

    def write(self, rel, content):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def commit_pending_wiki(self, chapter_id):
        self.write("wiki/current.md", "# Current\nUpdated\n")
        manifest = self.write("update.json", json.dumps({"updated_files": ["wiki/current.md"]}))
        self.cli("propose-wiki-update", chapter_id, "--patch", str(manifest))
        self.cli("commit-wiki", chapter_id)

    def test_end_to_end_and_gates(self):
        canon = self.write("input/ch1.md", "A fictional opening.")
        self.cli("ingest-canon", str(canon))
        self.assertNotEqual(self.cli("check-ready-to-plan", ok=False).returncode, 0)
        self.commit_pending_wiki("canon:ch1")
        self.cli("propose-plan", "chapter-001", "--level", "chapter", "--option", "A", "--option", "B")
        outline = self.write("outline.md", "# Outline\nA choice is made.\n")
        self.assertNotEqual(self.cli("finalize-plan", "chapter-001", "--outline", str(outline), ok=False).returncode, 0)
        self.cli("record-decision", "chapter-001", "--selected", "B")
        self.cli("finalize-plan", "chapter-001", "--outline", str(outline))
        self.cli("check-ready-to-write", "chapter-001")
        draft = self.write("new-draft.md", "The fictional chapter text.")
        self.cli("register-draft", "chapter-001", "--plan-id", "chapter-001", "--file", str(draft))
        self.assertNotEqual(self.cli("commit-wiki", "chapter-001", ok=False).returncode, 0)
        self.cli("approve-draft", "chapter-001")
        self.assertNotEqual(self.cli("check-ready-to-plan", ok=False).returncode, 0)
        self.commit_pending_wiki("chapter-001")
        self.cli("validate")
        self.assertTrue((self.root / "sources/continuation/chapter-001.md").is_file())
        self.assertTrue((self.root / ".story/receipts/wiki-update-chapter-001.yaml").is_file())

    def test_stale_proposal_is_rejected(self):
        self.cli("propose-plan", "arc-01", "--level", "arc", "--option", "A", "--option", "B")
        state_path = self.root / ".story/state.yaml"
        data = json.loads(state_path.read_text())
        data["wiki_revision"] = 1
        data["story_revision"] = 1
        state_path.write_text(json.dumps(data), encoding="utf-8")
        self.assertNotEqual(self.cli("record-decision", "arc-01", "--selected", "A", ok=False).returncode, 0)

    def test_context_includes_only_approved_style_files(self):
        self.write("style/profile.md", "# Profile\nApproved cinematic rule.\n")
        self.write("style/draft.md", "# Draft\nMust not leak.\n")
        self.write("wiki/characters/hero.md", "# Hero\nCurrent decision model.\n")
        manifest = {
            "schema_version": 1, "revision": 1, "source_scope": [],
            "approved_files": ["profile.md"], "pending_proposals": ["draft.md"],
            "updated_at": None,
        }
        self.write("style/manifest.json", json.dumps(manifest))
        request = self.write("request.json", json.dumps({
            "wiki_files": ["characters/hero.md"],
            "style_files": ["profile.md"],
            "reason": "Plan the hero's next decision",
        }))
        self.cli("build-context", "--for", "chapter", "--target", "chapter-001", "--request", str(request))
        context = (self.root / "context/chapter-001.md").read_text()
        self.assertIn("Approved cinematic rule", context)
        self.assertIn("Current decision model", context)
        self.assertNotIn("Must not leak", context)

        rejected = self.write("request-unapproved.json", json.dumps({"wiki_files": [], "style_files": ["draft.md"]}))
        self.assertNotEqual(self.cli("build-context", "--for", "chapter", "--target", "rejected", "--request", str(rejected), ok=False).returncode, 0)

    def test_context_budget_rejects_oversized_pack(self):
        self.write("wiki/characters/hero.md", "# Hero\n" + ("x" * 500))
        request = self.write("request-large.json", json.dumps({"wiki_files": ["characters/hero.md"], "style_files": []}))
        result = self.cli("build-context", "--for", "chapter", "--target", "large", "--request", str(request), "--max-chars", "100", ok=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("narrow the request", result.stderr)

    def test_style_approval_is_recorded(self):
        self.write("style/profile.md", "# Profile\nCandidate.\n")
        self.write("style/proposals/initial.md", "# Proposal\n")
        manifest = {
            "schema_version": 1, "revision": 0, "source_scope": [],
            "approved_files": [], "pending_proposals": ["proposals/initial.md"],
            "updated_at": None,
        }
        self.write("style/manifest.json", json.dumps(manifest))
        self.cli("approve-style", "--proposal", "proposals/initial.md", "--file", "profile.md")
        updated = json.loads((self.root / "style/manifest.json").read_text())
        self.assertEqual(updated["revision"], 1)
        self.assertEqual(updated["approved_files"], ["profile.md"])
        self.assertTrue((self.root / "decisions/style-revision-1.yaml").is_file())

    def test_managed_chapter_loop_and_hard_gates(self):
        state_path = self.root / ".story/state.yaml"
        data = json.loads(state_path.read_text())
        for plan_id, level, rel in [
            ("arc-01", "arc", "plans/arcs/arc-01.md"),
            ("arc-01-sequence", "sequence", "plans/chapters/arc-01-sequence.md"),
        ]:
            self.write(rel, f"# {plan_id}\n")
            self.write(f"decisions/{plan_id}.yaml", json.dumps({"confirmed_by": "user"}))
            data["plans"][plan_id] = {
                "status": "approved", "level": level, "path": rel,
                "based_on_wiki_revision": 0,
            }
        state_path.write_text(json.dumps(data), encoding="utf-8")
        self.cli(
            "managed-enable", "--arc-id", "arc-01", "--sequence-id", "arc-01-sequence",
            "--chapter", "arc-01-ch01", "--max-chapters", "1", "--delegation-id", "managed-test",
        )
        self.assertEqual(json.loads(self.cli("managed-next").stdout)["action"], "plan-chapter")
        self.cli("propose-plan", "arc-01-ch01", "--level", "chapter", "--option", "A", "--option", "B")
        outline = self.write("outline-managed.md", "# Managed outline\n")
        self.cli("delegated-finalize-plan", "arc-01-ch01", "--delegation", "managed-test", "--selected", "B", "--outline", str(outline))
        decision = json.loads((self.root / "decisions/arc-01-ch01.yaml").read_text())
        self.assertEqual(decision["confirmed_by"], "delegation")
        draft = self.write("managed-draft.md", "Managed chapter prose.\n")
        self.cli("register-draft", "arc-01-ch01", "--plan-id", "arc-01-ch01", "--file", str(draft))
        bad = self.write("quality-bad.json", json.dumps({"continuity": "fail"}))
        self.assertNotEqual(self.cli("delegated-approve-draft", "arc-01-ch01", "--delegation", "managed-test", "--quality-report", str(bad), ok=False).returncode, 0)
        quality = {key: "pass" for key in ["continuity", "character", "information_boundary", "world_rules", "foreshadowing", "outline_coverage", "style"]}
        quality.update({"major_change_detected": False, "revision_count": 1})
        good = self.write("quality-good.json", json.dumps(quality))
        self.cli("delegated-approve-draft", "arc-01-ch01", "--delegation", "managed-test", "--quality-report", str(good))
        self.commit_pending_wiki("arc-01-ch01")
        result = json.loads(self.cli("managed-next").stdout)
        self.assertEqual(result["action"], "pause")
        managed = json.loads(self.cli("managed-status").stdout)
        self.assertEqual(managed["completed_chapters"], ["arc-01-ch01"])
        self.assertEqual(managed["pause_reason"], "batch_limit")

    def test_supporting_character_obligations_are_audited_and_scheduled(self):
        self.write("wiki/characters/support.md", "# Supporting character\nObligations: O-001, O-002\n")
        ledger = {
            "schema_version": 1,
            "obligations": [
                {
                    "id": "O-001", "title": "Hidden allegiance", "type": "subplot", "status": "due",
                    "carrier_pages": ["characters/support.md"], "related_characters": ["hero"],
                    "reader_expectation": "The supporting character has another agenda", "open_questions": ["Who do they serve?"],
                    "last_touched": "ch-01", "next_review": "ch-03", "wake_on": ["leak"],
                    "allowed": ["reinforce"], "forbidden": ["resolve without approval"],
                    "sources": ["canon:ch-01"], "resolution_chapter": None,
                },
                {
                    "id": "O-002", "title": "Old promise", "type": "emotional_debt", "status": "dormant",
                    "carrier_pages": ["characters/support.md"], "related_characters": ["hero"],
                    "reader_expectation": "The promise may return", "open_questions": [],
                    "last_touched": "ch-01", "next_review": "sequence-02", "wake_on": ["homecoming"],
                    "allowed": ["activate"], "forbidden": [], "sources": ["canon:ch-01"],
                    "resolution_chapter": None,
                },
            ],
        }
        self.write("wiki/obligations.json", json.dumps(ledger))
        self.cli("audit-obligations")
        due = json.loads(self.cli("due-obligations", "--chapter-id", "ch-03", "--tag", "homecoming").stdout)
        self.assertEqual(due["must_include"], ["O-001"])
        self.assertEqual(due["consider"], ["O-002"])
        missing = self.write("coverage-missing.json", json.dumps({"coverage": []}))
        self.assertNotEqual(self.cli("check-sequence-coverage", "--coverage", str(missing), ok=False).returncode, 0)
        coverage = self.write("coverage.json", json.dumps({"coverage": [
            {"obligation_id": "O-001", "chapter_id": "ch-03", "action": "reinforce"}
        ]}))
        self.cli("check-sequence-coverage", "--coverage", str(coverage))

        request = self.write("request-obligation.json", json.dumps({"wiki_files": ["obligations.json"], "style_files": []}))
        self.cli("build-context", "--for", "chapter", "--target", "ch-03", "--request", str(request))
        self.assertIn("O-001", (self.root / "context/ch-03.md").read_text())


if __name__ == "__main__":
    unittest.main()
