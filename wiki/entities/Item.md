---
title: Item
type: entity
confidence: 0.9
sources:
  - traitsui/item.py:64
  - traitsui/item.py:260
last_updated: 2026-05-19
stale: false
---

# Item

## Overview

Represents a single trait editor element in a `View`. Maps a trait name to an editor widget with optional configuration.

## Class (`traitsui/item.py:64`)

Key traits:

| Trait | Type | Purpose |
|-------|------|---------|
| `name` | Str | Trait name to edit |
| `label` | Str | Display label |
| `editor` | EditorFactory | Explicit editor override |
| `style` | Enum | `'simple'`, `'custom'`, `'text'`, `'readonly'` |
| `object` | Str | Context object reference (default `'object'`) |
| `show_label` | Bool | Whether to show label |
| `tooltip` | Str | Hover tooltip |
| `visible_when` | Str | Expression for conditional visibility |
| `enabled_when` | Str | Expression for conditional enabling |
| `defined_when` | Str | Expression for conditional inclusion |
| `width` / `height` | Float | Sizing (pixels or fractions) |
| `emphasized` | Bool | Bold/emphasized display |
| `resizable` | Bool | Whether item can resize |
| `id` | Str | Unique identifier for state persistence |

## Special Name Values

| Name | Meaning |
|------|---------|
| `''` (empty) | Static label (use `label` for text) |
| `'_'` | Horizontal separator |
| `' '` | 5-pixel spacer |
| Digits (e.g., `'20'`) | N-pixel spacer |

## String Parsing (`traitsui/item.py:260`)

Items support a compact string syntax:

```
[id:][object.][name]['['label']']`tooltip`[<width,height>][#^][$|@|*|~|;style]
```

Style suffixes: `$` = simple, `@` = custom, `*` = text, `~` = readonly, `;style` = named

## Convenience Subclasses

| Class | Purpose |
|-------|---------|
| `UItem` (line 418) | Item with `show_label=False` |
| `Custom` (line 429) | Item with `style='custom'` |
| `UCustom` (line 440) | Custom + no label |
| `Readonly` (line 451) | Item with `style='readonly'` |
| `Label` (line 473) | Static label (empty name) |
| `Heading` (line 485) | Section heading |
| `Spring` (line 497) | Expandable spacer |

## Usage

```python
View(
    Item('name'),                              # Simple
    Item('age', editor=RangeEditor(low=0)),    # With editor
    Item('bio', style='custom'),               # Custom style
    Item('status', enabled_when='is_active'),  # Conditional
    Label('Section Title'),                    # Static label
)
```

## Related

- [[Group]] — Container for Items
- [[View]] — Top-level structure
- [[Editor-Factory-Pattern]] — How editors are resolved
