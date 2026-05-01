#!/usr/bin/env python3
"""
Bespoke-to-JSON converter.

Converts legacy .txt inputfiles used by various projects (book-builder,
word-count-reporter) with [keys], [book] directives to the modern
JSON format utilized by inputfile.py (this repo's main parser)

Handles both flat (chapters only) and hierarchical (parts with chapters)
structures.

Usage:

python converter.py INPUT_FILE [-h] [--output OUTPUT] [--encoding ENCODING]
                    [--indent INDENT] [--quiet] [--verbose] [--condense]
                    [--FORCE]

Or import and use convert_bespoke_to_json().

Examples:
    # convert legacy inputfile.txt, save to output.json
    python converter.py inputfile.txt --output output.json

    # condense output json to be more readable
    python converter.py inputfile.txt --output output.json --condense
"""

import re
import json
import sys
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class InlinePrimitiveListsEncoder(json.JSONEncoder):
    """
    JSON encoder that keeps primitive-only lists (strings, ints, floats, bools, null)
    on a single line. Lists containing dicts or other lists use pretty printing.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.indent_level = 0

    def _is_primitive(self, obj):
        """Return True for JSON primitive types, False for containers."""
        return isinstance(obj, (str, int, float, bool)) or obj is None

    def _is_primitive_list(self, lst):
        """Return True if list contains only primitive values (no nesting)."""
        return all(self._is_primitive(item) for item in lst)

    def encode(self, obj):
        return self._encode(obj)

    def _encode(self, obj):
        if isinstance(obj, list):
            return self._encode_list(obj)
        elif isinstance(obj, dict):
            return self._encode_dict(obj)
        else:
            return json.dumps(obj)

    def _encode_list(self, lst):
        # Inline if this is a leaf list of primitives
        if self._is_primitive_list(lst):
            items = ", ".join(json.dumps(item) for item in lst)
            return f"[{items}]"

        # Otherwise pretty-print (contains nested structures)
        indent = " " * (self.indent_level * self.indent)
        next_indent = " " * ((self.indent_level + 1) * self.indent)

        self.indent_level += 1
        items = [f"{next_indent}{self._encode(item)}" for item in lst]
        self.indent_level -= 1

        return "[\n" + ",\n".join(items) + f"\n{indent}]"

    def _encode_dict(self, dct):
        indent = " " * (self.indent_level * self.indent)
        next_indent = " " * ((self.indent_level + 1) * self.indent)

        self.indent_level += 1
        items = []
        for k, v in dct.items():
            items.append(f"{next_indent}{json.dumps(k)}: {self._encode(v)}")
        self.indent_level -= 1

        return "{\n" + ",\n".join(items) + f"\n{indent}}}"


def try_int(value: str) -> Union[int, str]:
    """Convert value to int if possible, otherwise return original string."""
    try:
        return int(value)
    except ValueError:
        return value


def parse_keys_section(lines: List[str]) -> Dict[str, Any]:
    """
    Parse [keys] section lines into a dictionary.

    Format: key: value (whitespace around colon allowed).
    Returns all key-value pairs as top-level metadata.
    """
    keys = {}
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if ':' not in line:
            logger.warning(f"Skipping invalid keys line (no colon): {line}")
            continue
        # Split on first colon only
        key, value = line.split(':', 1)
        key = key.strip()
        value = value.strip()
        keys[key] = value
    return keys


def parse_chapter_line(line: str) -> Dict[str, Any]:
    """
    Parse a chapter line: [NUM]:[NAME]:FILEPATH

    Returns a chapter dict with optional 'number', 'name', and required 'files'.
    """
    parts = line.split(':', 2)  # Split into at most 3 parts
    if len(parts) < 3:
        raise ValueError(f"Invalid chapter line (expected at least 3 colon-separated fields): {line}")

    num_str, name_str, filepath = parts
    num_str = num_str.strip()
    name_str = name_str.strip()
    filepath = filepath.strip()

    if not filepath:
        raise ValueError(f"Chapter line missing filepath: {line}")

    chapter: Dict[str, Any] = {"files": [filepath]}

    if num_str:
        chapter["number"] = try_int(num_str)
    if name_str:
        chapter["name"] = name_str

    return chapter


def parse_part_line(line: str) -> Dict[str, Any]:
    """
    Parse a part line: [NUM]~[NAME]

    Returns a part dict with optional 'number' and 'name'.
    """
    if '~' not in line:
        raise ValueError(f"Invalid part line (missing ~ separator): {line}")

    num_str, name_str = line.split('~', 1)
    num_str = num_str.strip()
    name_str = name_str.strip()

    part: Dict[str, Any] = {}

    if num_str:
        part["number"] = num_str  # Keep as string (may be Roman numerals)
    if name_str:
        part["name"] = name_str

    return part


def parse_book_section(lines: List[str]) -> Dict[str, Any]:
    """
    Parse [book] section lines into either flat or hierarchical structure.

    Returns a dict with either a 'chapters' key (flat) or 'parts' key (hierarchical).
    """
    # Filter out blank lines and comments, but keep structural lines
    meaningful_lines = []
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue
        meaningful_lines.append(line.rstrip('\n'))  # Keep original for processing

    # Detect if hierarchical (any line containing '~')
    is_hierarchical = any('~' in line for line in meaningful_lines)

    if not is_hierarchical:
        # Flat structure: all lines are chapter lines
        chapters = []
        for line in meaningful_lines:
            try:
                chapters.append(parse_chapter_line(line))
            except ValueError as e:
                logger.error(str(e))
                raise
        return {"chapters": chapters}

    # Hierarchical structure: parts accumulate chapters
    parts = []
    current_part: Optional[Dict[str, Any]] = None

    for line in meaningful_lines:
        if '~' in line:
            # Part line
            try:
                current_part = parse_part_line(line)
                # Ensure 'chapters' key exists
                current_part["chapters"] = []
                parts.append(current_part)
            except ValueError as e:
                logger.error(str(e))
                raise
        else:
            # Chapter line
            if not current_part:
                raise ValueError("Chapter line found before any part line in hierarchical mode")
            try:
                chapter = parse_chapter_line(line)
                current_part["chapters"].append(chapter)
            except ValueError as e:
                logger.error(str(e))
                raise

    return {"parts": parts}


def convert_bespoke_to_json(bespoke_text: str) -> Dict[str, Any]:
    """
    Convert entire bespoke format text to a JSON-serializable dictionary.

    Args:
        bespoke_text: The entire contents of the .txt file.

    Returns:
        Dictionary ready for json.dump().

    Raises:
        ValueError: If required sections or fields are missing.
    """
    lines = bespoke_text.splitlines()

    # Find section boundaries
    in_keys = False
    in_book = False
    keys_lines = []
    book_lines = []

    for line in lines:
        stripped = line.strip()

        if stripped == '[keys]':
            in_keys = True
            in_book = False
            continue
        elif stripped == '[book]':
            in_keys = False
            in_book = True
            continue
        elif stripped.startswith('[') and stripped.endswith(']'):
            # Unknown section - reset both flags
            in_keys = False
            in_book = False
            continue

        if in_keys:
            keys_lines.append(line)
        elif in_book:
            book_lines.append(line)

    if not keys_lines:
        raise ValueError("Missing [keys] section or section is empty")
    if not book_lines:
        raise ValueError("Missing [book] section or section is empty")

    # Parse keys
    metadata = parse_keys_section(keys_lines)

    # Validate required 'title' key
    if 'title' not in metadata:
        raise ValueError("Missing required 'title' key in [keys] section")

    # Parse book section
    book_data = parse_book_section(book_lines)

    # Merge metadata with book data
    result = {**metadata, **book_data}

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Convert bespoke book format (.txt) to JSON."
    )
    parser.add_argument("input", metavar="INPUTFILE", type=Path, help="Path to input .txt file")
    parser.add_argument("--output", type=Path, required=False, help="Path to output .json file")
    parser.add_argument("--encoding", default="utf-8", help="Input file encoding (default: utf-8)")
    parser.add_argument("--indent", type=int, default=2, help="JSON indentation (default: 2)")
    parser.add_argument("--quiet", action="store_true", help="Suppress info logging")
    parser.add_argument("--verbose", action="store_true", help="Enable debug-level logging (overrides --quiet)")
    parser.add_argument("--condense", action="store_true", help="Output lists (arrays) on a single line for readability")
    parser.add_argument("--FORCE", action="store_true", help="Overwrite existing JSON files without prompting")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    elif args.quiet:
        logging.getLogger().setLevel(logging.WARNING)
    else:
        logging.getLogger().setLevel(logging.INFO)

    input_path = args.input.resolve()  # resolve cwd
    if not input_path.exists():
        logger.error(f"Input file not found: {input_path}")
        sys.exit(1)

    # output: replace extension with JSON, unless user specifies output
    output = input_path.with_suffix('.json')
    if args.output:
        if args.output.suffix != ".json":
            logger.error(f"Output file not a .json file: {args.output}")
        output = args.output.resolve()

    # read bespoke input file
    try:
        with open(input_path, 'r', encoding=args.encoding) as f:
            bespoke_text = f.read()
    except Exception as e:
        logger.error(f"Failed to read input file: {e}")
        sys.exit(1)

    # convert bespoke to JSON
    try:
        result = convert_bespoke_to_json(bespoke_text)
    except ValueError as e:
        logger.error(f"Conversion failed: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

    # output converted JSON file
    try:
        if args.condense:
            json_str = json.dumps(result, cls=InlinePrimitiveListsEncoder, 
                                  indent=args.indent, ensure_ascii=False)
        else:
            json_str = json.dumps(result, indent=args.indent, ensure_ascii=False)

        if output.exists() and not args.FORCE:
            raise FileExistsError(f"{output} already exists. Use --FORCE to overwrite.")
        with open(output, 'w', encoding='utf-8') as f:
            f.write(json_str)

        logger.info(f"Successfully wrote JSON to {output}")
    except Exception as e:
        logger.error(f"Failed to write output file: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
