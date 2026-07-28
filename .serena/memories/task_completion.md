# Task Completion
- Treat `python3 scripts/build.py` as the primary completion check.
- For phase work that touches build internals, also run `python3 scripts/build.py --check` when practical.
- Verify generated output by inspecting `dist/` for the expected HTML, theme, and manifest files.
- Do not report completion if the build or output validation fails.