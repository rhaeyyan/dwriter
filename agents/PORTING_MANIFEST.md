# dwriter — Porting Manifest

Maintained by the **Branch Integration Steward**.
Tracks the status of every `dwriter-ai` commit relative to `main`.

## Portability Rules
A commit is **Portable** if it:
- Touches no file under `src/dwriter/ai/`
- Introduces no `instructor`, `ollama`, or `openai` import anywhere in its diff
- Passes `uv run pytest` on `main` independently after cherry-pick

A commit is **AI-Only** if it:
- Modifies anything under `src/dwriter/ai/`
- Adds a command that depends on model calls (e.g. `ask`, `compress`)
- References `PermissionEnforcer`, `SummaryCompressor`, or any AI schema

A commit is **Pending Review** if the commit mixes Portable and AI-Only files and must be split before any part can be ported.

---

## Log

| Commit | Message | Status | Ported? | Notes |
|--------|---------|--------|---------|-------|
| `29e2e26` | v4.2.0: Dual Model Pipeline and README updates | AI-Only | — | Core AI architecture commit |
| `fbc1afe` | v4.3.1 2nd-Brain enhancements | AI-Only | — | |
| `f2d38a4` | v4.3.1 2nd-Brain enhancements | AI-Only | — | |
| `ff19c7c` | Update project title to 'dwriter: AI Edition' | AI-Only | — | Title is branch-specific |
| `ee9118a` | Added new documentation: 2nd-Brain-GUIDE.md | AI-Only | — | |
| `fc60130` | v4.4.0 documentation update: added 2nd-brain-guide.md | AI-Only | — | Guide covers AI-only feature |
| `8c4ab0f` | visual overhaul and 2nd-Brain improvements | Pending Review | Yes | Ported as `e185492` on main — configure/logs/standup/timer/todo/themes; ai/, second_brain.py, README, docs excluded; REMINDER_COLOR resolved to [bold #FF0000] |
| `1fea844` | visual overhaul and 2nd-Brain improvements | Pending Review | Yes | .gitignore `agents/` entry already on main; `agents/` deletions excluded (gitignored) |
| `f8f5f55` | v4.5.1 — minor UI tweaks to delete and quick add entry form | Pending Review | Yes | Ported as `143a3ad` on main — todo.py CSS specificity fix; logs.py #save-exit-row and #save-exit-btn changes superseded by f1ae4b6 port layout |
| `bea219a` | v4.6.0: Updated 2nd-Brain from chat to command center | AI-Only | — | 2nd-Brain is dwriter-ai exclusive |
| `26e8b72` | Resolve merge conflict in documentation/user-manual.md | Portable | Verify | Doc change only |
| `45398ab` | v4.7.0: Obsidian Export Feature | Portable | Yes | Checked src/dwriter/export/, config.py, commands/standup.py, commands/review.py |
| `a42f56b` | v4.7.0: Obsidian Export TUI updates | AI-Only | — | Touches tui/screens/briefing_modals.py and second_brain.py |
| `7d6e47d` | v4.8.1: Ruff/Mypy compliance pass | Pending Review | Yes | Ported as `f05479c` on main (non-AI files only) |
| `007beff` | v4.8.2: add Guard 4 file-size ceiling check | Pending Review | Yes | `scripts/check_guards.sh` ported as part of `f05479c`; agents/ additions excluded |
| `5bc4d3d` | docs: update todo CLI reference for subcommand restructure | Portable | Yes | Already present on main — ported in an earlier session |
| `425a7ca` | feat: resolve Guard 4 violations — decompose oversized modules | Pending Review | Yes | Ported as `f05479c` on main — `tui/ai_handlers.py` confirmed compatible (no ai/ imports) |
| `dfc3240` | remove agents/ from version control | AI-Only | — | Agents-only housekeeping; no effect on main |
| `807ac4c` | docs: update README version to v4.8.2 | AI-Only | — | AI Edition README |
| `996d2f9` | docs: sync update-notes.md with dwriter-ai branch history | AI-Only | — | AI Edition version history |
| `c572605` | docs: fix update-notes link and todo subcommand syntax in README | AI-Only | — | AI Edition README |
| `cf1d15d` | fix: include app.tcss in installed package via package-data | Portable | Yes | Ported as `8bf177e` on main |
| `7b58b69` | feat: Overdue task labels + resolve pre-flight violations | Pending Review | Yes | Ported as `d8f393b` on main — format_due_date + commands/todo/ E501 hygiene + 11 tests; todo.py excluded (main already has more complete Overdue system); ai/ files excluded |
| `9ff43d2` | docs: update README and update-notes for v4.8.4 | AI-Only | — | AI Edition version docs |
| `e7703d7` | fix: resolve +Nm date parsing ambiguity (months vs minutes) | Portable | Yes | Already present on main (empty cherry-pick — ported in earlier session) |
| `bf243c2` | docs: sync agents/HISTORY.md from main | AI-Only | — | Agents-only |
| `78d1e7d` | minor housekeeping | AI-Only | — | Only touches agents/HISTORY.md |
| `1484df4` | feat: integrate LadybugDB graph index + rewrite analytics engine | Pending Review | Yes | Ported as `e4bfda1` on main — `ai/permissions.py` and `ai/tools.py` excluded |
| `f633785` | feat: implement Closed Learning Loop with Fact extraction | AI-Only | — | Entirely in `src/dwriter/ai/` |
| `58ceef9` | README and Documentation updates | Pending Review | Yes | Ported as `b5e6ae6` on main — DEV-and-CONFIG.md CQRS architecture update; headless-readme.md (AI section only), sync-guide.md (AI mention), 2ND-BRAIN-GUIDE.md excluded |
| `cae9966` | Remove high-signal readability feature description | AI-Only | — | AI Edition README |
| `b5ebda4` | style: fix docstring formatting to satisfy ruff | Portable | Yes | Ported as `86fa264` on main — `search_facts_fts` (AI-only) excluded |
| `0945948` | fix: resolve CLI tag formatting word-wrap bug | Portable | Yes | Ported as `dc2e783` on main — HISTORY.md and pyproject version bump excluded |
| `7639f9a` | docs: update version number to 4.10.2 across documentation | AI-Only | — | AI Edition version numbers |
| `70dcec7` | docs: add development-history.md journal | Portable | Yes | Ported as `29b71eb` on main |
| `266c66c` | docs: add development history link to README | AI-Only | — | AI Edition README |
| `edcecde` | docs: expand development history | Portable | Yes | Ported as `7b99cf9` on main |
| `32227e1` | Remove duplicate AI-Free version link | AI-Only | — | AI Edition README |
| `cd7b87f` | docs: explain Core Concepts in development history | Portable | Yes | Ported as `5ca50a2` on main |
| `ff9561f` | Delete rest_of_history.txt | AI-Only | — | Housekeeping |
| `064464e` | Delete HISTORY.md | AI-Only | — | Housekeeping |
| `f1ae4b6` | feat: v4.10.3 — Insight Hub layouts, energy/mood forms, timer fix | Pending Review | Yes | Ported as `019b24e` on main — EnergySlider, MoodPicker, logs/timer form updates, break fix, .gitignore; report_builders.py + second_brain.py excluded |
| `8f3b744` | docs: expand use-cases and fix 2nd-Brain chat accuracy | AI-Only | — | References AI-specific features throughout |
| `20c6ca5` | feat: v4.10.4 — incremental graph index + auto-sync on add | Portable | Yes | Ported as `e406af0` on main — `project_fact`, `delete_facts_for_entry` (AI-only) excluded |
| `953a4cc` | fix: sync push failure — git init now uses -b main | Portable | Yes | Ported as `7b740cc` on main |
| `706bd99` | docs: document sync push bug fix in update-notes, sync-guide, README | Portable | Yes | Ported as `64e145c` on main |
| `2146fa7` | Update experimental version to v4.10.5 | AI-Only | — | AI Edition README only |
| `80a3fca` | fix: sync pull KeyError on implicit_mood from older devices | Portable | Yes | Ported as `494df0e` on main — docs portion dropped (sync-guide.md not on main; README diverged) |
| `e1e9abf` | feat: vector projection, RRF hybrid search, search_semantic AI tool | Pending Review | Yes | Ported as `536dba0` on main — graph/ vector additions, rrf_fuse, hybrid_search_entries, sync.py E501; ai/engine.py + ai/tools.py + search_graph_facts excluded |
| `aa90977` | docs: update README and update-notes for v4.10.6 on dwriter-ai | AI-Only | — | dwriter-ai branch-specific docs; equivalent updates applied manually to main |
| `5ee099c` | fix: harden graph hybrid-search path (portable) | Portable | Yes | Ported as `ff9b71f` on main — graph/search.py uniform row schema, graph/projector.py dim-validation + datetime fix, commands/graph.py datetime fix. Clean cherry-pick. |
| `8a3fafa` | fix: register search_semantic with PermissionEnforcer + decompose engine | AI-Only | — | Enforcer fix, ai/semantic.py extraction, search_semantic wiring, enforcer tests — all branch-local, never ports |
| `7d61e75` | feat: gutter-rail layout for journal entry display (portable) | Portable | Yes | Ported as `29737cb` on main. **Carried a hidden dependency:** ui_utils.py imports `get_weekday_color`/`WEEKDAY_COLORS`, which existed only on dwriter-ai's `tui/colors.py`. The cherry-pick applied cleanly but caused an ImportError on main — caught by Steward post-port pre-flight. Folded the weekday color map into `29737cb` to land a working unit. |

---

## Pending Review Queue

Commits that mix Portable and AI-Only changes — the Steward must split or file-level cherry-pick before any part can land on `main`:

| Commit | Split required |
|--------|---------------|
| *(queue empty — all commits through aa90977 ported or classified)* | |

---

## Recommended Port Order (Next Session)

All graph infrastructure and feature splits through `e1e9abf` are live on main. Remaining work:

1. ~~**`7b58b69` split**~~ — Done (`d8f393b`)
2. ~~**`f1ae4b6` split**~~ — Done (`019b24e`)
3. ~~**`e1e9abf` split**~~ — Done (`536dba0`)
4. ~~**`58ceef9` split**~~ — Done (`b5e6ae6`)
5. ~~**`f8f5f55` split**~~ — Done (`143a3ad`)
6. ~~**`8c4ab0f` / `1fea844` split**~~ — Done (`e185492`)

---

## Steward Watch — ~~divergence from `main`~~ RESOLVED (2026-06-30)

The hybrid-search hardening and gutter-rail layout are now **re-ported and live
on main** (`ff9b71f`, `29737cb`). Post-port pre-flight on main: 4 guards pass,
206 tests pass, ruff/mypy net-neutral vs the pre-port baseline (77/62 — main's
pre-existing debt, untouched by these ports), AI-free check clean.

`hybrid_search_entries` on `main` remains **caller-less staged infrastructure**
— its only consumer (`search_semantic`) is AI-only and never lands on `main`.
Intentional staging, not dead code.

### Lesson — hidden cross-file dependencies survive a clean cherry-pick

`7d61e75`'s `ui_utils.py` imported `get_weekday_color`/`WEEKDAY_COLORS` from
`tui/colors.py`. Those symbols existed only on dwriter-ai, so the cherry-pick
applied with **zero git conflicts** yet broke `main` at import time. Git merge
success ≠ portability. **Going forward:** a portable commit that adds a new
import must have that import's target verified present on `main`, or the
dependency ported in the same commit. The post-port runtime-import + pre-flight
check is what caught this; keep it mandatory.

---

*Last updated: 2026-06-30 — ported 5ee099c→ff9b71f and 7d61e75→29737cb to main (weekday-color dependency folded in); 8a3fafa classified AI-Only (branch-local). Steward Watch divergence resolved. Through 7d61e75 fully classified.*
