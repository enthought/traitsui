---
title: UITester
type: entity
confidence: 0.85
sources:
  - traitsui/testing/tester/ui_tester.py:24
  - traitsui/testing/tester/ui_wrapper.py
  - traitsui/testing/tester/command.py
  - traitsui/testing/tester/query.py
  - traitsui/testing/_gui.py
last_updated: 2026-05-19
stale: false
---

# UITester

## Overview

A testing framework for TraitsUI applications that provides programmatic interaction with live UI elements without manual GUI manipulation.

## Class (`traitsui/testing/tester/ui_tester.py:24`)

Key API:

| Method | Purpose |
|--------|---------|
| `create_ui(object, ui_kwargs)` | Context manager: creates and disposes UI |
| `find_by_name(ui, name)` | Find editor by trait name → `UIWrapper` |
| `find_by_id(ui, id)` | Find editor by Item/Group id → `UIWrapper` |

Configuration:
- `registries` — Extensible list of `TargetRegistry` objects
- `delay` — Configurable delay for visual debugging
- `auto_process_events` — Controls automatic event processing

## UIWrapper

Returned by `find_by_name`/`find_by_id`. Provides chained interaction:

```python
wrapper = tester.find_by_name(ui, "name")
wrapper.perform(command.KeySequence("hello"))
wrapper.perform(command.KeyClick("Enter"))
value = wrapper.inspect(query.DisplayedText())
```

## Commands (`traitsui/testing/tester/command.py`)

- `KeySequence(text)` — Type text
- `KeyClick(key)` — Press a key
- `MouseClick()` — Click
- `MouseDClick()` — Double-click

## Queries (`traitsui/testing/tester/query.py`)

- `DisplayedText()` — Get displayed text
- `IsChecked()` — Checkbox state
- `IsEnabled()` — Enabled state
- `SelectedText()` — Selected item text

## Registry System

Each builtin editor has a registered set of supported commands and queries in `traitsui/testing/tester/_ui_tester_registry/`. Custom editors can extend the registry.

## Utilities

- `process_cascade_events()` (`traitsui/testing/_gui.py`): Process pending GUI events
- `reraise_exceptions()` (`traitsui/testing/_exception_handling.py`): Context manager for capturing exceptions in event handlers

## Usage

```python
from traitsui.testing.api import UITester, command, query

tester = UITester()
with tester.create_ui(my_model) as ui:
    name_editor = tester.find_by_name(ui, "name")
    name_editor.perform(command.KeySequence("Alice"))
    name_editor.perform(command.KeyClick("Enter"))
    assert my_model.name == "Alice"
```

## Related

- [[Editor-Factory-Pattern]] — Editors being tested
- [[Handler]] — Handler lifecycle during tests
