---
title: RangeEditor
type: entity
confidence: 0.85
sources:
  - traitsui/editors/range_editor.py:35
  - traitsui/qt/range_editor.py
last_updated: 2026-05-19
stale: false
---

# RangeEditor

## Overview

Numeric range editor that dynamically selects its widget type based on value range and data type. Supports sliders, spinners, and text fields.

## Factory (`traitsui/editors/range_editor.py:35`)

Key traits:

| Trait | Type | Purpose |
|-------|------|---------|
| `low` / `high` | Numeric | Static range bounds |
| `low_name` / `high_name` | Str | Trait names for dynamic bounds |
| `mode` | Enum | `'auto'`, `'slider'`, `'xslider'`, `'spinner'`, `'enum'`, `'text'`, `'logslider'` |
| `is_float` | Bool | Float vs integer mode |
| `format_str` | Str | Display format string |
| `label_width` | Int | Width of value label |

## Dynamic Editor Selection (lines 209-266)

In `'auto'` mode, the factory chooses the editor class based on:
- Range extent (e.g., enum-style for very small ranges)
- Data type (int vs float)
- Whether bounds are dynamic

## Modes

| Mode | Widget |
|------|--------|
| `'auto'` | Automatic selection |
| `'slider'` | Standard slider + text field |
| `'xslider'` | Extended slider (larger range) |
| `'spinner'` | Spin box |
| `'enum'` | Dropdown of discrete values |
| `'text'` | Plain text entry |
| `'logslider'` | Logarithmic slider |

## Usage

```python
Item('temperature', editor=RangeEditor(low=-20, high=50, mode='slider'))
Item('volume', editor=RangeEditor(low=0.0, high=1.0, is_float=True))
```

## Related

- [[BoundsEditor]] — Dual-handle variant for selecting a sub-range
