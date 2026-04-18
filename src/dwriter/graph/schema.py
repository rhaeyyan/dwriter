"""LadybugDB schema DDL for the dwriter graph index."""

NODE_TABLES = [
    """CREATE NODE TABLE Entry(
        uuid STRING,
        content STRING,
        project STRING,
        created_at STRING,
        implicit_mood STRING,
        life_domain STRING,
        energy_level DOUBLE,
        PRIMARY KEY(uuid)
    )""",
    """CREATE NODE TABLE Todo(
        uuid STRING,
        content STRING,
        project STRING,
        priority STRING,
        status STRING,
        due_date STRING,
        created_at STRING,
        completed_at STRING,
        PRIMARY KEY(uuid)
    )""",
    "CREATE NODE TABLE Tag(name STRING, PRIMARY KEY(name))",
    "CREATE NODE TABLE Project(name STRING, PRIMARY KEY(name))",
]

REL_TABLES = [
    "CREATE REL TABLE ENTRY_HAS_TAG(FROM Entry TO Tag)",
    "CREATE REL TABLE TODO_HAS_TAG(FROM Todo TO Tag)",
    "CREATE REL TABLE ENTRY_IN_PROJECT(FROM Entry TO Project)",
    "CREATE REL TABLE TODO_IN_PROJECT(FROM Todo TO Project)",
    "CREATE REL TABLE REFERENCES_TODO(FROM Entry TO Todo)",
]

FTS_INDICES = [
    ("Entry", "entry_fts_idx", ["content"]),
    ("Todo", "todo_fts_idx", ["content"]),
]
