# Changes

## Files updated

- `.github/workflows/quality-check.yml`
- `assets/css/site.css`
- `assets/favicon.svg`
- `assets/js/navigation.js`
- `assets/js/prompt-copy.js`
- `assets/js/site.js`
- `components/prompt-item.html`
- `core/build_pipeline.py`
- `core/component_validation.py`
- `core/page_registry.py`
- `core/renderers/base.py`
- `core/template_engine.py`
- `core/template_models.py`
- `core/template_validation.py`
- `data/page-registry.json`
- `pages/index.md`
- `pages/sections/ai-assistant.md`
- `pages/sections/image-ai.md`
- `pages/sections/ready-to-use.md`
- `scripts/build.py`
- `templates/base.html`
- `templates/partials/head.html`
- `templates/partials/navigation.html`
- `templates/partials/site-header.html`

## Notes

- Added the production JS entrypoint and its modules for mobile navigation and prompt copy behavior.
- Extended prompt-item markup with a copy button and live status region.
- Relaxed the template renderer and validators to support repeated head metadata placeholders and canonical URLs when a production base URL is configured.
- Simplified the workflow to reuse `scripts/build.py --check` instead of maintaining a duplicate inline validation script.
