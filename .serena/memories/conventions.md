# Conventions
- Prefer minimal, explicit, standard-library Python.
- Use named exports / small focused modules; avoid unrelated refactors.
- Keep repository-relative paths and trailing-slash routes consistent.
- Preserve deterministic build output except approved timestamps and current-year footer text.
- Escape registry/navigation metadata before HTML insertion; do not escape rendered Markdown HTML twice.
- Phase 5 template files live only under `templates/` and are validated before rendering.