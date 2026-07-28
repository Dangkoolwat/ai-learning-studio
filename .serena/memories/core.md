# Core
- Static site built from `data/` + `pages/` + `design/` + `templates/` through Python; generated output goes to `dist/`.
- Confirmed top-level IA stays fixed: `AI 체험 실습`, `바로 사용하기`, `AI 도우미`, `이미지 AI` with max depth 2.
- Page registry and navigation data are authoritative; routes, canonical paths, sitemap URLs, and menu links must stay aligned.
- Build pipeline is phase-gated and must fail closed on contract violations.
- Phase 4 theme generation is authoritative for active theme assets; Phase 5 template engine becomes the authoritative HTML shell wrapper.
- Read `mem:tech_stack` for tools/runtime, `mem:conventions` for coding/build conventions, `mem:suggested_commands` for local commands, and `mem:task_completion` for verification commands.