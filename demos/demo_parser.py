#!/usr/bin/env python3
"""Demo script for inputfile.py parser.

Usage:
    python demo_parser.py examples/example_flat.json
    python demo_parser.py examples/example_hierarchical.json
"""

import sys
from pathlib import Path

parent_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(parent_dir))
from inputfile import Document


def main():
    if len(sys.argv) != 2:
        print("Usage: python demo_parser.py <inputfile.json>")
        sys.exit(1)

    input_path = Path(sys.argv[1])

    if not input_path.exists():
        print(f"Error: File not found: {input_path}")
        sys.exit(1)

    try:
        doc = Document.from_json(input_path)
        print(doc)

        # Optional: serialize back to JSON
        output_path = input_path.with_suffix(".output.json")
        doc.to_json(output_path)
        print(f"\n💾 Serialized to: {output_path}")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
