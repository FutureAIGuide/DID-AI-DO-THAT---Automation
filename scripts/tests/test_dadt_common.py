import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import dadt_common as dc


def test_is_valid_slug():
    assert dc.is_valid_slug("ai-crime-story")
    assert dc.is_valid_slug("story2")
    assert not dc.is_valid_slug("Story_Bad")
    assert not dc.is_valid_slug("")
    assert not dc.is_valid_slug("-leading-dash")


def test_render_text_string():
    assert dc.render_text("hello") == "hello"


def test_render_text_list_of_dicts():
    content = [{"text": "hello "}, {"text": "world"}]
    assert dc.render_text(content) == "hello world"


def test_split_sections_ok():
    content = "# ALPHA\nbody one\n\n# BETA\nbody two\n"
    sections = dc.split_sections(content, ["ALPHA", "BETA"])
    assert sections["ALPHA"] == "body one"
    assert sections["BETA"] == "body two"


def test_split_sections_missing_raises():
    content = "# ALPHA\nbody one\n"
    try:
        dc.split_sections(content, ["ALPHA", "BETA"])
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "BETA" in str(exc)


def test_parse_decision_final_line():
    report = "Some analysis.\n\nFINAL GRADE: A\nFINAL DECISION: PUBLISH\n"
    assert dc.parse_decision(report) == "PUBLISH"


def test_parse_decision_fallback_last_match():
    report = "We considered HOLD earlier, but ultimately: REJECT"
    assert dc.parse_decision(report) == "REJECT"


def test_parse_decision_none_found():
    try:
        dc.parse_decision("no decision keywords here")
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_next_file_increments(tmp_path):
    rel = "articles/drafts/example.md"
    first = dc.save_file(tmp_path, rel, "v1")
    second_path = dc.next_file(tmp_path, rel)
    assert first.name == "example.md"
    assert second_path.name == "example-02.md"


def test_write_json_roundtrip(tmp_path):
    path = dc.write_json(tmp_path / "status.json", {"a": 1})
    assert path.exists()
    assert '"a": 1' in path.read_text(encoding="utf-8")
