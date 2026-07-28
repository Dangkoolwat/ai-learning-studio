# Suggested Commands
- Build: `python3 scripts/build.py`
- Check-only build: `python3 scripts/build.py --check`
- Targeted syntax check: `python3 -m py_compile scripts/build.py core/*.py`
- Local static preview: `python3 -m http.server 8000 --directory dist`
- Use repo-root relative paths; build commands assume current working directory is the repository root on macOS/Darwin.