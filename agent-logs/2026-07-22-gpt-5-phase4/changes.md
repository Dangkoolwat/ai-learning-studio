# Phase 4 Changes

- Added the single human-authored theme source at `design/studio-default/design.md` with the confirmed front matter fields and the required `Colors`, `Typography`, `Spacing`, `Radius`, `Shadow`, and `Layout` token sections.
- Added theme data models in `core/theme_models.py` for normalized tokens, validated theme designs, the public theme registry, and the theme generation result.
- Added strict theme parsing and validation in `core/theme_validation.py` for front matter, section order, token syntax, allowed token values, and error metadata.
- Added theme discovery logic in `core/theme_parser.py` so the build can find valid `design.md` sources under `design/` without copying source files into `dist/`.
- Added theme asset generation in `core/theme_generator.py` to write `dist/themes/themes.json`, `dist/themes/studio-default/tokens.json`, `dist/themes/studio-default/style.css`, and `dist/themes/studio-default/manifest.json`.
- Reworked `core/build_pipeline.py` so the build now loads themes, generates the theme assets, injects `data-theme="studio-default"` into the published HTML, links one stylesheet per page, and records theme metadata in `dist/build-manifest.json`.
- Extended `core/errors.py` so theme failures can report `theme_id`, `section`, and `token_name` alongside path and field context.
- Updated `.github/workflows/quality-check.yml` to run the build and verify the generated theme registry, theme files, theme metadata, stylesheet link, and published HTML.
- Updated `scripts/build.py` docstring and `requirements.txt` comment to match Phase 4.
- No pages, routing behavior, components, prompt builders, themes beyond the confirmed default theme, or external dependencies were introduced.
