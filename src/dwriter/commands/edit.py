"""Edit command for managing entries interactively."""

import click

from ..database import Database


@click.command()
@click.option(
    "-i",
    "--id",
    "entry_id",
    type=int,
    default=None,
    help="Edit a specific entry by ID",
)
@click.pass_context
def edit(ctx, entry_id: int):
    """Edit or delete entries interactively.

    Opens today's entries in your default text editor for bulk editing,
    or edits a specific entry by ID.

    Examples:
        dwriter edit

        dwriter edit --id 42
    """
    db = Database()

    if entry_id is not None:
        # Edit specific entry
        try:
            entry = db.get_entry(entry_id)
        except ValueError:
            click.echo(click.style("!", fg="red") + f" Entry {entry_id} not found.")
            return

        edited_content = click.edit(entry.content)

        if edited_content is None:
            click.echo("No changes made.")
            return

        edited_content = edited_content.strip()

        if not edited_content:
            if click.confirm("Content is empty. Delete this entry?"):
                db.delete_entry(entry_id)
                click.echo(click.style("✅", fg="green") + " Entry deleted.")
            return

        if edited_content != entry.content:
            db.update_entry(entry_id, content=edited_content)
            click.echo(click.style("✅", fg="green") + " Entry updated.")
        else:
            click.echo("No changes made.")
    else:
        # Bulk edit today's entries
        from datetime import datetime

        today_date = datetime.now()
        entries = db.get_entries_by_date(today_date)

        if not entries:
            click.echo("No entries for today to edit.")
            return

        # Create editable content
        editable_lines = []
        editable_lines.append("# Edit your entries below.")
        editable_lines.append("# Lines starting with '#' will be ignored.")
        editable_lines.append("# Format: [id] content | tag1, tag2 | project")
        editable_lines.append("#" + "-" * 60)

        for entry in entries:
            tags_str = ", ".join(entry.tag_names) if entry.tag_names else ""
            project_str = entry.project or ""
            line = f"[{entry.id}] {entry.content} | {tags_str} | {project_str}"
            editable_lines.append(line)

        edited_text = click.edit("\n".join(editable_lines))

        if edited_text is None:
            click.echo("No changes made.")
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
                    db.delete_entry(entry_id)
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
                db.update_entry(entry_id, content=content, tags=tags, project=project)
                updated_count += 1

            except (ValueError, IndexError):
                click.echo(
                    click.style("!", fg="yellow") + f" Could not parse line: {line}"
                )

        click.echo(
            click.style("✅", fg="green")
            + f" Updated {updated_count} entries, deleted {deleted_count}."
        )
