---
title: Group
type: entity
confidence: 0.9
sources:
  - traitsui/group.py:52
  - traitsui/group.py:406-511
last_updated: 2026-05-19
stale: false
---

# Group

## Overview

Container for Items and sub-Groups. Controls layout, orientation, and visual grouping of UI elements.

## Class (`traitsui/group.py:52`)

Key traits:

| Trait | Type | Default | Purpose |
|-------|------|---------|---------|
| `content` | List(ViewSubElement) | — | Child Items and Groups |
| `orientation` | Enum | `'vertical'` | `'vertical'` or `'horizontal'` |
| `layout` | Enum | `'normal'` | `'normal'`, `'flow'`, `'split'`, `'tabbed'`, `'fold'` |
| `columns` | Int | 1 | Grid column count |
| `show_border` | Bool | `False` | Draw border around group |
| `show_labels` | Bool | `True` | Show item labels |
| `label` | Str | `''` | Group title/tab label |
| `scrollable` | Bool | `False` | Enable scrolling |
| `id` | Str | `''` | For state persistence |

## Layout Modes

| Layout | Behavior |
|--------|----------|
| `'normal'` | Standard vertical/horizontal box |
| `'flow'` | Wrap items when space runs out |
| `'split'` | Resizable splitter between children |
| `'tabbed'` | Each child group as a tab |
| `'fold'` | Collapsible sections |

## Convenience Subclasses

| Class | Line | Equivalent |
|-------|------|------------|
| `HGroup` | 406 | `Group(orientation='horizontal')` |
| `VGroup` | 418 | `Group(orientation='vertical')` |
| `VGrid` | 430 | `Group(orientation='vertical', columns=...)` |
| `HFlow` | 441 | `Group(orientation='horizontal', layout='flow')` |
| `VFlow` | 456 | `Group(orientation='vertical', layout='flow')` |
| `VFold` | 470 | `Group(orientation='vertical', layout='fold')` |
| `HSplit` | 485 | `Group(orientation='horizontal', layout='split')` |
| `VSplit` | 498 | `Group(orientation='vertical', layout='split')` |
| `Tabbed` | 511 | `Group(layout='tabbed')` |

## ShadowGroup (`traitsui/group.py:524`)

Resolved version of a Group where `Include` references have been replaced with actual content. Created by `Group.get_shadow(ui)` (line 270).

## Usage

```python
View(
    HGroup(
        Item('first_name'),
        Item('last_name'),
    ),
    Tabbed(
        Group(Item('address'), label='Address'),
        Group(Item('phone'), label='Contact'),
    ),
    VSplit(
        Item('notes', style='custom'),
        Item('history', style='readonly'),
    ),
)
```

## Related

- [[Item]] — Individual elements inside groups
- [[View]] — Top-level container
