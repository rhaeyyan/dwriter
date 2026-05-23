# dwriter Update Notes

## Version 4.10.7 - May 23, 2026

### 🎨 Visual Overhaul

#### Input Field Style
All input fields across the TUI have switched to a clean underline style:
- `border: solid` replaced with `border: none` + `border-bottom: solid $primary` on every `Input` widget.
- Focus state uses `border-bottom: solid $accent` for a consistent highlight without a full box border.
- Padding standardised to `1 2 0 2` across modals and config sections.
- Affects: `QuickAddEntryModal`, `EditEntryModal`, `EditTodoModal`, `AddTodoForm`, `ConfigureScreen`, `SessionCompleteModal`, `TimerScreen` config section, `RangeSelectionScreen`, `FilterSelectionScreen`.

#### Label Style
Section labels changed from `text-style: bold` to `color: $text-muted` throughout `QuickAddEntryModal`, `EditTodoModal`, `AddTodoForm`, and `TimerScreen` config section.

#### List Entry Formatting
- **Separator**: `|` replaced with `·` (`[dim]·[/]`) in both `LogsResultsView._format_entry()` and `TodoListView._format_todo()`.
- **Hanging indent**: Long entry content wraps with a consistent 2-space hanging indent via `_wrap_with_hanging_indent()` (logs) and `_wrap_todo_with_hanging_indent()` (todos). Rich markup tags are stripped before computing visible line width.

#### Panel & Border Updates
- `LogsScreen`: list border `#45475a` → `$primary`; background `$surface` → `$background`; `ListItem` padding `0` → `1 2`.
- `TodoScreen`: search panel `border: solid $secondary` → `border-bottom: solid $primary`; list border `$secondary` → `$primary`; `ListItem` padding `0` → `0 2`.
- `StandupScreen`: daily/weekly editor background hardcoded `#0d0f18` → `$background`.
- `TimerScreen`: config panel border `#3b494c` → `$primary`; config label `text-style: bold` removed.
- `ConfigureScreen`: section panels use `border-left: solid $primary` instead of `border: solid $border-blurred`.

#### Themes
`THEME_OPTIONS` in `themes.py` refactored to use a named `_THEME_ORDER` intermediate list for clarity.

---

## Version 4.10.6 - May 23, 2026

### 🚀 Vector Projection & RRF Hybrid Search

#### Graph Vector Index
- The LadybugDB graph index now stores a `FLOAT[768]` embedding column on `Entry` nodes.
- An HNSW vector index (`entry_vec_idx`) is created automatically when the schema is initialized — idempotent across restarts via `ALTER TABLE Entry ADD embedding FLOAT[768]` + `CREATE_VECTOR_INDEX`.
- `GraphProjector.project_entry()` decodes stored embeddings and writes them into the vector index alongside the entry node. Entries without embeddings index cleanly with a `NULL` embedding and remain retrievable via FTS.
- `GraphProjector.search_vector(query_embedding, limit)` performs approximate nearest-neighbour (ANN) lookup via `QUERY_VECTOR_INDEX('Entry', 'entry_vec_idx', $emb, limit)`.

#### Reciprocal Rank Fusion (RRF)
- `rrf_fuse(ranked_id_lists, k=60)` added to `search_utils.py`. Accepts any number of UUID-ranked lists and returns a single fused ranking without depending on raw relevance scores.
- `hybrid_search_entries(query, query_embedding, projector, limit)` in `graph/search.py` issues an FTS search and a vector ANN search in parallel, then fuses both result lists via RRF. Entries with no embedding still appear via FTS; entries with no FTS hit still appear via vector similarity.

#### `search_semantic` AI Tool (AI Edition only)
- New tool exposed to the 2nd-Brain agent: `search_semantic(query)` embeds the query string and calls `hybrid_search_entries`, returning up to 10 conceptually relevant entries ranked by fused FTS + ANN score.
- The agent uses this instead of plain FTS when the user asks questions that may not match exact logged wording — e.g., "what was I working on when I felt stuck?" surfaces flow-state and blocker entries even without keyword overlap.
- This tool is **AI Edition only** and not ported to `main`.

---

## Version 4.10.5 - May 15, 2026

### 🐛 Bug Fixes

#### Sync pull failure: `KeyError: 'implicit_mood'`
`dwriter sync` (pull direction) would crash with a `KeyError` when pulling JSONL produced by a device still on an older version of dwriter that did not yet serialize the `implicit_mood`, `life_domain`, or `energy_level` columns:

```
KeyError: 'implicit_mood'
  File ".../dwriter/sync/engine.py", line 110, in _merge_entry
    existing.implicit_mood = data["implicit_mood"]
```

**Root cause:** `_merge_entry` in `sync/engine.py` used hard-coded key access (`data["implicit_mood"]`) for all three columns added in the v4.10.3 schema migration. Any JSONL file serialized before that migration — i.e., from a device that hadn't yet upgraded — was missing those keys, causing a `KeyError` on the first such entry.

**Fix:** All three accesses changed to `data.get(...)`, defaulting to `None`. Entries pulled from older devices now merge cleanly with those fields left `NULL`, which is the correct value for an entry that pre-dates the columns.

---

#### Sync push failure: "src refspec main does not match any"
`dwriter sync --push` (and `dwriter sync --remote`) would fail with the error below on machines where `git init.defaultBranch` was not explicitly configured:

```
Push failed: error: src refspec main does not match any
error: failed to push some refs to '<remote>'
```

**Root cause:** `git init` without `-b main` creates a `master` branch on git ≥ 2.28 when `init.defaultBranch` is unset. The sync engine hard-coded `"main"` in both the merge and push steps, so `git push origin main` found no matching local branch.

**Fix:** `git init` now always passes `-b main` (`commands/sync.py`). Existing sync repos already initialised on `master` are automatically renamed to `main` on the next `dwriter sync` call — no manual action required.

---

## Version 4.10.4 - May 14, 2026

### 🚀 Features

#### 1. Incremental Graph Index
`dwriter graph rebuild` is now incremental by default. Instead of wiping and re-projecting every node on each run, it reads a watermark timestamp stored in `SyncMetadata` and only projects entries and todos that have been created or updated since the last sync. First run (no watermark) falls back to a full rebuild automatically.

Use `dwriter graph rebuild --full` to force a complete wipe-and-rebuild — the correct path after bulk deletions or index corruption.

#### 2. Auto-Sync Graph on Every Add
The graph index now updates automatically in the background after every `dwriter add` (CLI) and every entry submitted via the TUI omnibox. No manual `graph rebuild` is needed during normal use. The index is always current — FTS, Cypher queries, and the Analytical Engine reflect your latest entry the moment it is logged.

### 🏗 Internal Architecture

- **`database.py`**: `get_graph_watermark() -> datetime | None` and `set_graph_watermark(ts: datetime)` added. Watermark stored as `SyncMetadata(key="last_graph_sync")`, ISO 8601 string — mirrors the existing `lamport_clock` KV pattern. No schema migration required.
- **`database_entry_repo.py`**: `get_entries_since(watermark)` — `WHERE updated_at > watermark ORDER BY updated_at ASC`.
- **`database_todo_repo.py`**: `get_todos_since(watermark)` — `WHERE created_at > watermark OR completed_at > watermark` (Todo has no `updated_at`).
- **`graph/projector.py`**: `build_index_incremental(db)` added alongside `build_index()`. Reads watermark, projects delta, writes new watermark. Falls back to `build_index()` on first run then sets watermark.
- **`commands/graph.py`**: `rebuild` command gains `--full / -f` flag. Default path calls `build_index_incremental()`; `--full` calls `build_index()` and sets watermark.
- **`commands/add.py`**: Daemon thread started after `db.add_entry()` to call `build_index_incremental()`. Mirrors the existing proactive-tagging pattern — zero CLI latency impact.
- **`tui/app.py`**: `on_entry_added()` handler now spawns a Textual thread worker to call `build_index_incremental()` after every entry submitted via the TUI.

All seven files contain zero AI imports — commits classified **Portable** by Branch Integration Steward.

---

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
