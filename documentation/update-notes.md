# dwriter Update Notes

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
