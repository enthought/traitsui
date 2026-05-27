---
title: Dispatch Modes
type: concept
confidence: 0.85
sources:
  - traitsui/view.py:79-116
  - traitsui/ui.py:226-235
  - traitsui/toolkit.py:117-195
last_updated: 2026-05-19
stale: false
---

# Dispatch Modes

## Overview

The `View.kind` trait determines how a UI is presented and how edits are committed. This is called the "dispatch mode" because the `UI.ui()` method dispatches to `toolkit().ui_<kind>()`.

## Available Modes

| Kind | Modal? | Live? | Description |
|------|--------|-------|-------------|
| `'live'` | No | Yes | Default. Non-modal, edits apply immediately |
| `'livemodal'` | Yes | Yes | Modal dialog, edits apply immediately |
| `'modal'` | Yes | No | Modal dialog, edits a clone; Apply/OK commits |
| `'nonmodal'` | No | No | Non-modal dialog, edits a clone; Apply/OK commits |
| `'panel'` | No | Yes | Embeddable panel (requires parent widget) |
| `'subpanel'` | No | Yes | Panel without command buttons |
| `'popup'` | No | Yes | Frameless popup, active while mouse is inside |
| `'popover'` | No | Yes | Frameless popup, active while over invoking control |
| `'info'` | No | Yes | Temporary popup overlaying invoking control |
| `'wizard'` | Yes | No | Multi-page wizard with Next/Back/Finish |

## Live vs. Clone-and-Commit

**Live modes** (`live`, `livemodal`, `panel`, `subpanel`, `popup`, `popover`, `info`):
- Editors directly modify the original model object
- Changes are visible immediately to all observers
- Cancel reverts changes via undo

**Clone-and-commit modes** (`modal`, `nonmodal`, `wizard`):
- The UI creates a working copy of the context
- Edits modify the copy only
- OK/Apply copies changes back to the original
- Cancel discards the copy

## Dispatch Mechanism

In `UI.ui()` (`traitsui/ui.py:226`):

```python
def ui(self, parent, kind):
    self.rebuild = getattr(toolkit(), "ui_" + kind)
    self.rebuild(self, parent)
```

Each toolkit implements all `ui_<kind>` methods to create the appropriate window/dialog type with correct modality and button configuration.

## Usage

```python
# Default live editing
view = View(Item('name'), kind='live')

# Modal dialog with OK/Cancel
view = View(Item('name'), kind='modal', buttons=OKCancelButtons)

# Embedded panel (for use inside another widget)
view = View(Item('name'), kind='panel')
```
