#!/usr/bin/env python3
"""Test suite for Document and Part root path resolution in inputfile.py.

This module tests the precedence rules for resolving relative file paths in
Document and Part structures. All tests use real directories (via tmp_path)
to ensure cross-platform compatibility.

Usage:
    pytest test_path_resolution.py -v
"""

import sys
import json
import pytest
from pathlib import Path

parent_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(parent_dir))
from inputfile import Document, Part, Chapter, FileRef


# ============================================================================
# Helper: Create a minimal JSON file with configurable root values
# ============================================================================

def create_test_json(
    tmp_path: Path,
    doc_root: str | None = None,
    part_root: str | None = None,
    file_path_in_json: str = "test.txt"
) -> Path:
    """Create a temporary JSON file for testing.

    Args:
        tmp_path: pytest's temporary directory fixture.
        doc_root: Value for Document.root (None means omit from JSON).
        part_root: Value for Part.root (None means omit from JSON).
        file_path_in_json: The file path string inside the chapter's files list.

    Returns:
        Path to the created JSON file.
    """
    json_content = {
        "title": "Test Document",
        "parts": [
            {
                "number": 1,
                "chapters": [
                    {
                        "number": 1,
                        "files": [file_path_in_json]
                    }
                ]
            }
        ]
    }

    if doc_root is not None:
        json_content["root"] = doc_root

    if part_root is not None:
        json_content["parts"][0]["root"] = part_root

    json_path = tmp_path / "test.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_content, f)

    return json_path


# ============================================================================
# Test cases
# ============================================================================

class TestPathResolution:
    """Test Document and Part root resolution precedence."""

    # ------------------------------------------------------------------------
    # Case 1: No roots provided
    # ------------------------------------------------------------------------
    def test_no_roots(self, tmp_path):
        """Document.root=None, Part.root=None
        Expected: File paths resolve relative to JSON file directory.
        """
        json_path = create_test_json(tmp_path, doc_root=None, part_root=None)
        doc = Document.from_json(json_path)

        expected = tmp_path / "test.txt"
        actual = doc.parts[0].chapters[0].files[0].path

        assert actual == expected

    # ------------------------------------------------------------------------
    # Case 2: Document.root missing, Part.root relative
    # ------------------------------------------------------------------------
    def test_doc_root_missing_part_root_relative(self, tmp_path):
        """Document.root=None, Part.root='subdir'
        Expected: Part.root resolves relative to JSON directory.
        """
        json_path = create_test_json(
            tmp_path,
            doc_root=None,
            part_root="subdir",
            file_path_in_json="file.txt"
        )
        doc = Document.from_json(json_path)

        expected = tmp_path / "subdir" / "file.txt"
        actual = doc.parts[0].chapters[0].files[0].path

        assert actual == expected

    # ------------------------------------------------------------------------
    # Case 3: Document.root missing, Part.root absolute (real path)
    # ------------------------------------------------------------------------
    def test_doc_root_missing_part_root_absolute(self, tmp_path):
        """Document.root=None, Part.root absolute (real directory)
        Expected: Part.root used directly as absolute path.
        """
        abs_part_root = tmp_path / "absolute" / "path"
        abs_part_root.mkdir(parents=True)

        json_path = create_test_json(
            tmp_path,
            doc_root=None,
            part_root=str(abs_part_root),
            file_path_in_json="data.txt"
        )
        doc = Document.from_json(json_path)

        expected = abs_part_root / "data.txt"
        actual = doc.parts[0].chapters[0].files[0].path

        assert actual == expected

    # ------------------------------------------------------------------------
    # Case 4: Document.root absolute, Part.root missing
    # ------------------------------------------------------------------------
    def test_doc_root_absolute_part_root_missing(self, tmp_path):
        """Document.root absolute, Part.root=None
        Expected: Document.root used as base.
        """
        abs_doc_root = tmp_path / "doc" / "root"
        abs_doc_root.mkdir(parents=True)

        json_path = create_test_json(
            tmp_path,
            doc_root=str(abs_doc_root),
            part_root=None,
            file_path_in_json="chapter.txt"
        )
        doc = Document.from_json(json_path)

        expected = abs_doc_root / "chapter.txt"
        actual = doc.parts[0].chapters[0].files[0].path

        assert actual == expected

    # ------------------------------------------------------------------------
    # Case 5: Document.root absolute, Part.root relative
    # ------------------------------------------------------------------------
    def test_doc_root_absolute_part_root_relative(self, tmp_path):
        """Document.root absolute, Part.root='sub'
        Expected: Document.root / Part.root.
        """
        abs_doc_root = tmp_path / "doc" / "root"
        abs_doc_root.mkdir(parents=True)

        json_path = create_test_json(
            tmp_path,
            doc_root=str(abs_doc_root),
            part_root="sub",
            file_path_in_json="notes.md"
        )
        doc = Document.from_json(json_path)

        expected = abs_doc_root / "sub" / "notes.md"
        actual = doc.parts[0].chapters[0].files[0].path

        assert actual == expected

    # ------------------------------------------------------------------------
    # Case 6: Document.root absolute, Part.root absolute
    # ------------------------------------------------------------------------
    def test_both_roots_absolute(self, tmp_path):
        """Document.root absolute, Part.root absolute
        Expected: Part.root takes precedence.
        """
        abs_doc_root = tmp_path / "doc" / "root"
        abs_doc_root.mkdir(parents=True)
        abs_part_root = tmp_path / "part" / "root"
        abs_part_root.mkdir(parents=True)

        json_path = create_test_json(
            tmp_path,
            doc_root=str(abs_doc_root),
            part_root=str(abs_part_root),
            file_path_in_json="content.txt"
        )
        doc = Document.from_json(json_path)

        expected = abs_part_root / "content.txt"
        actual = doc.parts[0].chapters[0].files[0].path

        assert actual == expected

    # ------------------------------------------------------------------------
    # Case 7: Document.root relative, Part.root missing
    # ------------------------------------------------------------------------
    def test_doc_root_relative_part_root_missing(self, tmp_path):
        """Document.root='rel/doc', Part.root=None
        Expected: Document.root resolved relative to JSON dir, then file appended.
        """
        rel_doc_root = "rel/doc"
        # Create the directory structure so resolution works
        (tmp_path / rel_doc_root).mkdir(parents=True)

        json_path = create_test_json(
            tmp_path,
            doc_root=rel_doc_root,
            part_root=None,
            file_path_in_json="paper.pdf"
        )
        doc = Document.from_json(json_path)

        expected = (tmp_path / rel_doc_root).resolve() / "paper.pdf"
        actual = doc.parts[0].chapters[0].files[0].path

        assert actual == expected

    # ------------------------------------------------------------------------
    # Case 8: Document.root relative, Part.root relative
    # ------------------------------------------------------------------------
    def test_both_roots_relative(self, tmp_path):
        """Document.root='rel/doc', Part.root='subpart'
        Expected: (JSON_dir / Document.root).resolve() / Part.root / file.
        """
        rel_doc_root = "rel/doc"
        rel_part_root = "subpart"
        # Create the directory structure
        (tmp_path / rel_doc_root / rel_part_root).mkdir(parents=True)

        json_path = create_test_json(
            tmp_path,
            doc_root=rel_doc_root,
            part_root=rel_part_root,
            file_path_in_json="data.bin"
        )
        doc = Document.from_json(json_path)

        expected = ((tmp_path / rel_doc_root).resolve() / rel_part_root) / "data.bin"
        actual = doc.parts[0].chapters[0].files[0].path

        assert actual == expected

    # ------------------------------------------------------------------------
    # Edge: Part.root with no trailing slash (should still work)
    # ------------------------------------------------------------------------
    def test_part_root_no_trailing_slash(self, tmp_path):
        """Edge: Part.root='subdir' (no slash) works identically."""
        json_path = create_test_json(
            tmp_path,
            doc_root=None,
            part_root="subdir",
            file_path_in_json="file.txt"
        )
        doc = Document.from_json(json_path)

        expected = tmp_path / "subdir" / "file.txt"
        actual = doc.parts[0].chapters[0].files[0].path

        assert actual == expected


# ============================================================================
# Optional: Run with verbose output if executed directly
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
