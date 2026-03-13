# Contributing to Dungeon Explorer

Thank you for your interest in contributing! This guide covers everything you need to get a development environment running and submit great pull requests.

---

## Getting Started

```bash
# 1. Fork the repo on GitHub, then clone your fork
git clone https://github.com/souvik03-136/Terminal-based-AI-MMORPG.git
cd Terminal-based-AI-MMORPG

# 2. Add upstream remote
git remote add upstream https://github.com/souvik03-136/Terminal-based-AI-MMORPG.git

# 3. Full dev setup
task setup
task install:dev
```

---

## Development Workflow

```bash
# Always branch from main
git checkout main
git pull upstream main
git checkout -b feat/your-feature-name

# Make your changes, then:
task check     # lint + format + typecheck
task test      # run tests
git commit -m "feat: add fireball spell system"
git push origin feat/your-feature-name
# Open a PR on GitHub
```

---

## Commit Message Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add fireball spell to combat system
fix: prevent crash when inventory is full during loot drop
docs: update DOCUMENTATION.md with spell system diagram
refactor: extract item parsing into its own function
test: add unit tests for dice advantage/disadvantage
chore: bump google-generativeai to 0.9.0
```

---

## Code Style

- **Formatter:** `ruff format` (enforced in CI)
- **Linter:** `ruff check` (enforced in CI)
- **Type hints:** All new functions must have type annotations
- **Docstrings:** Public classes and non-trivial functions should have a one-line docstring

Run all checks at once:
```bash
task check
```

---

## Adding a New Command

1. Write the handler in `server/handlers/<module>.py`
2. Register it in `server/command_router.py` inside `_dispatch()`
3. Add it to the help text in `server/handlers/admin_handler.py`
4. Write unit tests in `tests/unit/test_command_router.py`
5. Update `DOCUMENTATION.md` Section 9 (API Reference table)

---

## Reporting Bugs

Use the **Bug Report** issue template. Include:
- Full traceback from the server logs (`LOG_LEVEL=DEBUG`)
- Steps to reproduce
- Python version and OS

---

## Security Issues

**Do not open a public issue for security vulnerabilities.**
Email `security@yourdomain.com` with details. We aim to respond within 48 hours.

---

## Code of Conduct

Be kind, be constructive. We're building a game, not a battlefield.