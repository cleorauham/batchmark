import pytest
from batchmark.annotator import (
    Annotation, AnnotationError,
    save_annotation, load_annotation, list_annotations, delete_annotation,
)


@pytest.fixture
def store(tmp_path):
    return str(tmp_path / "annotations")


def _ann(suite="bench_a", branch="main", note="ok", tags=None):
    return Annotation(suite=suite, branch=branch, note=note, tags=tags or [])


def test_save_creates_file(store):
    a = _ann()
    path = save_annotation(store, a)
    assert path.exists()


def test_save_and_load_roundtrip(store):
    a = _ann(suite="s1", branch="feat/x", note="fast", tags=["perf"])
    save_annotation(store, a)
    loaded = load_annotation(store, "s1", "feat/x")
    assert loaded.note == "fast"
    assert loaded.tags == ["perf"]


def test_load_missing_raises(store):
    with pytest.raises(AnnotationError):
        load_annotation(store, "missing", "main")


def test_list_empty(store):
    assert list_annotations(store) == []


def test_list_returns_all(store):
    save_annotation(store, _ann(suite="a", branch="main"))
    save_annotation(store, _ann(suite="b", branch="dev"))
    result = list_annotations(store)
    assert len(result) == 2


def test_delete_removes_file(store):
    save_annotation(store, _ann())
    removed = delete_annotation(store, "bench_a", "main")
    assert removed is True
    with pytest.raises(AnnotationError):
        load_annotation(store, "bench_a", "main")


def test_delete_missing_returns_false(store):
    assert delete_annotation(store, "nope", "main") is False


def test_save_overwrites_existing(store):
    """Saving an annotation for the same suite/branch should overwrite the previous one."""
    save_annotation(store, _ann(note="original"))
    save_annotation(store, _ann(note="updated"))
    loaded = load_annotation(store, "bench_a", "main")
    assert loaded.note == "updated"
    # Ensure there is still only one entry for this suite/branch
    assert len(list_annotations(store)) == 1
