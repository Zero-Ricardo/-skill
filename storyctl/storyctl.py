#!/usr/bin/env python3
"""State-machine CLI for a long-form fiction workspace.

Files use JSON, which is a valid YAML subset, so the tool remains stdlib-only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path


STATE_PATH = Path(".story/state.yaml")
REQUIRED_DIRS = [
    "sources/canon", "sources/continuation", "wiki/characters", "plans/arcs",
    "plans/chapters", "plans/proposals", "drafts", "context", "decisions",
    ".story/receipts", ".story/wiki-updates", "style/observations", "style/proposals",
]
REQUIRED_FILES = [
    "wiki/index.md", "wiki/current.md", "wiki/knowledge.md", "wiki/obligations.json", "wiki/timeline.md", "wiki/world.md",
    "wiki/relationships.md", "wiki/foreshadowing.md", "wiki/questions.md",
    "plans/series.md", "style/manifest.json", "style/profile.md",
    "style/narrative-structure.md", "style/cinematic-scenes.md",
    "style/emotional-rhythm.md", "style/character-voices.md", "style/imagery.md",
    "style/title-system.md", "style/scene-patterns.md", "log.md",
]
CONTEXT_BUDGETS = {"arc": 18000, "sequence": 14000, "chapter": 10000}


class WorkflowError(RuntimeError):
    pass


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def dump(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise WorkflowError(f"missing file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise WorkflowError(f"invalid JSON/YAML-subset file {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise WorkflowError(f"expected object in {path}")
    return value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def state(root: Path) -> dict:
    return load(root / STATE_PATH)


def save_state(root: Path, data: dict) -> None:
    data["updated_at"] = now()
    dump(root / STATE_PATH, data)


def assert_clean_wiki(s: dict) -> None:
    pending = s.get("pending_wiki_update")
    if pending:
        raise WorkflowError(
            f"wiki-update-required: approved chapter {pending['chapter_id']} has not been committed"
        )
    if s.get("story_revision") != s.get("wiki_revision"):
        raise WorkflowError("story and wiki revisions differ; update the wiki first")


def active_delegation(s: dict, delegation_id: str | None = None) -> dict:
    managed = s.get("managed")
    if not managed:
        raise WorkflowError("managed mode is not configured")
    if delegation_id and managed.get("delegation_id") != delegation_id:
        raise WorkflowError("delegation id does not match the active managed run")
    if managed.get("status") != "active":
        raise WorkflowError(f"managed mode is {managed.get('status', 'inactive')}")
    return managed


def plan_hash(root: Path, plan: dict) -> str:
    path = root / plan.get("path", "")
    if not path.is_file():
        raise WorkflowError("approved parent plan file is missing")
    return sha256(path)


def assert_delegation_current(root: Path, s: dict, delegation_id: str, chapter_id: str | None = None) -> dict:
    managed = active_delegation(s, delegation_id)
    if chapter_id and chapter_id not in managed["chapters"]:
        raise WorkflowError(f"chapter {chapter_id} is outside delegated scope")
    arc = s.get("plans", {}).get(managed["arc_id"])
    sequence = s.get("plans", {}).get(managed["sequence_id"])
    if not arc or not sequence or arc.get("status") != "approved" or sequence.get("status") != "approved":
        raise WorkflowError("delegated arc and sequence plans must remain approved")
    if plan_hash(root, arc) != managed["arc_plan_sha256"] or plan_hash(root, sequence) != managed["sequence_plan_sha256"]:
        raise WorkflowError("parent plan changed; managed authorization is stale")
    return managed


def cmd_init(args: argparse.Namespace) -> None:
    root = args.root
    for rel in REQUIRED_DIRS:
        (root / rel).mkdir(parents=True, exist_ok=True)
    for rel in REQUIRED_FILES:
        path = root / rel
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            if rel == "style/manifest.json":
                dump(path, {
                    "schema_version": 1,
                    "revision": 0,
                    "source_scope": [],
                    "approved_files": [],
                    "pending_proposals": [],
                    "updated_at": None,
                })
            elif rel == "wiki/obligations.json":
                dump(path, {"schema_version": 1, "obligations": []})
            else:
                path.write_text(f"# {path.stem.replace('-', ' ').title()}\n", encoding="utf-8")
    if not (root / STATE_PATH).exists():
        dump(root / STATE_PATH, {
            "schema_version": 1,
            "story_revision": 0,
            "wiki_revision": 0,
            "canon_ingests": [],
            "plans": {},
            "drafts": {},
            "pending_wiki_update": None,
            "managed": None,
            "updated_at": now(),
        })
    print(f"initialized story workspace: {root}")


def cmd_status(args: argparse.Namespace) -> None:
    print(json.dumps(state(args.root), ensure_ascii=False, indent=2))


def cmd_ingest_canon(args: argparse.Namespace) -> None:
    s = state(args.root)
    source = args.source.resolve()
    if not source.is_file():
        raise WorkflowError(f"source does not exist: {source}")
    source_hash = sha256(source)
    if any(x["sha256"] == source_hash for x in s["canon_ingests"]):
        raise WorkflowError("this source content has already been ingested")
    dest = args.root / "sources/canon" / source.name
    if dest.exists() and sha256(dest) != source_hash:
        raise WorkflowError(f"destination already exists with different content: {dest}")
    if source != dest.resolve():
        shutil.copy2(source, dest)
    s["canon_ingests"].append({"path": str(dest.relative_to(args.root)), "sha256": source_hash, "at": now()})
    s["story_revision"] += 1
    s["pending_wiki_update"] = {"chapter_id": f"canon:{source.stem}", "source": str(dest.relative_to(args.root)), "sha256": source_hash}
    save_state(args.root, s)
    print("canon source registered; wiki-update-required")


def cmd_check_ready_to_plan(args: argparse.Namespace) -> None:
    s = state(args.root)
    assert_clean_wiki(s)
    print(f"ready-to-plan at wiki revision {s['wiki_revision']}")


def proposal_path(root: Path, plan_id: str) -> Path:
    return root / "plans/proposals" / f"{plan_id}.yaml"


def cmd_propose_plan(args: argparse.Namespace) -> None:
    s = state(args.root)
    assert_clean_wiki(s)
    if len(args.option) < 2 or len(args.option) > 3:
        raise WorkflowError("present exactly 2 or 3 options")
    if len(set(args.option)) != len(args.option):
        raise WorkflowError("option ids must be unique")
    path = proposal_path(args.root, args.plan_id)
    if path.exists():
        raise WorkflowError(f"proposal already exists: {args.plan_id}")
    data = {
        "plan_id": args.plan_id,
        "level": args.level,
        "status": "awaiting_confirmation",
        "based_on_wiki_revision": s["wiki_revision"],
        "options": [{"id": item, "summary": "", "character_impact": "", "foreshadowing_impact": "", "risk": ""} for item in args.option],
        "selected": None,
        "created_at": now(),
    }
    dump(path, data)
    s["plans"][args.plan_id] = {"status": "awaiting_confirmation", "level": args.level, "based_on_wiki_revision": s["wiki_revision"]}
    save_state(args.root, s)
    print(path)


def cmd_record_decision(args: argparse.Namespace) -> None:
    s = state(args.root)
    ppath = proposal_path(args.root, args.plan_id)
    proposal = load(ppath)
    if proposal["based_on_wiki_revision"] != s["wiki_revision"]:
        raise WorkflowError("proposal is stale; regenerate it from the current wiki")
    allowed = {x["id"] for x in proposal["options"]}
    if args.selected not in allowed:
        raise WorkflowError(f"selection must be one of: {', '.join(sorted(allowed))}")
    decision = {
        "decision_id": f"decision-{args.plan_id}",
        "target": args.plan_id,
        "selected": args.selected,
        "confirmed_by": "user",
        "confirmation_mode": "structured-dialogue",
        "based_on_wiki_revision": s["wiki_revision"],
        "confirmed_at": now(),
    }
    dump(args.root / "decisions" / f"{args.plan_id}.yaml", decision)
    proposal["selected"] = args.selected
    proposal["status"] = "confirmed"
    dump(ppath, proposal)
    s["plans"][args.plan_id]["status"] = "confirmed"
    save_state(args.root, s)
    print(f"recorded user selection {args.selected} for {args.plan_id}")


def cmd_finalize_plan(args: argparse.Namespace) -> None:
    s = state(args.root)
    proposal = load(proposal_path(args.root, args.plan_id))
    decision = load(args.root / "decisions" / f"{args.plan_id}.yaml")
    if proposal["status"] != "confirmed" or decision["confirmed_by"] != "user":
        raise WorkflowError("a structured user decision is required")
    if proposal["based_on_wiki_revision"] != s["wiki_revision"]:
        raise WorkflowError("proposal is stale; user must confirm a current proposal")
    if decision["selected"] != proposal["selected"]:
        raise WorkflowError("decision and proposal selections differ")
    dest_dir = "arcs" if proposal["level"] == "arc" else "chapters"
    dest = args.root / "plans" / dest_dir / f"{args.plan_id}.md"
    if not args.outline.is_file():
        raise WorkflowError(f"outline does not exist: {args.outline}")
    header = (
        "---\n"
        f"plan_id: {args.plan_id}\nstatus: approved\nlevel: {proposal['level']}\n"
        f"selected_option: {proposal['selected']}\nbased_on_wiki_revision: {s['wiki_revision']}\n---\n\n"
    )
    dest.write_text(header + args.outline.read_text(encoding="utf-8"), encoding="utf-8")
    s["plans"][args.plan_id].update({"status": "approved", "path": str(dest.relative_to(args.root)), "selected": proposal["selected"]})
    save_state(args.root, s)
    print(dest)


def cmd_check_ready_to_write(args: argparse.Namespace) -> None:
    s = state(args.root)
    assert_clean_wiki(s)
    plan = s["plans"].get(args.plan_id)
    if not plan or plan.get("status") != "approved":
        raise WorkflowError("an approved plan is required")
    if plan["based_on_wiki_revision"] != s["wiki_revision"]:
        raise WorkflowError("approved plan is stale")
    print(f"ready-to-write from {args.plan_id}")


def cmd_register_draft(args: argparse.Namespace) -> None:
    s = state(args.root)
    plan = s["plans"].get(args.plan_id)
    if not plan or plan.get("status") != "approved":
        raise WorkflowError("an approved plan is required")
    assert_clean_wiki(s)
    if not args.file.is_file():
        raise WorkflowError(f"draft does not exist: {args.file}")
    dest = args.root / "drafts" / f"{args.chapter_id}.md"
    if args.file.resolve() != dest.resolve():
        shutil.copy2(args.file, dest)
    s["drafts"][args.chapter_id] = {
        "status": "awaiting_approval", "path": str(dest.relative_to(args.root)),
        "sha256": sha256(dest), "plan_id": args.plan_id,
        "based_on_wiki_revision": s["wiki_revision"],
    }
    save_state(args.root, s)
    print(f"registered draft {args.chapter_id}; awaiting user approval")


def cmd_approve_draft(args: argparse.Namespace) -> None:
    s = state(args.root)
    draft = s["drafts"].get(args.chapter_id)
    if not draft or draft["status"] != "awaiting_approval":
        raise WorkflowError("draft is not awaiting approval")
    if sha256(args.root / draft["path"]) != draft["sha256"]:
        raise WorkflowError("draft changed after registration; register it again")
    draft["status"] = "approved"
    draft["approved_by"] = "user"
    draft["approved_at"] = now()
    s["story_revision"] += 1
    s["pending_wiki_update"] = {"chapter_id": args.chapter_id, "source": draft["path"], "sha256": draft["sha256"]}
    save_state(args.root, s)
    print(f"approved {args.chapter_id}; wiki-update-required")


def cmd_managed_enable(args: argparse.Namespace) -> None:
    s = state(args.root)
    assert_clean_wiki(s)
    if s.get("managed") and s["managed"].get("status") in {"active", "paused"}:
        raise WorkflowError("another managed run is already active or paused")
    if len(set(args.chapter)) != len(args.chapter):
        raise WorkflowError("delegated chapter ids must be unique")
    if args.max_chapters < 1:
        raise WorkflowError("max-chapters must be positive")
    arc = s.get("plans", {}).get(args.arc_id)
    sequence = s.get("plans", {}).get(args.sequence_id)
    if not arc or arc.get("status") != "approved":
        raise WorkflowError("an approved arc plan is required")
    if not sequence or sequence.get("status") != "approved":
        raise WorkflowError("an approved sequence plan is required")
    delegation_id = args.delegation_id or f"managed-{args.arc_id}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
    managed = {
        "delegation_id": delegation_id,
        "mode": "managed",
        "status": "active",
        "arc_id": args.arc_id,
        "sequence_id": args.sequence_id,
        "chapters": args.chapter,
        "completed_chapters": [],
        "max_chapters_per_run": args.max_chapters,
        "completed_this_run": 0,
        "permissions": {
            "chapter_plan": "delegated", "chapter_draft": "delegated",
            "wiki_commit": "automatic", "title_selection": "delegated"
        },
        "hard_stops": [
            "canon_conflict", "arc_deviation", "major_character_death", "betrayal",
            "identity_revelation", "world_rule_change", "central_mystery_resolution",
            "major_foreshadowing_resolution", "relationship_status_change",
            "new_unapproved_power", "low_confidence"
        ],
        "arc_plan_sha256": plan_hash(args.root, arc),
        "sequence_plan_sha256": plan_hash(args.root, sequence),
        "based_on_wiki_revision": s["wiki_revision"],
        "granted_by": "user", "granted_at": now(), "pause_reason": None
    }
    s["managed"] = managed
    dump(args.root / "decisions" / f"{delegation_id}.yaml", {
        "decision_id": delegation_id, "decision_type": "managed-delegation",
        "confirmed_by": "user", "confirmation_mode": "structured-dialogue",
        "scope": managed, "confirmed_at": now()
    })
    save_state(args.root, s)
    print(f"managed mode enabled: {delegation_id}")


def cmd_managed_status(args: argparse.Namespace) -> None:
    print(json.dumps(state(args.root).get("managed"), ensure_ascii=False, indent=2))


def cmd_managed_next(args: argparse.Namespace) -> None:
    s = state(args.root)
    managed = active_delegation(s)
    assert_delegation_current(args.root, s, managed["delegation_id"])
    if s.get("pending_wiki_update"):
        result = {"action": "commit-wiki", "chapter_id": s["pending_wiki_update"]["chapter_id"], "delegation_id": managed["delegation_id"]}
    elif managed["completed_this_run"] >= managed["max_chapters_per_run"]:
        managed["status"] = "paused"
        managed["pause_reason"] = "batch_limit"
        save_state(args.root, s)
        result = {"action": "pause", "reason": "batch_limit", "completed_this_run": managed["completed_this_run"]}
    else:
        remaining = [x for x in managed["chapters"] if x not in managed["completed_chapters"]]
        if not remaining:
            managed["status"] = "complete"
            save_state(args.root, s)
            result = {"action": "complete", "delegation_id": managed["delegation_id"]}
        else:
            chapter_id = remaining[0]
            plan = s.get("plans", {}).get(chapter_id)
            draft = s.get("drafts", {}).get(chapter_id)
            if not plan or plan.get("status") != "approved":
                action = "plan-chapter"
            elif not draft:
                action = "write-chapter"
            elif draft.get("status") == "awaiting_approval":
                action = "quality-check-and-approve"
            elif draft.get("status") == "approved":
                raise WorkflowError("approved draft has no pending wiki update")
            else:
                raise WorkflowError(f"unsupported draft state: {draft.get('status')}")
            result = {"action": action, "chapter_id": chapter_id, "delegation_id": managed["delegation_id"], "arc_id": managed["arc_id"], "sequence_id": managed["sequence_id"]}
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_delegated_finalize_plan(args: argparse.Namespace) -> None:
    s = state(args.root)
    managed = assert_delegation_current(args.root, s, args.delegation, args.plan_id)
    assert_clean_wiki(s)
    proposal = load(proposal_path(args.root, args.plan_id))
    if proposal.get("level") != "chapter" or proposal.get("based_on_wiki_revision") != s["wiki_revision"]:
        raise WorkflowError("delegated chapter proposal is invalid or stale")
    allowed = {x["id"] for x in proposal.get("options", [])}
    if args.selected not in allowed:
        raise WorkflowError("selected option was not presented in the proposal")
    if not args.outline.is_file():
        raise WorkflowError(f"outline does not exist: {args.outline}")
    decision = {
        "decision_id": f"decision-{args.plan_id}", "target": args.plan_id,
        "selected": args.selected, "confirmed_by": "delegation",
        "delegation_id": managed["delegation_id"],
        "based_on_wiki_revision": s["wiki_revision"], "confirmed_at": now()
    }
    dump(args.root / "decisions" / f"{args.plan_id}.yaml", decision)
    proposal["selected"] = args.selected
    proposal["status"] = "confirmed"
    dump(proposal_path(args.root, args.plan_id), proposal)
    dest = args.root / "plans/chapters" / f"{args.plan_id}.md"
    header = (
        "---\n" f"plan_id: {args.plan_id}\nstatus: approved\nlevel: chapter\n"
        f"selected_option: {args.selected}\nbased_on_wiki_revision: {s['wiki_revision']}\n"
        f"approved_by: delegation\ndelegation_id: {managed['delegation_id']}\n---\n\n"
    )
    dest.write_text(header + args.outline.read_text(encoding="utf-8"), encoding="utf-8")
    s["plans"][args.plan_id] = {
        "status": "approved", "level": "chapter", "path": str(dest.relative_to(args.root)),
        "selected": args.selected, "based_on_wiki_revision": s["wiki_revision"],
        "approved_by": "delegation", "delegation_id": managed["delegation_id"]
    }
    save_state(args.root, s)
    print(dest)


def cmd_delegated_approve_draft(args: argparse.Namespace) -> None:
    s = state(args.root)
    managed = assert_delegation_current(args.root, s, args.delegation, args.chapter_id)
    draft = s.get("drafts", {}).get(args.chapter_id)
    if not draft or draft.get("status") != "awaiting_approval":
        raise WorkflowError("draft is not awaiting approval")
    report = load(args.quality_report)
    required = ["continuity", "character", "information_boundary", "world_rules", "foreshadowing", "outline_coverage", "style"]
    failed = [key for key in required if report.get(key) != "pass"]
    if failed:
        raise WorkflowError("quality report failed: " + ", ".join(failed))
    if report.get("major_change_detected") is not False:
        raise WorkflowError("major change requires user confirmation")
    if not isinstance(report.get("revision_count"), int) or report["revision_count"] > 2:
        raise WorkflowError("delegated drafting allows at most two automatic revisions")
    if sha256(args.root / draft["path"]) != draft["sha256"]:
        raise WorkflowError("draft changed after registration; register it again")
    draft.update({
        "status": "approved", "approved_by": "delegation",
        "delegation_id": managed["delegation_id"], "approved_at": now(),
        "quality_report": str(args.quality_report)
    })
    s["story_revision"] += 1
    s["pending_wiki_update"] = {
        "chapter_id": args.chapter_id, "source": draft["path"], "sha256": draft["sha256"],
        "delegation_id": managed["delegation_id"]
    }
    save_state(args.root, s)
    print(f"delegated approval recorded for {args.chapter_id}; wiki-update-required")


def cmd_managed_pause(args: argparse.Namespace) -> None:
    s = state(args.root)
    managed = active_delegation(s)
    managed.update({"status": "paused", "pause_reason": args.reason, "paused_chapter": args.chapter, "paused_at": now()})
    save_state(args.root, s)
    print(f"managed mode paused: {args.reason}")


def cmd_managed_resume(args: argparse.Namespace) -> None:
    s = state(args.root)
    managed = s.get("managed")
    if not managed or managed.get("status") != "paused":
        raise WorkflowError("managed mode is not paused")
    if args.decision and not (args.root / args.decision).is_file():
        raise WorkflowError("resume decision file does not exist")
    managed.update({"status": "active", "pause_reason": None, "completed_this_run": 0, "resumed_at": now(), "resume_decision": args.decision})
    save_state(args.root, s)
    print("managed mode resumed")


def cmd_managed_disable(args: argparse.Namespace) -> None:
    s = state(args.root)
    managed = s.get("managed")
    if not managed:
        raise WorkflowError("managed mode is not configured")
    managed.update({"status": "disabled", "disabled_at": now()})
    save_state(args.root, s)
    print("managed mode disabled")


def cmd_propose_wiki_update(args: argparse.Namespace) -> None:
    s = state(args.root)
    pending = s.get("pending_wiki_update")
    if not pending or pending["chapter_id"] != args.chapter_id:
        raise WorkflowError("chapter is not the pending wiki update")
    if not args.patch.is_file():
        raise WorkflowError(f"wiki update manifest does not exist: {args.patch}")
    manifest = load(args.patch)
    updated = manifest.get("updated_files")
    if not isinstance(updated, list) or not updated:
        raise WorkflowError("wiki update manifest needs a non-empty updated_files list")
    for rel in updated:
        if not str(rel).startswith("wiki/"):
            raise WorkflowError("updated_files may only contain wiki/ paths")
    dest = args.root / ".story/wiki-updates" / f"{args.chapter_id}.yaml"
    dump(dest, manifest)
    print(dest)


def cmd_commit_wiki(args: argparse.Namespace) -> None:
    s = state(args.root)
    pending = s.get("pending_wiki_update")
    if not pending or pending["chapter_id"] != args.chapter_id:
        raise WorkflowError("chapter is not pending wiki update")
    manifest = load(args.root / ".story/wiki-updates" / f"{args.chapter_id}.yaml")
    updated = manifest["updated_files"]
    for rel in updated:
        path = args.root / rel
        if not path.is_file():
            raise WorkflowError(f"declared wiki file is missing: {rel}")
    source = args.root / pending["source"]
    if sha256(source) != pending["sha256"]:
        raise WorkflowError("approved source changed before wiki commit")
    if not pending["chapter_id"].startswith("canon:"):
        dest = args.root / "sources/continuation" / f"{args.chapter_id}.md"
        shutil.copy2(source, dest)
    old = s["wiki_revision"]
    s["wiki_revision"] = s["story_revision"]
    s["pending_wiki_update"] = None
    receipt = {
        "chapter_id": args.chapter_id,
        "source_sha256": pending["sha256"],
        "previous_wiki_revision": old,
        "new_wiki_revision": s["wiki_revision"],
        "updated_files": updated,
        "validated": True,
        "committed_at": now(),
    }
    dump(args.root / ".story/receipts" / f"wiki-update-{args.chapter_id.replace(':', '-')}.yaml", receipt)
    managed = s.get("managed")
    if managed and pending.get("delegation_id") == managed.get("delegation_id") and args.chapter_id in managed.get("chapters", []):
        if args.chapter_id not in managed["completed_chapters"]:
            managed["completed_chapters"].append(args.chapter_id)
            managed["completed_this_run"] += 1
    save_state(args.root, s)
    print(f"wiki committed at revision {s['wiki_revision']}")


def cmd_build_context(args: argparse.Namespace) -> None:
    s = state(args.root)
    assert_clean_wiki(s)
    out = args.root / "context" / f"{args.target}.md"
    request = {"wiki_files": [], "style_files": [], "reason": "baseline context"}
    if args.request:
        request = load(args.request)
    wiki_files = request.get("wiki_files", [])
    style_files = request.get("style_files", [])
    if not isinstance(wiki_files, list) or not isinstance(style_files, list):
        raise WorkflowError("context request wiki_files and style_files must be lists")
    sections = []
    selected = []
    for rel in ["current.md", "index.md", *wiki_files]:
        path = Path(str(rel))
        if path.is_absolute() or ".." in path.parts or path.suffix not in {".md", ".json"}:
            raise WorkflowError(f"invalid wiki context path: {rel}")
        full = args.root / "wiki" / path
        if not full.is_file():
            raise WorkflowError(f"requested wiki file is missing: {rel}")
        label = f"wiki/{path.as_posix()}"
        if label not in selected:
            selected.append(label)
            sections.append(f"\n\n## {label}\n\n" + full.read_text(encoding="utf-8"))
    manifest_path = args.root / "style/manifest.json"
    manifest = load(manifest_path) if manifest_path.is_file() else {"approved_files": []}
    approved_style = set(manifest.get("approved_files", []))
    for rel in style_files:
        path = Path(str(rel))
        if path.is_absolute() or ".." in path.parts or path.suffix != ".md":
            raise WorkflowError(f"invalid style context path: {rel}")
        normalized = path.as_posix()
        if normalized not in approved_style:
            raise WorkflowError(f"style file is not approved: {rel}")
        full = args.root / "style" / path
        if not full.is_file():
            raise WorkflowError(f"requested style file is missing: {rel}")
        label = f"style/{normalized}"
        if label not in selected:
            selected.append(label)
            sections.append(f"\n\n## {label}\n\n" + full.read_text(encoding="utf-8"))
    body = "".join(sections)
    budget = args.max_chars or CONTEXT_BUDGETS[args.mode]
    if budget < 1:
        raise WorkflowError("max-chars must be positive")
    if len(body) > budget:
        raise WorkflowError(f"context pack is {len(body)} characters; narrow the request below the {budget} character budget")
    content = (
        "---\n"
        f"target: {args.target}\nmode: {args.mode}\nwiki_revision: {s['wiki_revision']}\n"
        f"context_budget: {budget}\n"
        "---\n\n# Planning Context\n\n"
        f"Request reason: {request.get('reason', '')}\n\n"
        "Selected files:\n"
        + "".join(f"- {item}\n" for item in selected)
        + "\n\n## Agent checklist\n\n"
        "- Use only relevant character decisions, relationships, knowledge, rules and foreshadowing.\n"
        "- Cite the corresponding Wiki page or source for every hard constraint.\n"
        "- Request a targeted Wiki repair if required character motivation is missing.\n"
        + body
    )
    out.write_text(content, encoding="utf-8")
    print(out)


def cmd_approve_style(args: argparse.Namespace) -> None:
    manifest_path = args.root / "style/manifest.json"
    manifest = load(manifest_path)
    if args.proposal not in manifest.get("pending_proposals", []):
        raise WorkflowError("style proposal is not pending")
    if not args.file:
        raise WorkflowError("approve at least one style file")
    approved = set(manifest.get("approved_files", []))
    for rel in args.file:
        path = Path(rel)
        if path.is_absolute() or ".." in path.parts or path.suffix != ".md":
            raise WorkflowError(f"invalid style file: {rel}")
        if not (args.root / "style" / path).is_file():
            raise WorkflowError(f"style file does not exist: {rel}")
        approved.add(path.as_posix())
    old_revision = int(manifest.get("revision", 0))
    manifest["revision"] = old_revision + 1
    manifest["approved_files"] = sorted(approved)
    manifest["pending_proposals"] = [x for x in manifest.get("pending_proposals", []) if x != args.proposal]
    manifest["updated_at"] = now()
    dump(manifest_path, manifest)
    dump(args.root / "decisions" / f"style-revision-{manifest['revision']}.yaml", {
        "decision_id": f"style-revision-{manifest['revision']}",
        "target": args.proposal,
        "approved_files": args.file,
        "confirmed_by": "user",
        "confirmation_mode": "structured-dialogue",
        "confirmed_at": now(),
    })
    print(f"approved style revision {manifest['revision']}")


def obligation_items(root: Path) -> list[dict]:
    ledger = load(root / "wiki/obligations.json")
    items = ledger.get("obligations")
    if not isinstance(items, list):
        raise WorkflowError("wiki/obligations.json obligations must be a list")
    if not all(isinstance(item, dict) for item in items):
        raise WorkflowError("every story obligation must be an object")
    return items


def obligation_errors(root: Path, items: list[dict]) -> list[str]:
    errors = []
    allowed_status = {"dormant", "active", "due", "resolved", "retired", "blocked"}
    ids = []
    for item in items:
        oid = item.get("id")
        if not isinstance(oid, str) or not oid.startswith("O-"):
            errors.append("every obligation needs an O- prefixed id")
            continue
        ids.append(oid)
        status = item.get("status")
        if status not in allowed_status:
            errors.append(f"{oid}: invalid status {status}")
        carriers = item.get("carrier_pages", [])
        if not isinstance(carriers, list) or not carriers:
            errors.append(f"{oid}: carrier_pages must be a non-empty list")
        else:
            for rel in carriers:
                path = Path(str(rel))
                if path.is_absolute() or ".." in path.parts or not str(rel).startswith("characters/") or not (root / "wiki" / path).is_file():
                    errors.append(f"{oid}: missing or invalid carrier page {rel}")
        if not isinstance(item.get("sources"), list) or not item.get("sources"):
            errors.append(f"{oid}: at least one source is required")
        wake_on = item.get("wake_on", [])
        if not isinstance(wake_on, list):
            errors.append(f"{oid}: wake_on must be a list")
        if status in {"active", "due"} and not item.get("next_review") and not wake_on:
            errors.append(f"{oid}: active/due obligation needs next_review or wake_on")
        if status == "dormant" and (not item.get("next_review") or not wake_on):
            errors.append(f"{oid}: dormant obligation needs both next_review and wake_on")
        if status == "resolved" and not item.get("resolution_chapter"):
            errors.append(f"{oid}: resolved obligation needs resolution_chapter")
        if status == "retired" and not item.get("retired_by"):
            errors.append(f"{oid}: retired obligation needs retired_by decision reference")
    if len(ids) != len(set(ids)):
        errors.append("obligation ids must be unique")
    return errors


def cmd_audit_obligations(args: argparse.Namespace) -> None:
    items = obligation_items(args.root)
    errors = obligation_errors(args.root, items)
    if errors:
        raise WorkflowError("obligation audit failed:\n- " + "\n- ".join(errors))
    counts = {}
    for item in items:
        counts[item["status"]] = counts.get(item["status"], 0) + 1
    print(json.dumps({"valid": True, "count": len(items), "by_status": counts}, ensure_ascii=False, indent=2))


def cmd_due_obligations(args: argparse.Namespace) -> None:
    items = obligation_items(args.root)
    errors = obligation_errors(args.root, items)
    if errors:
        raise WorkflowError("repair the obligation ledger before querying due items")
    tags = set(args.tag or [])
    result = {"must_include": [], "consider": [], "dormant": [], "blocked": []}
    for item in items:
        oid = item["id"]
        status = item["status"]
        wake_match = bool(tags.intersection(item.get("wake_on", [])))
        review_match = item.get("next_review") == args.chapter_id
        if status == "blocked":
            result["blocked"].append(oid)
        elif status == "due" or review_match:
            result["must_include"].append(oid)
        elif status == "active" and wake_match:
            result["consider"].append(oid)
        elif status == "dormant" and wake_match:
            result["consider"].append(oid)
        elif status in {"active", "dormant"}:
            result["dormant"].append(oid)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_check_sequence_coverage(args: argparse.Namespace) -> None:
    items = obligation_items(args.root)
    errors = obligation_errors(args.root, items)
    if errors:
        raise WorkflowError("repair the obligation ledger before checking sequence coverage")
    coverage = load(args.coverage).get("coverage")
    if not isinstance(coverage, list) or not all(isinstance(x, dict) for x in coverage):
        raise WorkflowError("coverage file needs a coverage list")
    by_id = {}
    allowed_actions = {"mention", "reinforce", "activate", "resolve", "retire", "defer"}
    coverage_errors = []
    valid_ids = {item["id"] for item in items}
    for entry in coverage:
        oid = entry.get("obligation_id")
        action = entry.get("action")
        if oid not in valid_ids:
            coverage_errors.append(f"unknown obligation id: {oid}")
            continue
        if action not in allowed_actions:
            coverage_errors.append(f"{oid}: invalid coverage action {action}")
        if not entry.get("chapter_id"):
            coverage_errors.append(f"{oid}: chapter_id is required")
        by_id.setdefault(oid, []).append(entry)
    for item in items:
        oid = item["id"]
        if item["status"] == "due" and oid not in by_id:
            coverage_errors.append(f"{oid}: due obligation is not covered")
        if item["status"] == "active" and oid not in by_id:
            coverage_errors.append(f"{oid}: active obligation needs a touch or explicit defer")
        for entry in by_id.get(oid, []):
            if entry.get("action") in {"resolve", "retire"} and item.get("forbidden") and not entry.get("approval_decision"):
                coverage_errors.append(f"{oid}: {entry['action']} requires approval_decision because handling is restricted")
    if coverage_errors:
        raise WorkflowError("sequence coverage failed:\n- " + "\n- ".join(coverage_errors))
    print(json.dumps({"valid": True, "covered_obligations": sorted(by_id)}, ensure_ascii=False, indent=2))


def cmd_validate(args: argparse.Namespace) -> None:
    s = state(args.root)
    errors = []
    for rel in REQUIRED_DIRS:
        if not (args.root / rel).is_dir(): errors.append(f"missing directory: {rel}")
    for rel in REQUIRED_FILES:
        if not (args.root / rel).is_file(): errors.append(f"missing file: {rel}")
    if s.get("wiki_revision", -1) > s.get("story_revision", -1):
        errors.append("wiki revision cannot exceed story revision")
    pending = s.get("pending_wiki_update")
    if s.get("story_revision") != s.get("wiki_revision") and not pending:
        errors.append("revision mismatch without pending wiki update")
    for plan_id, plan in s.get("plans", {}).items():
        if plan.get("status") == "approved":
            if not (args.root / plan["path"]).is_file(): errors.append(f"approved plan file missing: {plan_id}")
            if not (args.root / "decisions" / f"{plan_id}.yaml").is_file(): errors.append(f"approved plan lacks decision: {plan_id}")
    managed = s.get("managed")
    if managed and managed.get("status") in {"active", "paused"}:
        if not (args.root / "decisions" / f"{managed.get('delegation_id')}.yaml").is_file():
            errors.append("managed delegation lacks a user decision record")
        for key in ("arc_id", "sequence_id", "chapters", "hard_stops", "permissions"):
            if key not in managed: errors.append(f"managed delegation lacks {key}")
    try:
        errors.extend(obligation_errors(args.root, obligation_items(args.root)))
    except WorkflowError as exc:
        errors.append(str(exc))
    if errors:
        raise WorkflowError("validation failed:\n- " + "\n- ".join(errors))
    print("workspace valid")


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="storyctl")
    p.add_argument("--root", type=Path, default=Path.cwd())
    sub = p.add_subparsers(dest="command", required=True)
    def add(name, fn):
        q = sub.add_parser(name); q.set_defaults(fn=fn); return q
    add("init", cmd_init)
    add("status", cmd_status)
    q = add("ingest-canon", cmd_ingest_canon); q.add_argument("source", type=Path)
    add("check-ready-to-plan", cmd_check_ready_to_plan)
    q = add("propose-plan", cmd_propose_plan); q.add_argument("plan_id"); q.add_argument("--level", choices=["arc", "sequence", "chapter"], required=True); q.add_argument("--option", action="append", required=True)
    q = add("record-decision", cmd_record_decision); q.add_argument("plan_id"); q.add_argument("--selected", required=True)
    q = add("finalize-plan", cmd_finalize_plan); q.add_argument("plan_id"); q.add_argument("--outline", type=Path, required=True)
    q = add("check-ready-to-write", cmd_check_ready_to_write); q.add_argument("plan_id")
    q = add("register-draft", cmd_register_draft); q.add_argument("chapter_id"); q.add_argument("--plan-id", required=True); q.add_argument("--file", type=Path, required=True)
    q = add("approve-draft", cmd_approve_draft); q.add_argument("chapter_id")
    q = add("managed-enable", cmd_managed_enable); q.add_argument("--arc-id", required=True); q.add_argument("--sequence-id", required=True); q.add_argument("--chapter", action="append", required=True); q.add_argument("--max-chapters", type=int, default=3); q.add_argument("--delegation-id")
    add("managed-status", cmd_managed_status)
    add("managed-next", cmd_managed_next)
    q = add("delegated-finalize-plan", cmd_delegated_finalize_plan); q.add_argument("plan_id"); q.add_argument("--delegation", required=True); q.add_argument("--selected", required=True); q.add_argument("--outline", type=Path, required=True)
    q = add("delegated-approve-draft", cmd_delegated_approve_draft); q.add_argument("chapter_id"); q.add_argument("--delegation", required=True); q.add_argument("--quality-report", type=Path, required=True)
    q = add("managed-pause", cmd_managed_pause); q.add_argument("--reason", required=True); q.add_argument("--chapter")
    q = add("managed-resume", cmd_managed_resume); q.add_argument("--decision")
    add("managed-disable", cmd_managed_disable)
    q = add("propose-wiki-update", cmd_propose_wiki_update); q.add_argument("chapter_id"); q.add_argument("--patch", type=Path, required=True)
    q = add("commit-wiki", cmd_commit_wiki); q.add_argument("chapter_id")
    q = add("build-context", cmd_build_context); q.add_argument("--for", dest="mode", choices=["arc", "sequence", "chapter"], required=True); q.add_argument("--target", required=True); q.add_argument("--request", type=Path); q.add_argument("--max-chars", type=int)
    q = add("approve-style", cmd_approve_style); q.add_argument("--proposal", required=True); q.add_argument("--file", action="append", required=True)
    add("audit-obligations", cmd_audit_obligations)
    q = add("due-obligations", cmd_due_obligations); q.add_argument("--chapter-id", required=True); q.add_argument("--tag", action="append")
    q = add("check-sequence-coverage", cmd_check_sequence_coverage); q.add_argument("--coverage", type=Path, required=True)
    add("validate", cmd_validate)
    return p


def main() -> int:
    args = parser().parse_args()
    args.root = args.root.resolve()
    try:
        args.fn(args)
    except WorkflowError as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
