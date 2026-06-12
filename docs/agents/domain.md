# Domain Docs

How the engineering skills should consume this repo's domain documentation when exploring the codebase.

## Before exploring, read these

- **`CONTEXT.md`** at the repo root, or
- **`CONTEXT-MAP.md`** at the repo root if it exists — it points at one `CONTEXT.md` per context. Read each one relevant to the topic.
- **`docs/adr/`** — read ADRs that touch the area you're about to work in. In multi-context repos, also check `src/<context>/docs/adr/` for context-scoped decisions.

If any of these files don't exist, **proceed silently**. Don't flag their absence; don't suggest creating them upfront. The producer skill (`/grill-with-docs`) creates them lazily when terms or decisions actually get resolved.

## File structure

Single-context repo:

```
/
├── CONTEXT.md          ← not created yet; add when domain terms stabilize
├── docs/adr/           ← not created yet
├── docs/agents/        ← agent skills configuration (this folder)
└── friture/            ← application source
```

## Dock analysis widget

Dock-hosted analyzers implement **`DockAnalysisWidget`** (`friture/dock_analysis_widget.py`):

- `set_buffer` / `handle_new_data` — audio path from shared `AudioBuffer`
- `canvasUpdate` — display timer refresh (~25 ms)
- `pause` / `restart` — optional; `Dock` skips if missing
- `saveState` / `restoreState` / `settings_called` / `qml_file_name` / `view_model`

FFT-style docks should read history via **`RingBufferFrameReader`** (`friture/ring_buffer_frame_reader.py`). Chunk-only docks (levels, octave spectrum) may consume the latest `floatdata` chunk directly.

Integration tests: **`AudioHarness`** + **`wire_dock_analysis_widget`** in `friture/test/helpers.py`.

## Use the glossary's vocabulary

When your output names a domain concept (in an issue title, a refactor proposal, a hypothesis, a test name), use the term as defined in `CONTEXT.md`. Don't drift to synonyms the glossary explicitly avoids.

If the concept you need isn't in the glossary yet, that's a signal — either you're inventing language the project doesn't use (reconsider) or there's a real gap (note it for `/grill-with-docs`).

## Flag ADR conflicts

If your output contradicts an existing ADR, surface it explicitly rather than silently overriding:

> _Contradicts ADR-0007 (event-sourced orders) — but worth reopening because…_
