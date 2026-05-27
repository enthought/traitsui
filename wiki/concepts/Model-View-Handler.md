---
title: Model-View-Handler Pattern
type: concept
confidence: 0.9
sources:
  - traitsui/view.py:157
  - traitsui/handler.py:48
  - traitsui/ui.py:57
  - traitsui/ui_info.py
last_updated: 2026-05-19
stale: false
---

# Model-View-Handler Pattern

## Overview

TraitsUI implements a variant of MVC called **Model-View-Handler (MVH)**. Unlike traditional MVC where the Controller mediates all communication, in MVH:

- The **Model** is any `HasTraits` object with observable attributes
- The **View** is a declarative structure (not a live widget) that specifies layout
- The **Handler** provides lifecycle hooks and event interception on the live UI

The actual widget rendering is delegated to **Editors** (one per trait being displayed), making this closer to a **Model-View-Editor-Handler** architecture.

## Components

### Model

Any `HasTraits` subclass. The model knows nothing about its UI — it simply defines traits with types, defaults, and validation.

```python
class Person(HasTraits):
    name = Str()
    age = Int()
```

### View (`traitsui/view.py:157`)

A declarative description of UI structure:

```python
view = View(
    Item('name'),
    Item('age', editor=RangeEditor(low=0, high=150)),
    kind='live',
    title='Edit Person',
    handler=MyHandler()
)
```

Key traits:
- `content` — Top-level `Group` containing all Items/Groups
- `kind` — Presentation mode (see [[Dispatch-Modes]])
- `handler` — Handler instance for event logic
- `buttons` — Dialog buttons (OK, Cancel, Apply, etc.)

### Handler (`traitsui/handler.py:48`)

Controls runtime behavior through lifecycle hooks:

| Method | When Called | Purpose |
|--------|-----------|---------|
| `init(info)` | After UI construction | Final setup; return False to abort |
| `position(info)` | Before display | Window positioning |
| `close(info, is_ok)` | User attempts close | Validate; return False to prevent |
| `closed(info, is_ok)` | After close | Cleanup |
| `setattr(info, object, name, value)` | Trait being set by editor | Intercept/modify value setting |
| `<object>_<name>_changed(info)` | Named trait changes | React to specific trait changes |

### Controller (`traitsui/handler.py:507`)

A `Handler` subclass that holds a reference to the model:

```python
class PersonController(Controller):
    # self.model is the Person instance
    def object_name_changed(self, info):
        # React to model.name changing
        pass
```

Context becomes `{'object': model, 'controller': self, 'handler': self}`.

### ModelView (`traitsui/handler.py:563`)

Alternative pattern where the ModelView IS the context's `object`, and the wrapped model is accessible as `model`:

```python
class PersonView(ModelView):
    model = Instance(Person)
    formatted_name = Property(depends_on='model.name')
```

### UI (`traitsui/ui.py:57`)

The active running interface instance. Created by `View.ui()`:

- Holds the `context` dict, `view`, `handler`, and toolkit `control`
- Manages editor lifecycle (creation, sync, disposal)
- Evaluates `visible_when`/`enabled_when` expressions
- Routes trait changes to Handler via `Dispatcher` (line 887)

### UIInfo (`traitsui/ui_info.py`)

Lightweight wrapper passed to Handler methods. Provides access to:
- `ui` — The UI instance
- Named attributes for each editor (by Item id or trait name)
- `initialized` — Whether UI is fully constructed

## Data Flow

```
User edits widget
    → Editor._set_value()
        → Handler.setattr(info, object, name, value)
            → object.trait_set(**{name: value})
                → Trait notification fires
                    → UI.Dispatcher routes to Handler.<obj>_<name>_changed()
                    → Other editors update via sync_value()
```

## Usage Patterns

**Simple (default handler):**
```python
person.configure_traits()  # Auto-generates View, uses default Handler
```

**Custom view:**
```python
person.configure_traits(view=View(Item('name'), Item('age')))
```

**Controller pattern:**
```python
controller = PersonController(model=person)
controller.configure_traits()
```
