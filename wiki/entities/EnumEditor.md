---
title: EnumEditor
type: entity
confidence: 0.9
sources:
  - traitsui/editors/enum_editor.py:34
  - traitsui/editor_factory.py:278
last_updated: 2026-05-19
stale: false
---

# EnumEditor

## Overview

Single-selection editor for enumerated values. Renders as a dropdown (simple style) or radio buttons (custom style).

## Factory (`traitsui/editors/enum_editor.py:34`)

Extends `EditorWithListFactory`. Key traits:

| Trait | Type | Purpose |
|-------|------|---------|
| `values` | List/Dict | Static value list |
| `name` | Str | Trait name for dynamic values |
| `cols` | Int | Number of columns for radio layout |
| `mode` | Enum | `'radio'` or `'list'` (custom style) |
| `completion_mode` | Enum | `'inline'` or `'popup'` (Qt only) |
| `evaluate` | Callable | Value transformation function |

## Styles

| Style | Rendering |
|-------|-----------|
| Simple | Dropdown/combobox |
| Custom | Radio buttons (mode='radio') or list widget (mode='list') |
| Text | Text field with completion |
| Readonly | Static label |

## Dynamic Values

Values can come from:
1. Static `values` list on the factory
2. A trait on the edited object (via `name`)
3. A trait on another context object (via `object` + `name`)

The editor updates automatically when the source list changes.

## Usage

```python
Item('color', editor=EnumEditor(values=['red', 'green', 'blue']))
Item('status', editor=EnumEditor(name='available_statuses'))
```
