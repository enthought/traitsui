---
title: CSVEditor
type: entity
confidence: 0.85
sources:
  - traitsui/editors/csv_list_editor.py
last_updated: 2026-05-19
stale: false
---

# CSVEditor (CSVListEditor)

## Overview

Edits a list trait as a comma-separated text string. Built on top of `TextEditor` with custom parsing and formatting.

## Factory (`traitsui/editors/csv_list_editor.py`)

Key components:
- `_eval_list_str()` (line 25): Parses CSV text into a list
- `_format_list_str()` (line 62): Formats a list as CSV text
- Extends `TextEditor` with custom `evaluate` and `format_func`

## Configuration

| Trait | Purpose |
|-------|---------|
| `sep` | Separator character (default: `','`) |
| `ignore_trailing_sep` | Ignore trailing separator |
| `auto_set` | Update on every keystroke vs. on Enter |

## Usage

```python
class MyModel(HasTraits):
    tags = List(Str)

view = View(Item('tags', editor=CSVListEditor()))
```

The user sees: `tag1, tag2, tag3` and edits as plain text.

## Related

- [[Editor-Factory-Pattern]] — How it extends TextEditor
