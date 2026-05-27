---
title: Handler
type: entity
confidence: 0.9
sources:
  - traitsui/handler.py:48
  - traitsui/handler.py:507
  - traitsui/handler.py:563
last_updated: 2026-05-19
stale: false
---

# Handler

## Overview

The runtime controller for a TraitsUI interface. Provides lifecycle hooks, event interception, and trait change notifications.

## Class (`traitsui/handler.py:48`)

## Lifecycle Methods

| Method | Signature | Purpose |
|--------|-----------|---------|
| `init` | `(info) → bool` | Post-construction setup; return False to abort |
| `position` | `(info)` | Window positioning before display |
| `close` | `(info, is_ok) → bool` | Validate close; return False to prevent |
| `closed` | `(info, is_ok)` | Post-close cleanup |

## Event Methods

| Method | Signature | Purpose |
|--------|-----------|---------|
| `setattr` | `(info, object, name, value)` | Intercept trait setting from editors |
| `perform` | `(info, action, event)` | Handle toolbar/menu actions |
| `apply` | `(info)` | Called on Apply button |
| `revert` | `(info)` | Called on Revert button |

## Dynamic Trait Change Handlers

The `UI.Dispatcher` automatically connects methods matching the pattern:

```python
def <object>_<name>_changed(self, info):
    ...
```

For example, `object_name_changed` is called when `info.object.name` changes.

Extended form: `<object>_<name>_changed(self, info, object, name, old, new)`

## Subclasses

### Controller (`traitsui/handler.py:507`)

Holds a `model` reference. Context = `{'object': model, 'controller': self, 'handler': self}`.

```python
class MyController(Controller):
    def object_name_changed(self, info):
        # self.model is the object being edited
        pass
```

### ModelView (`traitsui/handler.py:563`)

The ModelView IS the context's `'object'`; the wrapped model is `info.model`.

```python
class MyModelView(ModelView):
    model = Instance(MyModel)
    display_name = Property(depends_on='model.name')
```

## UIInfo

The `info` parameter passed to all handler methods provides:
- `info.ui` — The `UI` instance
- `info.<name>` — Direct access to editors by trait name or Item id
- `info.initialized` — Whether UI is fully set up

## Usage

```python
class PersonHandler(Handler):
    def close(self, info, is_ok):
        if is_ok and not info.object.name:
            error(info.ui.control, "Name is required")
            return False
        return True

    def object_age_changed(self, info):
        if info.object.age >= 18:
            info.ui.title = "Adult Editor"
```

## Related

- [[Model-View-Handler]] — Overall pattern
- [[View]] — Where handler is specified
