---
title: Known Issues
type: synthesis
confidence: 0.7
sources:
  - wiki/raw/issues/
last_updated: 2026-05-19
stale: false
---

# Known Issues

Compiled from open GitHub issues on enthought/traitsui.

## TableEditor Issues

The TableEditor accounts for the most bug reports:

- **Selection synchronization** — Selected items can become out-of-sync with the actual selection widget state, especially after sorting or filtering
- **Column sorting** — Sorting can interact poorly with dynamic data updates
- **Performance** — Large datasets (1000+ rows) cause UI lag
- **Cell editing** — Focus loss during cell edit can lose changes

## TreeEditor Issues

- **Node refresh** — Tree doesn't always update when underlying data changes
- **Drag-and-drop** — Reordering can produce incorrect state
- **Multi-selection** — Extended selection mode has edge cases

## UITester Issues

- **Modal dialog testing** — `auto_process_events` must be disabled for modal dialogs to avoid deadlocks
- **Timing sensitivity** — Some tests require manual event processing delays
- **Registry coverage** — Not all editor interactions are registered

## General Framework Issues

- **visible_when/enabled_when** — Expression evaluation can be fragile with complex object references
- **Undo/redo** — Undo stack doesn't always capture all editor changes correctly
- **Toolkit parity** — Some features work on Qt but not Wx (or vice versa)
- **Disposal** — Editor disposal can leave dangling trait listeners if not done carefully

## Deprecation/Migration

- **Wx backend** — Receiving less maintenance, potential future deprecation
- **Python version support** — Ongoing updates to support latest Python versions
- **Qt6 migration** — Some APIs deprecated in Qt6 need updating

## Related

- [[TableEditor]] — Most-reported editor
- [[UITester]] — Testing framework issues
- [[Qt-vs-Wx]] — Backend-specific gaps
