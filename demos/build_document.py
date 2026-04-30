#!/usr/bin/env python3
"""Demo: Build a Document from scratch and serialize to JSON.

This shows how to use the dataclasses directly without parsing an existing JSON file.
Useful for:
    - Generating input files programmatically
    - Creating documents from databases or APIs
    - Testing the serialization (to_json) functionality
"""

import sys
from pathlib import Path

parent_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(parent_dir))
from inputfile import Document, Part, Chapter, FileRef


def main():
    # ================================================================
    # Build a hierarchical document (with parts)
    # ================================================================

    # Create files for chapters
    files_part1_ch1 = [FileRef(path=Path("origin_story.txt"))]
    files_part1_ch2 = [
        FileRef(path=Path("early_conflicts/ch1.txt")),
        FileRef(path=Path("early_conflicts/ch2.txt")),
    ]

    # Build chapters
    chapter1 = Chapter(number=1, files=files_part1_ch1)
    chapter1.name = "The Beginning"  # set custom name

    chapter2 = Chapter(number=2, files=files_part1_ch2)
    # No custom name — will default to "Chapter 2" on display

    # Build part containing these chapters
    part1 = Part(number=1, chapters=[chapter1, chapter2])
    part1.name = "Genesis"

    # ================================================================
    # Build another part
    # ================================================================

    files_part2_ch1 = [FileRef(path=Path("modern_intro.txt"))]
    files_part2_ch2 = [FileRef(path=Path("cyber_pirates.md"))]

    chapter3 = Chapter(number=1, files=files_part2_ch1)
    chapter3.name = "Digital Horizons"

    chapter4 = Chapter(number=2, files=files_part2_ch2)
    # No custom name — will default to "Chapter 2"

    part2 = Part(number=10, chapters=[chapter3, chapter4])
    part2.name = "Modern Age"

    # ================================================================
    # Build the document
    # ================================================================

    doc = Document(
        title="The Codex of the High Seas",
        root=Path("./manuscripts"),
        chapters=[],  # empty because we're using parts
        parts=[part1, part2],
        author="Captain Syntax",
        default_extension=".txt",
        language="en",
        year=2025,
        metadata={
            "publisher": "GitHub Press",
            "isbn": "123-4567890123",
        },
    )

    # ================================================================
    # Display the document (uses __str__ method)
    # ================================================================

    print("=" * 60)
    print("DOCUMENT BUILT PROGRAMMATICALLY")
    print("=" * 60)
    print(doc)

    # ================================================================
    # Serialize to JSON
    # ================================================================

    output_path = Path("generated_document.json")
    doc.to_json(output_path)
    print(f"\n💾 Serialized document to: {output_path}")

    # ================================================================
    # Verify by parsing it back
    # ================================================================

    print("\n" + "=" * 60)
    print("VERIFYING: Parsing the generated JSON file")
    print("=" * 60)

    doc_reloaded = Document.from_json(output_path)
    print(doc_reloaded)

    # ================================================================
    # Demonstrate flat document (no parts)
    # ================================================================

    print("\n" + "=" * 60)
    print("FLAT DOCUMENT EXAMPLE (chapters only)")
    print("=" * 60)

    flat_chapters = [
        Chapter(number=1, files=[FileRef(path=Path("intro.txt"))]),
        Chapter(number=2, files=[FileRef(path=Path("chapter2.txt"))]),
    ]
    flat_chapters[0].name = "Prologue"
    # Chapter 2 gets default name "Chapter 2"

    flat_doc = Document(
        title="A Pirate's Log",
        root=Path("./logs"),
        chapters=flat_chapters,
        parts=[],
        author="First Mate Jenkins",
        year=1720,
        default_extension=".log",
    )

    print(flat_doc)

    flat_output = Path("flat_document.json")
    flat_doc.to_json(flat_output)
    print(f"\n💾 Serialized flat document to: {flat_output}")


if __name__ == "__main__":
    main()
