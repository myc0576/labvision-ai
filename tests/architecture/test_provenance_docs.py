from __future__ import annotations

from pathlib import Path


def test_provenance_docs_record_public_core_and_deferred_legacy_scope():
    root = Path(__file__).resolve().parents[2]
    inventory = (root / "docs" / "provenance" / "asset-inventory.md").read_text(encoding="utf-8")
    open_questions = (root / "docs" / "provenance" / "open-questions.md").read_text(encoding="utf-8")
    for field in ["Source path", "Asset type", "Transformation performed", "Distribution status", "Review owner/date"]:
        assert field in inventory
    assert "public GitHub core package" in inventory
    assert "legacy-dependent features deferred" in inventory
    assert "does not include the legacy-dependent modules" in open_questions
    assert "Allowed now: public GitHub browsing" in open_questions
