---
title: BoundsEditor
type: entity
confidence: 0.8
sources:
  - traitsui/qt/extra/bounds_editor.py:196
  - traitsui/wx/extra/bounds_editor.py:245
last_updated: 2026-05-19
stale: false
---

# BoundsEditor

## Overview

A dual-handle range selection editor that allows users to select both a low and high value within a defined range. Uses a custom `RangeSlider` widget with two draggable handles.

## Location

Unlike most editors, BoundsEditor lives in the `extra/` subdirectory of each backend:
- Qt: `traitsui/qt/extra/bounds_editor.py`
- Wx: `traitsui/wx/extra/bounds_editor.py`

## Key Traits

| Trait | Purpose |
|-------|---------|
| `low` / `high` | Overall range bounds |
| `low_name` / `high_name` | Dynamic bound trait names |
| `format` | Display format string |
| `label_width` | Width of value labels |

## Widget

Uses a custom `RangeSlider` widget that renders two handles on a single track. The user drags either handle to adjust the low/high selection.

## Usage

```python
class MyModel(HasTraits):
    selection_low = Float(20.0)
    selection_high = Float(80.0)

view = View(
    Item('selection_low',
         editor=BoundsEditor(low=0.0, high=100.0))
)
```

## Related

- [[RangeEditor]] — Single-value range editor
