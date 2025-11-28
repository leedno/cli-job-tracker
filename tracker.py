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
    delete_jobs_by_ids,
    delete_all_jobs,
)
import subprocess
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Confirm

# Initialize database on import
initialize_db()

# Define the root directory for your cover letters
# It will be a 'cover_letters' folder right next to your tracker.py file.
CL_DIR = Path(__file__).parent / "cover_letters"
# Ensure the directory exists
CL_DIR.mkdir(exist_ok=True)

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

    latest_job = get_jobs()[0]
    latest_job_id = latest_job["id"]

    # Ask user if they want to create/edit the letter now
    if Confirm.ask(
        f"Do you want to create/edit the cover letter file for ID #{latest_job_id} now?",
        default=True,
    ):
        handle_open_letter(latest_job_id)


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
    # NEW COLUMN for Cover Letter status
    table.add_column("CL", style="bold green", justify="center")
    table.add_column("Notes", style="dim white")

    for job in jobs:
        # job is now a sqlite3.Row object, access by index or name
        status = job["status"]
        status_colored = f"[{get_status_color(status)}]{status}[/]"

        # --- NEW COVER LETTER CHECK ---
        # Replicate the filename construction logic from handle_open_letter
        safe_company = job["company"].replace(" ", "_").replace("/", "-")
        safe_title = job["title"].replace(" ", "_").replace("/", "-")
        filename = f"{job['id']}_{safe_company}_{safe_title}.md"
        file_path = CL_DIR / filename

        # Check if the file exists on the filesystem
        cl_display = (
            "[bold green]✓[/bold green]"
            if file_path.exists()
            else "[dim red]—[/dim red]"
        )
        # --- END NEW CHECK ---

        table.add_row(
            str(job["id"]),
            job["company"],
            job["title"],
            job["source"],
            status_colored,
            job["date_applied"],
            cl_display,  # ADDED to the table row
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


def handle_delete(args):
    """Handles the 'delete' command for one, multiple, or all jobs."""

    if args.all:
        # Handle DELETE ALL logic (jt delete --all)
        console.print(
            "\n[bold red]WARNING:[/bold red] You are about to delete ALL job applications."
        )
        if Confirm.ask(
            "Are you absolutely sure you want to delete everything?", default=False
        ):
            deleted_count = delete_all_jobs()
            console.print(
                f"\n[bold red]Success![/bold red] {deleted_count} total job(s) deleted."
            )
        else:
            console.print("\n[bold yellow]Operation cancelled.[/bold yellow]")
        return

    # Handle DELETE BY IDs logic (jt delete 1 2 3)
    job_ids = args.ids

    if not job_ids:
        # This occurs if the user runs 'jt delete' with no IDs and no --all flag
        console.print(
            "[bold red]Error:[/bold red] Please provide one or more Job IDs, or use --all."
        )
        return

    console.print(
        "\n[bold red]WARNING:[/bold red] You are about to delete the following job(s):"
    )
    jobs_to_delete = []

    # Preview and gather valid jobs
    for job_id in job_ids:
        job = get_job_by_id(job_id)
        if job:
            console.print(
                f"  - [bold]{job_id}[/bold]: {job['company']} - {job['title']}"
            )
            jobs_to_delete.append(job_id)
        else:
            console.print(f"  - [bold red]Error:[/bold red] Job #{job_id} not found.")

    if not jobs_to_delete:
        console.print(
            "[bold yellow]No valid jobs to delete. Operation cancelled.[/bold yellow]\n"
        )
        return

    if Confirm.ask("\nAre you sure you want to delete all listed jobs?", default=False):
        deleted_count = delete_jobs_by_ids(jobs_to_delete)
        console.print(
            f"\n[bold red]Success![/bold red] {deleted_count} job(s) deleted."
        )
    else:
        console.print("\n[bold yellow]Operation cancelled.[/bold yellow]")


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


def handle_open_letter(job_id: int):
    """Opens or creates the cover letter file for a job using nvim."""
    job = get_job_by_id(job_id)
    if not job:
        console.print(f"[bold red]Error:[/bold red] Job #{job_id} not found.")
        return

    # Standardized file name: ID_Company_Title.md
    # Clean company/title names for filenames (replace spaces, slashes, etc.)
    safe_company = job["company"].replace(" ", "_").replace("/", "-")
    safe_title = job["title"].replace(" ", "_").replace("/", "-")

    filename = f"{job_id}_{safe_company}_{safe_title}.md"
    file_path = CL_DIR / filename

    console.print(
        f"[bold yellow]Opening letter for:[/bold yellow] [cyan]{job['company']} - {job['title']}[/cyan]..."
    )
    console.print(f"[dim]File:[/dim] {file_path}")

    try:
        # Use subprocess to call nvim (or 'vi', 'nano', whatever text editor you prefer)
        # We use 'nvim' as requested by the user.
        subprocess.run(["nvim", str(file_path)], check=True)

    except FileNotFoundError:
        console.print(
            f"\n[bold red]Error:[/bold red] 'nvim' command not found. Please ensure it is installed and in your PATH."
        )
    except Exception as e:
        console.print(f"\n[bold red]An unexpected error occurred:[/bold red] {e}")


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
    delete_parser = subparsers.add_parser(
        "delete", help="Delete jobs by ID, or delete all jobs with --all."
    )
    # nargs='*' allows 0 or more IDs (used for deleting multiple)
    delete_parser.add_argument(
        "ids", type=int, nargs="*", help="One or more Job IDs to delete (e.g., 5 6 7)"
    )
    # The --all flag
    delete_parser.add_argument(
        "--all", action="store_true", help="Delete ALL job entries."
    )

    # EDIT
    edit_parser = subparsers.add_parser("edit", help="Edit job details")
    edit_parser.add_argument("id", type=int, help="Job ID")

    # STATS
    subparsers.add_parser("stats", help="Show application statistics")

    # VIEW-LETTER
    view_letter_parser = subparsers.add_parser(
        "letter", help="Open the cover letter file with nvim"
    )
    view_letter_parser.add_argument("id", type=int, help="Job ID")

    args = parser.parse_args()

    if args.command == "add":
        handle_add()
    elif args.command == "list":
        handle_list()
    elif args.command == "update":
        handle_update(args.id, args.status)
    elif args.command == "delete":
        handle_delete(args)
    elif args.command == "edit":
        handle_edit(args.id)
    elif args.command == "stats":
        handle_stats()
    elif args.command == "letter":
        handle_open_letter(args.id)


if __name__ == "__main__":
    main()
