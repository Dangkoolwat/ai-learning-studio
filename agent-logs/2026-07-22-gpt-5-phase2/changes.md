# Phase 2 Changes

- Added the minimum page source at `pages/index.md` with the limited front matter format required for this phase.
- Added `core/build_pipeline.py` with source discovery, front matter parsing, limited Markdown rendering, route mapping, asset copying, manifest writing, and output validation.
- Refactored `scripts/build.py` into a build orchestration entry point with clear stage logging and optional `--check` support.
- Updated `.github/workflows/quality-check.yml` to run on `main` pushes and `workflow_dispatch`, use Python 3.12, run the build, and verify the generated outputs.
- Updated `requirements.txt` to reflect that the phase still uses only the Python standard library.
- Removed placeholder `.gitkeep` files from `pages/`, `core/`, `assets/`, `components/`, `css/`, `data/`, `design/`, and `templates/` because they were not required for this phase.

## Source format introduced

- `---
  title: ...
  description: ...
  route: ...
  lang: ko|en
  status: ...
  ---`
- The parser only accepts `title`, `description`, `route`, `lang`, and `status`.

## Supported Markdown subset

- `# ` headings
- `## ` headings
- paragraphs
- unordered list items beginning with `- `
- fenced code blocks with bare triple backticks
- blank lines

## Notes

- The build remains deterministic for identical inputs except for the UTC timestamp in the manifest.
- The pipeline intentionally does not implement sitemap, robots, 404, page types, components, or theme generation yet.
- The manifest stores `source_page_files` and `generated_output_files` without absolute paths.
