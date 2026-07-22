# Phase 6 Changes

- Added `core/renderer_models.py` to define the approved renderer IDs, renderer validation status, renderer context model, renderer result model, and the renderer-specific block dataclasses.
- Added `core/renderer_validation.py` to parse and validate machine-readable control blocks, renderer contexts, and renderer results.
- Added `core/page_renderers.py` as the renderer registry and dispatcher.
- Added `core/renderers/__init__.py`, `core/renderers/base.py`, `core/renderers/landing.py`, `core/renderers/static_prompt.py`, `core/renderers/prompt_builder.py`, and `core/renderers/practice_timeline.py` for the approved renderer implementations.
- Updated `core/errors.py` so build errors can report renderer-specific validation context.
- Updated `core/template_models.py` and `core/template_engine.py` so the shared template layer receives renderer output as `main_html`.
- Reworked `core/build_pipeline.py` so renderer parsing and dispatch happen inside the build flow and renderer metadata is written into the manifest.
- Updated `scripts/build.py` and `requirements.txt` only to keep the bootstrap entry point and dependency contract aligned with the new renderer phase.
- Updated `.github/workflows/quality-check.yml` so CI runs the build and the renderer-focused validation checks.
- Updated `pages/sections/ai-practice.md`, `pages/sections/ready-to-use.md`, `pages/sections/ai-assistant.md`, and `pages/sections/image-ai.md` to include the approved `prompt` control block examples needed by the renderer parser.
- Preserved the confirmed navigation structure, page registry shape, route set, theme architecture, template architecture, and project documentation without redesign.
- No new page types, no extra dependencies, no Node.js, no npm, no component library, no final UI, and no later-phase rendering features were introduced.
