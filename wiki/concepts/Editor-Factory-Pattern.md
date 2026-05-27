---
title: Editor Factory Pattern
type: concept
confidence: 0.9
sources:
  - traitsui/editor_factory.py:36
  - traitsui/editor.py:50
  - traitsui/editor_factory.py:163
  - traitsui/editors/
last_updated: 2026-05-19
stale: false
---

# Editor Factory Pattern

## Overview

Every trait in a TraitsUI `View` is rendered by an **Editor** — a toolkit-specific widget that displays and edits the trait value. Editors are created by **EditorFactory** instances, which define configuration and resolve the correct toolkit-specific editor class.

## The Two Classes

### EditorFactory (`traitsui/editor_factory.py:36`)

The toolkit-independent factory. Responsibilities:
- Holds configuration (e.g., `low`, `high` for RangeEditor)
- Provides four style methods: `simple_editor()`, `custom_editor()`, `text_editor()`, `readonly_editor()`
- Resolves toolkit-specific editor classes via `_get_toolkit_editor()`

### Editor (`traitsui/editor.py:50`)

The toolkit-specific widget controller. Responsibilities:
- Creates and manages the actual widget (`self.control`)
- Synchronizes model trait ↔ widget state via `sync_value()`
- Handles undo/redo logging
- Disposes of resources on close

## Four Editor Styles

Every editor factory produces four variants:

| Style | Purpose | Example |
|-------|---------|---------|
| `simple` | Compact, inline widget | Dropdown for Enum |
| `custom` | Full-featured widget | Radio buttons for Enum |
| `text` | Text-only editing | Plain text field |
| `readonly` | Display only | Static label |

The style is determined by `Item.style` or the `View.style` default.

## Resolution Flow

```
Item(name='color', editor=EnumEditor(values=['red','green','blue']))
    │
    ▼
EnumEditor.simple_editor(ui, object, name, description)
    │
    ▼
EnumEditor._get_simple_editor_class()
    → _get_toolkit_editor("simple")  (line 163)
        → walks MRO, calls toolkit_object("enum_editor:SimpleEditor")
            → returns traitsui.qt.enum_editor.SimpleEditor
    │
    ▼
SimpleEditor(parent, ui=ui, object=object, name=name, factory=self)
    → Editor.init() creates the widget
    → Editor.sync_value() connects trait notifications
```

## Automatic Editor Selection

When no explicit `editor=` is specified on an Item, TraitsUI infers the editor from the trait type:

- `Str` → `TextEditor`
- `Int`/`Float` (with range) → `RangeEditor`
- `Bool` → `BooleanEditor`
- `Enum` → `EnumEditor`
- `List` → `ListEditor`
- `Instance` → `InstanceEditor`
- etc.

This mapping is defined by each trait type's `get_editor()` method in the Traits library.

## EditorWithListFactory (`traitsui/editor_factory.py:278`)

A subclass for editors that work with enumerated values:
- `values` — Static list of valid values
- `name` — Trait name on the object holding dynamic values
- `object` — Context object reference
- Handles dynamic update when the values list changes

Used by: `EnumEditor`, `CheckListEditor`, `SetEditor`

## Key Editor Lifecycle

1. **Construction:** `EditorFactory.simple_editor(ui, object, name, description)` creates the Editor
2. **`prepare(parent)`** (`traitsui/editor.py:238`): Common initialization
3. **`init(parent)`** (abstract): Toolkit-specific widget creation
4. **`sync_value()`**: Establishes trait ↔ editor synchronization
5. **`update_editor()`**: Initial population of widget from model
6. **`dispose()`** (`traitsui/editor.py:255`): Cleanup on UI close

## Value Synchronization

`Editor.sync_value(user_name, editor_name, mode)` (`traitsui/editor.py:333`):

| Mode | Direction |
|------|-----------|
| `'from'` | Model → Editor only |
| `'to'` | Editor → Model only |
| `'both'` | Bidirectional |

This uses Traits' `on_trait_change` mechanism to maintain consistency.

## Value Setting with Handler Interception

`Editor._set_value(value)` (`traitsui/editor.py:802`):
1. Calls `handler.setattr(info, object, name, value)`
2. Handler can intercept, modify, or reject the change
3. If not intercepted, sets the trait directly on the model
