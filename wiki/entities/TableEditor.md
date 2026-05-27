---
title: TableEditor
type: entity
confidence: 0.85
sources:
  - traitsui/editors/table_editor.py:53
  - traitsui/qt/table_editor.py
  - traitsui/table_column.py
  - traitsui/tabular_adapter.py
last_updated: 2026-05-19
stale: false
---

# TableEditor

## Overview

The most complex editor in TraitsUI. Displays a list of objects as a tabular grid where each row is an object and each column maps to one of its traits.

## Factory (`traitsui/editors/table_editor.py:53`)

Key configuration traits:

| Trait | Type | Purpose |
|-------|------|---------|
| `columns` | List(TableColumn) | Column definitions |
| `editable` | Bool | Allow cell editing |
| `sortable` | Bool | Allow column sorting |
| `sort_model` | Bool | Sort underlying model (vs. view only) |
| `selection_mode` | Enum | `'row'`, `'rows'`, `'column'`, `'columns'`, `'cell'`, `'cells'` |
| `selected` | Any | Currently selected object(s) |
| `filter_name` | Str | Trait name for filter object |
| `show_toolbar` | Bool | Show add/delete toolbar |
| `row_factory` | Callable | Factory for new rows |
| `auto_size` | Bool | Auto-size columns to content |
| `configurable` | Bool | Allow user column configuration |

## TableColumn (`traitsui/table_column.py`)

Defines a single column:
- `name` — Trait name on row objects
- `label` — Column header
- `editable` — Per-column edit control
- `width` — Column width
- `horizontal_alignment` — Text alignment
- `format_func` — Custom formatting
- `menu` — Right-click context menu

Subclasses: `ObjectColumn`, `NumericColumn`, `ExpressionColumn`, `ListColumn`

## Architecture

```
TableEditor (factory, toolkit-independent)
    → Qt: traitsui/qt/table_editor.py
        → Uses QTableView + custom QAbstractTableModel
    → Wx: traitsui/wx/table_editor.py
        → Uses wx.grid.Grid
```

## Common Issues

The TableEditor is the most bug-reported editor. Known problem areas:
- Selection synchronization (selection state vs. model state)
- Column sorting with dynamic data
- Performance with large datasets
- Cell editor lifecycle (commit/revert on focus loss)
- Filter interaction with selection

## Related

- [[Editor-Factory-Pattern]] — How the factory creates editors
- [[Toolkit-Abstraction]] — How Qt/Wx implementations are dispatched
