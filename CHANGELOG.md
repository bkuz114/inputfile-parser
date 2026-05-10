# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-05-09

### Added
- Support for `root` field on parts. Behavior:
  - If Part.root is absolute → chapters resolve relative to that path
  - If Part.root is relative → resolves relative to Document.root (or JSON parent if Document.root absent)
  - If Part.root omitted → inherits Document.root resolution behavior
  - If no roots provided → all paths resolve relative to JSON file's parent directory
  See: 454182f
- `FileRef`, `Chapter`, and `Part` objects have back-references to parent objects to allow for easy document traversal (8064a8b)
- Unique `id` fields assigned to `Document`, `Part`, `Chapter`, and `FileRef` objects (2c68564)
- (meta) bespoke-to-json converter for legacy input file migration (d5a4e6f)
- `files` property for `Document` objects to list all files within the document, for easy file retrieval without Document traversal (6b11f76)

### Changes

- Relative root paths now resolved against JSON source (previously cwd) (7329df1)


### Fixes

- Relative root paths resolved agains JSON file location (instead of cwd), avoiding broken paths when script running from directory other than script dir (7329df1)

## [1.0.0] - 2025-04-30

### Added
- Initial release
- `Document`, `Part`, `Chapter`, `FileRef` dataclasses with typed properties
- `Document.from_json()` for parsing JSON input files
- `Document.to_json()` for serializing documents back to JSON
- Support for flat structure (`chapters` array only)
- Support for hierarchical structure (`parts` array with nested `chapters`)
- Auto-numbering for missing `number` fields on parts and chapters
- Default names (`Part X`, `Chapter X`) when `name` omitted
- Optional per-file display names via `{"path": "...", "name": "..."}` syntax
- Extensible `metadata` dictionary for custom key-value pairs
- `__str__` methods for human-readable output
- Comprehensive error messages with context
- Zero external dependencies (uses only Python standard library)
- Python 3.9+ compatibility

### Documentation
- README with JSON schema reference, API docs, and examples
- Demo scripts in `demos/` directory
- Example JSON files in `examples/` directory

---

[1.0.0]: https://github.com/bkuz114/inputfile-parser/releases/tag/v1.0.0
[2.0.0]: https://github.com/bkuz114/inputfile-parser/releases/tag/v2.0.0
