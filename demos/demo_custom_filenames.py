#!/usr/bin/env python3
"""Demo: Using custom display names for individual files.

Shows two ways to specify files in JSON:
    - Simple string: just the path
    - Object: {"path": "...", "name": "Display Name"}
"""

import sys
from pathlib import Path

parent_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(parent_dir))
from inputfile import Document

# Example JSON with mixed file specifications
json_content = """
{
  "title": "Illustrated Novel",
  "root": "./assets",
  "chapters": [
    {
      "number": 1,
      "name": "The Visual Journey",
      "files": [
        "chapter1_text.txt",
        {"path": "chapter1_map.pdf", "name": "Map of the Realm"},
        {"path": "chapter1_sketch.png", "name": "Author Sketch"}
      ]
    },
    {
      "number": 2,
      "name": "Appendices",
      "files": [
        "appendix_a.txt",
        "appendix_b.txt",
        {"path": "colophon.pdf", "name": "Colophon"}
      ]
    }
  ]
}
"""


def main():
    # Write the JSON to a temp file
    temp_json = Path("demo_custom_names.json")
    temp_json.write_text(json_content)

    # Parse it
    doc = Document.from_json(temp_json)

    print("=" * 60)
    print("DEMO: Custom File Display Names")
    print("=" * 60)
    print(doc)  # Uses __str__ method

    print("\n" + "=" * 60)
    print("Detailed file listing:")
    print("=" * 60)

    for chapter in doc.chapters:
        print(f"\n📖 Chapter {chapter.number}: {chapter.name}")
        for file_ref in chapter.files:
            # resolved_path = doc.root / file_ref.path
            # path should already be resolved
            resolved_path = file_ref.path
            if file_ref.name:
                print(f"   📄 Display as: {file_ref.name}")
                print(f"      Actual path: {resolved_path}")
            else:
                print(f"   📄 {resolved_path}")

    # Clean up
    temp_json.unlink()
    print("\n✅ Demo complete. Temp file cleaned up.")


if __name__ == "__main__":
    main()
