# dwriter Update Notes

## Version 4.10.3 - May 8, 2026

### 🚀 Features

#### 1. Insight Hub — Redesigned Report Layouts
All six Insight Hub reports have been rebuilt with richer, more structured layouts that make better use of available screen space:
- **Energy Radar**: Wider domain bars, color-coded green/yellow/red by level, peak and low domain summary.
- **Momentum**: Contextual execution assessment (strong / moderate / low) appended to the Say-Do ratio.
- **Golden Hour**: Day-of-week activity bars now intensity-colored relative to the peak day.
- **Stale Tasks**: Full entry content on the first line, project + age bar on the second — no truncation. Health summary bar at top. Task limit raised from 7 → 10.
- **Focus**: Big Rock project now renders a proportional bandwidth bar. Context switch count labeled with a qualitative assessment.
- **Weekly Pulse**: 7-day Mon–Sun activity grid (block characters + count row) added alongside the Deep Work Ratio bar.

#### 2. Active Insight Trigger Color Fix
The selected insight trigger button now renders its label in **cyan** (`#89dceb`) instead of near-black. Visible in all themes.

#### 3. Energy Slider & Mood Picker in Quick-Add Forms
Two new optional fields appear in the **Quick Add Entry** modal (Logs screen) and the **Session Complete** modal (timer completion):
- **Energy slider (1–10):** Color-coded handle (green ≥8 / yellow ≥5 / red <5). Keyboard-navigable with ←/→, clickable on the track.
- **Mood dropdown:** 🌊 Flow / 😊 Good / 😐 Meh / 😔 Low — blank by default. Both fields write to the existing `energy_level` and `implicit_mood` columns, so the Energy Radar and Weekly Pulse reports reflect user-supplied values immediately.

#### 4. Timer Break Toggle Fix
Flipping the Break toggle now immediately updates the minutes input field to the configured break duration. Previously the field retained the work duration (25m default), causing the timer to start at the wrong length.

### 🏗 Internal Architecture

- **`src/dwriter/tui/report_builders.py`** (new): Report text-building logic extracted from `SecondBrainScreen._generate_report()` into a pure-function module. `second_brain.py` reduced from 598 → 447 lines, clearing the 600-line File-Size Ceiling Guard.
- **`src/dwriter/tui/widgets/energy_slider.py`** (new): Lightweight `EnergySlider` widget — no Textual `Slider` dependency.

---

## Version 4.10.2 - May 1, 2026

### 🛠 Improvements & Fixes
- **CLI Formatting**: Resolved an issue in the `add` and `search` CLI commands where rich text markup codes were artificially inflating string lengths during the `textwrap` phase. This caused tags with hyphens to wrap unnaturally mid-word.
- **Search Output**: Fixed a minor spacing inconsistency before the `Project:` field in the `dwriter search` command output.
- **Documentation**: Updated all references to reflect the `4.10.2` version.

---

## Version 4.10.1 - April 20, 2026

### 🚀 Key Features

#### 1. Closed Learning Loop (Fact Extraction)
- **Durable Memory**: dwriter now automatically extracts "Facts" from your journal entries. These include durable user preferences ("I prefer working on backend tasks in the morning"), goals ("Goal: release the beta by June"), and constraints ("I can't work on weekends").
- **LadybugDB Fact Nodes**: Facts are stored as a dedicated node type in the graph index, linked back to their source entry via `EXTRACTED_FROM` relationships.
- **`search_facts` Tool**: The 2nd-Brain agent can now search through these extracted facts mid-conversation to provide more personalized and contextually aware advice.

### 🛠 Improvements & Fixes
- **AI Tool Reliability**: Fixed a bug where `search_facts` was missing from the agent's available tools array, causing tool execution errors.
- **Graph Search Accuracy**: Replaced generic FTS search with `search_facts_fts` to correctly handle Fact node schemas (text, category, source entry UUID).
- **Version reporting**: Bumped internal version to v4.10.1.

---

## Version 4.10.0 - April 17, 2026

### 🚀 Key Features

#### 1. Graph Index — `dw graph rebuild`
- New `dw graph rebuild` command fully clears and reprojects the LadybugDB graph index from SQLite. Run this after the first install or whenever you want to force-sync the index to the current database state.

### 🛠 Internal Architecture & Quality

- **Analytics Engine rewrite**: `analytics/engine.py` is now backed entirely by the LadybugDB graph index. All 18 behavioral metrics (streak, burnout score, deep work ratio, tag velocity, etc.) are computed via Cypher queries instead of SQLAlchemy ORM. The SQLite write path is unchanged; analytics reads from the derived graph index. Line count reduced from 516 → 393.
- **Output parity verified**: 26 new tests in `test_analytics_graph.py` assert that all 18 methods return the same types and correct values as the original implementation.

---

## Version 4.9.0 - April 17, 2026

### 🚀 Key Features

#### 1. LadybugDB Graph Index (CQRS Read Layer)
- dwriter now maintains a **LadybugDB property-graph index** alongside SQLite as a derived read side. SQLite remains the write-of-record and sync source-of-truth; the graph index is regenerable and can be discarded without data loss.
- **Graph schema**: Entry, Todo, Tag, and Project nodes connected by `ENTRY_HAS_TAG`, `TODO_HAS_TAG`, `ENTRY_IN_PROJECT`, `TODO_IN_PROJECT`, and `REFERENCES_TODO` edges.
- **Full-text search**: FTS indices on Entry and Todo content (porter-stemmed) via LadybugDB's FTS extension.
- **Auto-rebuild on sync pull**: The graph index is automatically rebuilt after every successful `dw sync --pull` merge.

#### 2. Graph-Backed AI Tools
Two new tools are now available to the 2nd-Brain agent in Follow-up mode:
- **`run_cypher`**: Execute read-only Cypher queries directly against the graph index for graph traversal, co-occurrence analysis, and cross-entity aggregation.
- **`search_graph`**: Full-text search over journal entries or todos using LadybugDB FTS — more semantically accurate than the previous fuzzy-match approach.

The legacy `search_journal`, `search_todos`, and `get_daily_standup` tools are retained for backward compatibility.

### 🛠 Internal Architecture & Quality

- **New module `src/dwriter/graph/`**: `schema.py` (DDL), `projector.py` (`GraphProjector` class — thread-safe, idempotent upserts), `search.py` (FTS helpers).
- **`sync/daemon.py`**: `_rebuild_graph_index()` called after every pull merge; failure is logged and non-fatal.
- **`ai/permissions.py`**: `run_cypher` and `search_graph` registered in `_read_tools`; Security Mode Guard continues to gate all tool calls.
- **13 new tests** in `test_graph.py` covering schema creation, node/edge projection, idempotency, full index rebuild, and FTS search.
- **`date_utils.py`**: Fixed pre-existing E501 line-length violation on the relative-time regex pattern.

---

## Version 4.8.4 - April 12, 2026
