"""Edit command for managing entries interactively."""

from datetime import datetime

import click

from ..cli import AppContext
from ..search_utils import find_multiple_matches


@click.command()
@click.option(
    "-i",
    "--id",
    "entry_id",
    type=int,
    default=None,
    help="Edit a specific entry by ID",
)
@click.option(
    "-s",
    "--search",
    "search_query",
    default=None,
    help="Search for an entry by text (fuzzy match)",
)
@click.pass_obj
def edit(ctx: AppContext, entry_id: int, search_query: str):
    """Edit or delete entries interactively.

    Opens today's entries in your default text editor for bulk editing,
    or edits a specific entry by ID.

    Examples:
        dwriter edit

        dwriter edit --id 42

        dwriter edit --search "redis cache"
    """
    # Handle search-based editing
    if search_query is not None:
        entries = ctx.db.get_all_entries()
        matches = find_multiple_matches(search_query, entries, limit=5, threshold=60)

        if not matches:
            ctx.console.print(
                f"[red]![/red] No entries found matching \"{search_query}\"."
            )
            return

        if len(matches) == 1:
            # Single high-confidence match
            entry, score = matches[0]
            ctx.console.print(
                f"[green]Found match:[/green] [{entry.id}] {entry.content} "
                f"(Match: {int(score)}%)"
            )
            entry_id = entry.id
        else:
            # Multiple matches - ask user to select
            ctx.console.print(
                f"[yellow]Multiple matches found for \"{search_query}\":[/yellow]"
            )
            for i, (entry, score) in enumerate(matches, 1):
                date_str = entry.created_at.strftime("%Y-%m-%d")
                ctx.console.print(
                    f"  {i}. [[cyan]{entry.id}[/cyan]] {date_str}: {entry.content} "
                    f"[dim]({int(score)}%)[/dim]"
                )

            choice = click.prompt(
                "Which entry do you want to edit? [1-5]", type=int, default=1
            )
            if choice < 1 or choice > len(matches):
                ctx.console.print("[red]Invalid selection.[/red]")
                return
            entry, _ = matches[choice - 1]
            entry_id = entry.id

    if entry_id is not None:
        # Edit specific entry
        try:
            entry = ctx.db.get_entry(entry_id)
        except ValueError:
            ctx.console.print(f"[red]![/red] Entry {entry_id} not found.")
            return

        edited_content = click.edit(entry.content)

        if edited_content is None:
            ctx.console.print("No changes made.")
            return

        edited_content = edited_content.strip()

        if not edited_content:
            if click.confirm("Content is empty. Delete this entry?"):
                ctx.db.delete_entry(entry_id)
                ctx.console.print("[green]✅[/green] Entry deleted.")
            return

        if edited_content != entry.content:
            ctx.db.update_entry(entry_id, content=edited_content)
            ctx.console.print("[green]✅[/green] Entry updated.")
        else:
            ctx.console.print("No changes made.")
    else:
        # Bulk edit today's entries
        today_date = datetime.now()
        entries = ctx.db.get_entries_by_date(today_date)

        if not entries:
            ctx.console.print("No entries for today to edit.")
            return

        # Create editable content
        editable_lines = []
        editable_lines.append("# Edit your entries below.")
        editable_lines.append("# Lines starting with '#' will be ignored.")
        editable_lines.append("# Format: [id] content | tag1, tag2 | project")
        editable_lines.append("#" + "-" * 60)

        for entry in entries:
            date_str = entry.created_at.strftime("%Y-%m-%d")
            time_str = entry.created_at.strftime("%I:%M %p")
            tags_str = ", ".join(entry.tag_names) if entry.tag_names else ""
            project_str = entry.project or ""
            line = (
                f"[{entry.id}] {date_str} | {time_str}: {entry.content} | "
                f"{tags_str} | {project_str}"
            )
            editable_lines.append(line)

        edited_text = click.edit("\n".join(editable_lines))

        if edited_text is None:
            ctx.console.print("No changes made.")
            return

        # Parse edited content
        lines = edited_text.strip().split("\n")
        updated_count = 0
        deleted_count = 0

        for line in lines:
            line = line.strip()

            # Skip comments and empty lines
            if not line or line.startswith("#"):
                continue

            # Parse line: [id] content | tags | project
            if "]" not in line:
                continue

            try:
                id_end = line.index("]")
                entry_id = int(line[1:id_end])
                rest = line[id_end + 1 :].strip()

                parts = rest.split("|")
                content = parts[0].strip()
                tags_str = parts[1].strip() if len(parts) > 1 else ""
                project_str = parts[2].strip() if len(parts) > 2 else ""

                # Skip if content is empty (means delete)
                if not content:
                    ctx.db.delete_entry(entry_id)
                    deleted_count += 1
                    continue

                # Parse tags
                tags = (
                    [t.strip().lstrip("#") for t in tags_str.split(",")]
                    if tags_str
                    else []
                )
                tags = [t for t in tags if t]  # Remove empty tags

                project = project_str if project_str else None

                # Update entry
                ctx.db.update_entry(
                    entry_id, content=content, tags=tags, project=project
                )
                updated_count += 1

            except (ValueError, IndexError):
                ctx.console.print(
                    f"[yellow]![/yellow] Could not parse line: {line}"
                )

        ctx.console.print(
            f"[green]✅[/green] Updated {updated_count} entries, "
            f"deleted {deleted_count}."
        )
