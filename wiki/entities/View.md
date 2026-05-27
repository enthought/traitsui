---
title: View
type: entity
confidence: 0.9
sources:
  - traitsui/view.py:157
  - traitsui/view.py:79-116
last_updated: 2026-05-19
stale: false
---

# View

## Overview

The declarative structure that defines a TraitsUI interface. A `View` specifies what traits to show, how to lay them out, and how the UI should behave.

## Class (`traitsui/view.py:157`)

Key traits:

| Trait | Type | Default | Purpose |
|-------|------|---------|---------|
| `content` | Group | — | Top-level group containing all elements |
| `kind` | ViewKind | `'live'` | Presentation mode (see [[Dispatch-Modes]]) |
| `handler` | Handler | `Handler()` | Event handler |
| `title` | Str | `''` | Window title |
| `buttons` | List | — | Dialog buttons |
| `resizable` | Bool | `False` | Allow resize |
| `scrollable` | Bool | `False` | Add scroll bars |
| `width` / `height` | Float | -1 | Window dimensions |
| `x` / `y` | Float | -1 | Window position |
| `style` | EditorStyle | `'simple'` | Default editor style |
| `dock` | DockStyle | — | Docking behavior |
| `menubar` | MenuBar | — | Menu bar definition |
| `toolbar` | ToolBar | — | Toolbar definition |
| `key_bindings` | KeyBindings | — | Key binding definitions |
| `close_result` | Bool | — | Result when closed via window X |

## Construction

Views accept Items and Groups as positional arguments:

```python
View(
    Group(
        Item('name'),
        Item('age'),
        label='Personal Info'
    ),
    Item('email'),
    title='Edit Person',
    kind='modal',
    buttons=OKCancelButtons
)
```

## Key Methods

- `ui(context, parent, kind)` (line 376): Creates a `UI` instance and launches the GUI
- `replace_include(...)`: Resolves `Include` references

## Related

- [[Model-View-Handler]] — The overall MVH pattern
- [[Dispatch-Modes]] — How `kind` affects behavior
- [[Item]] — Individual fields
- [[Group]] — Layout containers
