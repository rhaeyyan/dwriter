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

A commit is **Pending Review** if portability is ambiguous (e.g. shared utility change that may have AI assumptions baked in).

---

## Log

| Commit | Message | Status | Ported? | Notes |
|--------|---------|--------|---------|-------|
| `bea219a` | v4.6.0: Updated 2nd-Brain from chat to command center | AI-Only | — | 2nd-Brain is dwriter-ai exclusive |
| `fc60130` | v4.4.0 documentation update: added 2nd-brain-guide.md | AI-Only | — | Guide covers AI-only feature |
| `ee9118a` | Added new documentation: 2nd-Brain-GUIDE.md | AI-Only | — | |
| `ff19c7c` | Update project title to 'dwriter: AI Edition' | AI-Only | — | Title is branch-specific |
| `d3a0e33` | v4.5.1 - minor UI tweaks to delete and quick add entry form | Pending Review | No | UI changes may be portable — needs diff audit |
| `a750fb0` | visual overhaul and 2nd-Brain improvements | Pending Review | No | Split: overhaul may be portable, 2nd-Brain is not |
| `ba3b53a` | visual overhaul and 2nd-Brain improvements | Pending Review | No | Same as above |
| `26e8b72` | Resolve merge conflict in documentation/user-manual.md | Portable | Verify | Doc change only |
| `f2d38a4` | v4.3.1 2nd-Brain enhancements | AI-Only | — | |
| `fbc1afe` | v4.3.1 2nd-Brain enhancements | AI-Only | — | |
| `29e2e26` | v4.2.0: Dual Model Pipeline and README updates | AI-Only | — | Core AI architecture commit |
| `45398ab` | v4.7.0: Obsidian Export Feature | Portable | Yes | Checked src/dwriter/export/, src/dwriter/config.py, src/dwriter/commands/standup.py, src/dwriter/commands/review.py |
| `a42f56b` | v4.7.0: Obsidian Export TUI updates | AI-Only | — | Touches src/dwriter/tui/screens/briefing_modals.py and second_brain.py |

---

## Pending Review Queue
The following commits require diff audit before a portability decision can be made:

- `d3a0e33` — UI tweaks to delete and quick add form (TUI Architect to assess)
- `a750fb0` / `ba3b53a` — Visual overhaul (TUI Architect to split portable UI changes from 2nd-Brain work)

---

*Last updated: April 11, 2026 (Session 25)*
