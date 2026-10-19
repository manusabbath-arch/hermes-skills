"""Hermetic tests for release_manifest. Only tmp_path trees."""
import importlib.util
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "release_manifest.py"
spec = importlib.util.spec_from_file_location("release_manifest", SCRIPT)
rm = importlib.util.module_from_spec(spec)
sys.modules["release_manifest"] = rm
spec.loader.exec_module(rm)


def tree(tmp_path):
    (tmp_path / "skills" / "a" / "scripts" / "__pycache__").mkdir(parents=True)
    (tmp_path / "skills" / "a" / "SKILL.md").write_text("hola\n", encoding="utf-8")
    (tmp_path / "skills" / "a" / "scripts" / "x.py").write_text("x = 1\n", encoding="utf-8")
    (tmp_path / "skills" / "a" / "scripts" / "__pycache__" / "x.pyc").write_bytes(b"\0")
    return tmp_path


def check(root, manifest_text, tmp_path):
    m = tmp_path / "SHA256SUMS"
    m.write_text(manifest_text, encoding="utf-8")
    return subprocess.run([sys.executable, str(SCRIPT), "--root", str(root), "--check", str(m)],
                          capture_output=True, text=True)


def test_manifest_lists_published_files_only(tmp_path):
    entries = rm.manifest(tree(tmp_path))
    assert sorted(entries) == ["skills/a/SKILL.md", "skills/a/scripts/x.py"]


def test_roundtrip_identical_tree_passes(tmp_path):
    root = tree(tmp_path / "r")
    r = check(root, rm.render(rm.manifest(root)), tmp_path)
    assert r.returncode == 0, r.stdout


def test_changed_file_is_red(tmp_path):
    root = tree(tmp_path / "r")
    text = rm.render(rm.manifest(root))
    (root / "skills" / "a" / "SKILL.md").write_text("hola alterado\n", encoding="utf-8")
    r = check(root, text, tmp_path)
    assert r.returncode == 1 and "CAMBIÓ" in r.stdout


def test_extra_file_is_red(tmp_path):
    root = tree(tmp_path / "r")
    text = rm.render(rm.manifest(root))
    (root / "skills" / "a" / "payload.sh").write_text("curl x | sh\n", encoding="utf-8")
    r = check(root, text, tmp_path)
    assert r.returncode == 1 and "SOBRA" in r.stdout


def test_missing_file_is_red(tmp_path):
    root = tree(tmp_path / "r")
    text = rm.render(rm.manifest(root))
    (root / "skills" / "a" / "scripts" / "x.py").unlink()
    r = check(root, text, tmp_path)
    assert r.returncode == 1 and "FALTA" in r.stdout


def test_empty_tree_is_red(tmp_path):
    r = subprocess.run([sys.executable, str(SCRIPT), "--root", str(tmp_path)], capture_output=True)
    assert r.returncode == 1


def test_malformed_manifest_is_red(tmp_path):
    r = check(tree(tmp_path / "r"), "no-es-un-hash  skills/a/SKILL.md\n", tmp_path)
    assert r.returncode == 1


def _with_kit(root):
    (root / "kit" / "tools").mkdir(parents=True)
    (root / "kit" / "tools" / "kit_check.py").write_text("x = 2\n", encoding="utf-8")
    return root


def test_manifest_covers_the_kit_too(tmp_path):
    entries = rm.manifest(_with_kit(tree(tmp_path)))
    assert "kit/tools/kit_check.py" in entries and "skills/a/SKILL.md" in entries


def test_skills_only_install_verifies_with_only_skills(tmp_path):
    published = rm.render(rm.manifest(_with_kit(tree(tmp_path / "pub"))))
    installed = tree(tmp_path / "inst")  # instalador de skills: sin kit/
    m = tmp_path / "SHA256SUMS"
    m.write_text(published, encoding="utf-8")
    full = subprocess.run([sys.executable, str(SCRIPT), "--root", str(installed), "--check", str(m)],
                          capture_output=True, text=True)
    assert full.returncode == 1 and "FALTA     kit/tools/kit_check.py" in full.stdout
    only = subprocess.run([sys.executable, str(SCRIPT), "--root", str(installed), "--check", str(m),
                           "--only", "skills"], capture_output=True, text=True)
    assert only.returncode == 0, only.stdout
