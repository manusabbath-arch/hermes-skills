"""Hermetic tests for the installer used by Codex, Cursor and anyone without a plugin system."""
import importlib.util
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))
spec = importlib.util.spec_from_file_location("install_skills", SCRIPTS / "install_skills.py")
inst = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inst)

ALL = sorted(p.parent.name for p in (SCRIPTS.parent / "skills").glob("*/SKILL.md"))


def test_targets_map_to_each_agent_skills_dir(tmp_path):
    assert inst.resolve_dest("agents", home=tmp_path) == tmp_path / ".agents" / "skills"
    assert inst.resolve_dest("cursor", home=tmp_path) == tmp_path / ".cursor" / "skills"
    assert inst.resolve_dest("claude", home=tmp_path) == tmp_path / ".claude" / "skills"
    assert inst.resolve_dest("hermes", home=tmp_path) == tmp_path / ".hermes" / "skills"


def test_installs_every_skill_and_verifies(tmp_path):
    dest = tmp_path / "skills"
    assert inst.main(["--dest", str(dest)]) == 0
    assert sorted(p.parent.name for p in dest.glob("*/SKILL.md")) == ALL
    assert inst.verify(dest, ALL) == []


def test_installs_only_the_requested_skill(tmp_path):
    dest = tmp_path / "skills"
    assert inst.main(["--dest", str(dest), "--skill", "erp-business-analysis"]) == 0
    assert [p.name for p in dest.iterdir()] == ["erp-business-analysis"]


def test_unknown_skill_is_usage_error(tmp_path):
    assert inst.main(["--dest", str(tmp_path / "s"), "--skill", "no-existe"]) == 2
    assert not (tmp_path / "s").exists()


def test_never_overwrites_without_force(tmp_path):
    dest = tmp_path / "skills"
    mine = dest / "delta-lakehouse" / "SKILL.md"
    mine.parent.mkdir(parents=True)
    mine.write_text("mi versión local", encoding="utf-8")
    assert inst.main(["--dest", str(dest), "--skill", "delta-lakehouse"]) == 1
    assert mine.read_text(encoding="utf-8") == "mi versión local"
    assert inst.main(["--dest", str(dest), "--skill", "delta-lakehouse", "--force"]) == 0
    assert inst.verify(dest, ["delta-lakehouse"]) == []


def test_other_skills_in_dest_are_left_alone(tmp_path):
    dest = tmp_path / "skills"
    (dest / "ajena").mkdir(parents=True)
    (dest / "ajena" / "SKILL.md").write_text("x", encoding="utf-8")
    assert inst.main(["--dest", str(dest), "--skill", "delta-lakehouse"]) == 0
    assert (dest / "ajena" / "SKILL.md").read_text(encoding="utf-8") == "x"


def test_verify_catches_a_changed_or_missing_file(tmp_path):
    dest = tmp_path / "skills"
    inst.main(["--dest", str(dest), "--skill", "erp-business-analysis"])
    (dest / "erp-business-analysis" / "SKILL.md").write_text("alterado", encoding="utf-8")
    (dest / "erp-business-analysis" / "templates" / "error-book.md").unlink()
    errs = inst.verify(dest, ["erp-business-analysis"])
    assert len(errs) == 2
