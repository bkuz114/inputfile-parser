# inputfile-parser

A lightweight, typed JSON parser for hierarchical document definitions. Built with Python dataclasses and zero external dependencies.

## Features

- Parse JSON into typed `Document`, `Part`, `Chapter`, `FileRef` objects
- Support for flat (chapters only) or hierarchical (parts with chapters) structures
- Auto-numbering of missing `number` fields
- Default names (`Chapter X`, `Part X`) when names are omitted
- Optional per-file display names
- Extensible metadata for custom key-value pairs
- Serialize back to JSON with `to_json()`

## Installation

```bash
git clone https://github.com/bkuz114/inputfile-parser
cd inputfile-parser
```

Then copy `inputfile.py` into your project, or use as a submodule.

**Requirements:** Python 3.9+

## Quick Start

```python
from inputfile import Document

# Parse a JSON input file
doc = Document.from_json("path/to/input.json")

# Access data
print(doc.title)
for chapter in doc.chapters:
    print(f"Chapter {chapter.number}: {chapter.name}")
    for file_ref in chapter.files:
        print(f"  {doc.root / file_ref.path}")
```

## JSON Schema

A document must have **either** `chapters` (flat) **or** `parts` (hierarchical), never both.

### Flat structure (chapters only)

```json
{
  "title": "My Book",
  "root": "./documents",
  "chapters": [
    {
      "number": 1,
      "name": "Introduction",
      "files": ["intro.txt"]
    },
    {
      "files": ["chapter2.txt"]
    }
  ]
}
```

### Hierarchical structure (parts with chapters)

```json
{
  "title": "My Book",
  "root": "./documents",
  "parts": [
    {
      "name": "Genesis",
      "chapters": [
        {"number": 1, "files": ["genesis1.txt"]},
        {"files": ["genesis2.txt"]}
      ]
    }
  ]
}
```

### Field reference

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `title` | string | No | `"Untitled"` | Document title |
| `root` | string | No | `None` | Base directory for relative paths. If omitted, file paths are used as-is (absolute recommended). |
| `default_extension` | string | No | `None` | Appended to files with no extension |
| `author` | string | No | `None` | Optional author name |
| `year` | integer | No | `None` | Optional publication year |
| `language` | string | No | `None` | Optional language code |
| `chapters` | array | See note | `[]` | List of chapters (flat mode) |
| `parts` | array | See note | `[]` | List of parts (hierarchical mode) |

> **Note:** Exactly one of `chapters` or `parts` must be non-empty.

### Chapter fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `number` | integer | No | Auto-numbered | Chapter number |
| `name` | string | No | `"Chapter X"` | Chapter display name |
| `files` | array of strings or objects | Yes | — | File paths (see below) |

### File specification

Files can be specified as:

```json
"files": ["simple_path.txt"]
```

Or with a custom display name:

```json
"files": [
    "simple_path.txt",
    {"path": "custom.pdf", "name": "Custom Display Name"}
]
```

### Part fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `number` | integer | No | Auto-numbered | Part number |
| `name` | string | No | `"Part X"` | Part display name |
| `chapters` | array | Yes | — | List of chapters |

## API Reference

### `Document.from_json(filepath: Path) -> Document`

Parse a JSON file into a `Document` instance.

```python
doc = Document.from_json(Path("input.json"))
```

### `Document.to_json(filepath: Path) -> None`

Serialize a `Document` instance to a JSON file.

```python
doc.to_json(Path("output.json"))
```

### Dataclasses

| Class | Properties | Description |
|-------|------------|-------------|
| `Document` | `title`, `root`, `chapters`, `parts`, `default_extension`, `author`, `year`, `language`, `metadata` | Root container |
| `Part` | `number`, `name`, `chapters` | Top-level division |
| `Chapter` | `number`, `name`, `files` | Contains one or more files |
| `FileRef` | `path`, `name` | Reference to a file |

All dataclasses have `__str__` methods for pretty printing.

## Building Documents Programmatically

```python
from pathlib import Path
from inputfile import Document, Part, Chapter, FileRef

# Build a chapter
chapter = Chapter(number=1, files=[FileRef(path=Path("intro.txt"))])
chapter.name = "The Beginning"

# Build a part containing the chapter
part = Part(number=1, chapters=[chapter])
part.name = "Genesis"

# Build the document
doc = Document(
    title="My Book",
    root=Path("./documents"),
    chapters=[],      # empty because using parts
    parts=[part],
    author="Jane Austen",
    metadata={"publisher": "GitHub Press"}
)

# Serialize to JSON
doc.to_json(Path("output.json"))
```

## Examples

Sample input files are in [`examples/`](examples/).  
Demo scripts are in [`demos/`](demos/).

Run a demo:

```bash
python demos/basic_usage.py examples/flat.json
```

## Troubleshooting

### "Document cannot have both 'chapters' and 'parts'"

Your JSON contains both fields. Remove one.

### "Document must have either 'chapters' or 'parts'"

Your JSON contains neither. Add one.

### "Chapter X must have at least one file"

Every chapter must have a non-empty `files` array.

### `default_extension` not working as expected

The extension is only added when the file path has **no extension**. `file.txt` stays `file.txt`. `file` becomes `file.txt`.

## Versioning

This project follows [Semantic Versioning](https://semver.org/).

## License

MIT

## Contributing

Issues and pull requests are welcome. Please ensure tests pass and update documentation as needed.
