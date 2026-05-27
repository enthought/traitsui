---
title: TreeEditor
type: entity
confidence: 0.85
sources:
  - traitsui/editors/tree_editor.py:63
  - traitsui/tree_node.py
  - traitsui/qt/tree_editor.py
last_updated: 2026-05-19
stale: false
---

# TreeEditor

## Overview

Hierarchical tree view editor for displaying and editing object graphs. Supports multi-level nesting, drag-and-drop, context menus, and inline editing.

## Factory (`traitsui/editors/tree_editor.py:63`)

Key configuration traits:

| Trait | Type | Purpose |
|-------|------|---------|
| `nodes` | List(TreeNode) | Node type definitions |
| `editable` | Bool | Allow editing |
| `hide_root` | Bool | Hide the root node |
| `selection_mode` | Enum | `'single'` or `'extended'` |
| `selected` | Any | Currently selected node object |
| `click` / `dclick` | Event | Click/double-click events |
| `on_select` / `on_dclick` | Callable | Selection callbacks |
| `show_icons` | Bool | Display node icons |

## TreeNode (`traitsui/tree_node.py`)

Defines how an object type appears in the tree:

- `node_for` — List of class types this node handles
- `children` — Trait name containing child objects
- `label` — Trait name or string for display label
- `icon_item` / `icon_group` / `icon_open` — Icons
- `menu` — Context menu actions
- `add` — List of addable child types
- `move` — Allow drag-and-drop reordering
- `copy` / `delete` / `rename` — Permission flags

## Standard Actions

Defined at module level in `traitsui/editors/tree_editor.py`:
- `CopyAction`, `CutAction`, `PasteAction`
- `DeleteAction`, `RenameAction`
- `NewAction`

## Architecture

The Qt implementation uses `QTreeView` with a custom model. The Wx implementation uses `wx.TreeCtrl`.

## Common Patterns

```python
tree_editor = TreeEditor(
    nodes=[
        TreeNode(node_for=[Folder], children='files', label='name'),
        TreeNode(node_for=[File], label='name', icon_item='file'),
    ],
    hide_root=True,
    editable=True,
)
```

## Related

- [[TableEditor]] — Alternative flat-list display
- [[Editor-Factory-Pattern]] — Factory pattern
