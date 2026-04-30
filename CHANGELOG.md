# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
