---
title: Qt vs Wx Backend Comparison
type: comparison
confidence: 0.8
sources:
  - traitsui/qt/
  - traitsui/wx/
  - wiki/raw/issues/
last_updated: 2026-05-19
stale: false
---

# Qt vs Wx Backend Comparison

## Overview

TraitsUI supports two GUI backends: **Qt** (via PyQt5/6 or PySide2/6) and **Wx** (via wxPython). Qt is the primary/recommended backend; Wx is maintained for legacy compatibility but receives less active development.

## Feature Parity

| Feature | Qt | Wx | Notes |
|---------|----|----|-------|
| Core editors | Full | Full | All standard editors work |
| TableEditor | Full | Full | Both have known selection bugs |
| TreeEditor | Full | Full | |
| VideoEditor | Yes | Limited | Qt Multimedia vs wx.media |
| BoundsEditor | Yes | Yes | Both in `extra/` |
| Completion mode (Enum) | `inline`/`popup` | `inline` only | Qt has richer completion |
| Drag-and-drop | Full | Partial | |
| High-DPI | Good | Poor | Qt handles scaling natively |
| Dark mode | Partial | No | Qt inherits system theme |
| UITester | Full | Full | Same API, different registries |

## Architecture Differences

### Qt Backend (`traitsui/qt/`)
- Uses PyQt5/6 or PySide2/6 (via `pyface.qt` compatibility layer)
- Model/View architecture for complex editors (QAbstractItemModel)
- Signal/slot connections for event handling
- QSS for styling

### Wx Backend (`traitsui/wx/`)
- Uses wxPython (Phoenix)
- Native OS widgets where possible
- Event binding via `Bind()`
- Platform-native look-and-feel

## Known Gaps (Wx limitations)

1. **No popup completion** for EnumEditor (Qt-only feature)
2. **VideoEditor** has limited functionality on Wx
3. **High-DPI support** is manual/incomplete
4. **Fewer active maintainers** — bugs may persist longer
5. **Testing coverage** is lower (UITester registries less complete)

## Selection Guidance

| Use Case | Recommendation |
|----------|----------------|
| New projects | Qt |
| Cross-platform consistency | Qt |
| Legacy Wx applications | Wx (keep existing) |
| Headless testing | null toolkit |
| Maximum native look | Wx (on each platform) |

## Related

- [[Toolkit-Abstraction]] — How backends are selected and dispatched
