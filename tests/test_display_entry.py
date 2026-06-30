"""Structure tests for the gutter-rail entry renderer (ui_utils.display_entry).

Output is captured as plain text (Rich ``record`` mode strips styling), so these
assert the visible arrangement and the edge cases — rail, header segments,
right-aligned id, midnight time suppression, empty tags/project/domain.

``life_domain`` is set via ``setattr`` rather than the Entry constructor so the
test stays portable to the AI-free ``main`` branch, where the column is absent.
"""

import io
from datetime import datetime
from types import SimpleNamespace

from rich.console import Console

from dwriter.database import Entry, Tag
from dwriter.ui_utils import display_entry

# 2026-06-30 is a Tuesday; 2026-06-29 is a Monday.
TUESDAY = datetime(2026, 6, 30, 14, 34)
MONDAY_MIDNIGHT = datetime(2026, 6, 29, 0, 0, 0)


def make_config(show_id=True, date_format="YYYY-MM-DD", clock_24hr=False):
    return SimpleNamespace(
        display=SimpleNamespace(
            show_id=show_id,
            date_format=date_format,
            clock_24hr=clock_24hr,
        )
    )


def make_entry(content, created_at, tags=None, project=None, domain=None, id=1):
    entry = Entry(id=id, content=content, created_at=created_at, project=project)
    if tags:
        entry.tags = [Tag(name=t) for t in tags]
    if domain is not None:
        # setattr (not constructor) keeps this portable to main, where Entry
        # has no life_domain column.
        entry.life_domain = domain
    return entry


def render(entry, config=None):
    console = Console(width=64, record=True, file=io.StringIO())
    display_entry(console, entry, config or make_config())
    return console.export_text()


def test_basic_structure_has_rail_header_and_footer():
    entry = make_entry(
        "Finished the vector projection work today.",
        TUESDAY,
        tags=["work", "rag"],
        project="dwriter",
        domain="work",
        id=3,
    )
    out = render(entry)
    lines = out.splitlines()

    # Header line: weekday + date + time + domain, no rail, id right-aligned.
    assert lines[0].startswith("  Tue · 2026-06-30 · 02:34 PM · work")
    assert lines[0].rstrip().endswith("#3")
    # Body + footer lines carry the gutter rail.
    assert any(line.startswith("▌ ") for line in lines)
    assert "Finished the vector projection work today." in out
    # Footer: tags then project, dot-separated.
    assert "#work · #rag · &dwriter" in out


def test_midnight_entry_omits_time():
    entry = make_entry("Quick note before bed.", MONDAY_MIDNIGHT)
    out = render(entry)
    assert out.splitlines()[0].startswith("  Mon · 2026-06-29")
    assert "AM" not in out and "PM" not in out
    assert "00:00" not in out


def test_show_id_false_hides_id():
    entry = make_entry("No id please.", TUESDAY, id=7)
    out = render(entry, make_config(show_id=False))
    assert "#7" not in out


def test_empty_tags_and_project_have_no_footer():
    entry = make_entry("Just content, nothing else.", TUESDAY)
    out = render(entry)
    # No footer markers, and no stray "None" from missing optional fields.
    assert "&" not in out
    assert "None" not in out
    # Header has no trailing domain segment (only weekday/date/time before id).
    assert "· work" not in out


def test_domain_appears_in_header_when_present():
    entry = make_entry("Logged a workout.", TUESDAY, domain="health")
    out = render(entry)
    assert "· health" in out.splitlines()[0]


def test_clock_24hr_setting_is_honored():
    entry = make_entry("Afternoon sync.", TUESDAY)
    out = render(entry, make_config(clock_24hr=True))
    assert "14:34" in out
    assert "PM" not in out


def test_long_content_wraps_under_the_rail():
    entry = make_entry(
        "word " * 40,  # forces several wrapped lines at width 64
        TUESDAY,
    )
    out = render(entry)
    body_lines = [ln for ln in out.splitlines() if ln.startswith("▌ ")]
    assert len(body_lines) > 1
    # Every wrapped body line stays within the console width.
    assert all(len(ln) <= 64 for ln in body_lines)
