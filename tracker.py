import argparse
from datetime import date
from database import (
    initialize_db,
    add_job,
    get_jobs,
    update_job_status,
    delete_job,
    get_job_by_id,
    update_job_details,
    get_job_counts,
)

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Confirm

# Initialize database on import
initialize_db()

console = Console()


def get_status_color(status: str) -> str:
    """Helper function to assign Rich colors based on status."""
    status_map = {
        "Applied": "cyan",
        "Interview": "bold yellow",
        "Offer": "bold green",
        "Rejected": "dim red",
    }
    return status_map.get(status, "white")


def handle_add():
    """Handles the 'add' command."""
    print("\n--- Add New Job Application ---")

    company = input("Company Name: ").strip()
    title = input("Job Title: ").strip()
    source = input("Source (e.g., LinkedIn): ").strip()
    notes = input("Notes (optional): ").strip()
    date_applied = date.today().isoformat()

    if not company or not title:
        console.print(
            "[bold red]Error: Company Name and Job Title are required.[/bold red]"
        )
        return

    add_job(company, title, source, notes, date_applied)
    console.print(
        f"\n[bold green]Success![/bold green] Added application for [bold]{company}[/bold]."
    )


def handle_list():
    """Handles the 'list' command."""
    jobs = get_jobs()

    if not jobs:
        console.print("[bold red]No job applications tracked yet![/bold red]")
        return

    table = Table(title="[bold magenta]Job Application Tracker[/bold magenta]")

    table.add_column("ID", style="bold", justify="center")
    table.add_column("Company", style="cyan", justify="left")
    table.add_column("Title", style="white", justify="left")
    table.add_column("Source", style="blue")
    table.add_column("Status", style="bold", justify="center")
    table.add_column("Date", style="dim")
    table.add_column("Notes", style="dim white")

    for job in jobs:
        # job is now a sqlite3.Row object, access by index or name
        status = job["status"]
        status_colored = f"[{get_status_color(status)}]{status}[/]"

        table.add_row(
            str(job["id"]),
            job["company"],
            job["title"],
            job["source"],
            status_colored,
            job["date_applied"],
            job["notes"],
        )

    console.print(table)


def handle_update(job_id: int, new_status: str):
    """Handles the 'update' command (Status only)."""
    valid_statuses = ["Applied", "Interview", "Offer", "Rejected"]

    if new_status not in valid_statuses:
        console.print(
            f"[bold red]Error:[/bold red] Invalid status. Use: {', '.join(valid_statuses)}"
        )
        return

    if update_job_status(job_id, new_status):
        console.print(
            f"[bold green]Success:[/bold green] Job #{job_id} updated to [{get_status_color(new_status)}]{new_status}[/]."
        )
    else:
        console.print(f"[bold red]Error:[/bold red] Job #{job_id} not found.")


def handle_delete(job_id: int):
    """Handles the 'delete' command."""
    job = get_job_by_id(job_id)
    if not job:
        console.print(f"[bold red]Error:[/bold red] Job #{job_id} not found.")
        return

    console.print(f"Deleting: [bold]{job['company']} - {job['title']}[/bold]")
    if Confirm.ask("Are you sure?", default=False):
        delete_job(job_id)
        console.print(f"[bold red]Deleted[/bold red] Job #{job_id}.")
    else:
        console.print("[bold yellow]Operation cancelled.[/bold yellow]")


def handle_edit(job_id: int):
    """Handles the 'edit' command for full details."""
    job = get_job_by_id(job_id)
    if not job:
        console.print(f"[bold red]Error:[/bold red] Job #{job_id} not found.")
        return

    console.print(f"\n[bold magenta]Editing Job #{job_id}[/bold magenta]")
    console.print("[dim]Press Enter to keep current value[/dim]\n")

    new_company = (
        console.input(f"Company [[cyan]{job['company']}[/cyan]]: ").strip()
        or job["company"]
    )
    new_title = (
        console.input(f"Title [[cyan]{job['title']}[/cyan]]: ").strip() or job["title"]
    )
    new_source = (
        console.input(f"Source [[cyan]{job['source']}[/cyan]]: ").strip()
        or job["source"]
    )

    console.print(
        f"Current Status: [{get_status_color(job['status'])}]{job['status']}[/]"
    )
    new_status = console.input(
        f"New Status (Applied, Interview, Offer, Rejected): "
    ).strip()
    if not new_status:
        new_status = job["status"]

    new_notes = (
        console.input(f"Notes [[cyan]{job['notes']}[/cyan]]: ").strip() or job["notes"]
    )

    update_job_details(
        job_id, new_company, new_title, new_source, new_status, new_notes
    )
    console.print(f"\n[bold green]Success![/bold green] Job details updated.")


def handle_stats():
    """Display simple statistics."""
    counts = get_job_counts()
    total = sum(count for _, count in counts)

    if total == 0:
        console.print("[yellow]No data to analyze.[/yellow]")
        return

    print()
    console.print(
        Panel(f"[bold]Total Applications:[/bold] [cyan]{total}[/cyan]", expand=False)
    )

    for status, count in counts:
        percentage = (count / total) * 100
        bar = "█" * int(percentage / 5)
        color = get_status_color(status)
        console.print(
            f"[{color}]{status:<10}[/] | {count:>2} | {bar} [dim]({percentage:.1f}%)[/dim]"
        )
    print()


def main():
    parser = argparse.ArgumentParser(description="CLI Job Application Tracker")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # ADD
    subparsers.add_parser("add", help="Add a new job application")

    # LIST
    subparsers.add_parser("list", help="List all applications")

    # UPDATE
    update_parser = subparsers.add_parser("update", help="Quickly update status")
    update_parser.add_argument("id", type=int, help="Job ID")
    update_parser.add_argument("status", type=str, help="New status")

    # DELETE
    delete_parser = subparsers.add_parser("delete", help="Delete an application")
    delete_parser.add_argument("id", type=int, help="Job ID")

    # EDIT
    edit_parser = subparsers.add_parser("edit", help="Edit job details")
    edit_parser.add_argument("id", type=int, help="Job ID")

    # STATS
    subparsers.add_parser("stats", help="Show application statistics")

    args = parser.parse_args()

    if args.command == "add":
        handle_add()
    elif args.command == "list":
        handle_list()
    elif args.command == "update":
        handle_update(args.id, args.status)
    elif args.command == "delete":
        handle_delete(args.id)
    elif args.command == "edit":
        handle_edit(args.id)
    elif args.command == "stats":
        handle_stats()


if __name__ == "__main__":
    main()
