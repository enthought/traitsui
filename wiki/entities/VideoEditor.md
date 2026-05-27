---
title: VideoEditor
type: entity
confidence: 0.8
sources:
  - traitsui/editors/video_editor.py:34
last_updated: 2026-05-19
stale: false
---

# VideoEditor

## Overview

A display-only video playback widget. Uses `BasicEditorFactory` for a minimal configuration surface.

## Factory (`traitsui/editors/video_editor.py:34`)

Key traits (using `CVType` — `ContextValue` for dynamic binding):

| Trait | Type | Purpose |
|-------|------|---------|
| `aspect_ratio` | CVType | Video aspect ratio |
| `muted` | CVType | Mute audio |
| `volume` | CVType | Volume level |
| `playback_rate` | CVType | Playback speed |
| `state` | CVType | Play/pause/stop state |
| `position` | CVType | Current playback position |
| `duration` | CVType | Total duration (read-only) |
| `media_status` | CVType | Loading/buffering status |
| `buffer` | CVType | Buffer status |

## Design

The VideoEditor uses `ContextValue` (CVType) pattern extensively — each trait can be bound to a trait name on the context object, enabling dynamic synchronization without hard-coding trait names.

## Usage

```python
class Player(HasTraits):
    video_url = Str()
    is_playing = Enum('stopped', 'playing', 'paused')
    
view = View(
    Item('video_url', editor=VideoEditor(state='is_playing'))
)
```

## Notes

- Display-only: no built-in playback controls (UI must be provided separately)
- Relies on backend media framework (Qt Multimedia)
- Relatively new addition to TraitsUI
