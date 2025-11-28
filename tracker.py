import argparse
from datetime import date
from database import initialize_db, add_job, get_jobs, update_job_status

from rich.console import Console
from rich.table import Table

# Initialize the database file when the script starts
initialize_db()

console = Console()


def handle_add():
    """Handles the 'add' command and prompts for user input."""
    print("\n--- Add New Job Application ---")

    # Simple form-like input
    company = input("Company Name: ").strip()
    title = input("Job Title: ").strip()
    source = input("Source (e.g., LinkedIn, StudentJob): ").strip()
    notes = input("Notes (optional): ").strip()

    # Automatically get the current date
    date_applied = date.today().isoformat()

    if not company or not title:
        print("Error: Company Name and Job Title are required.")
        return

    # Call the database function
    add_job(company, title, source, notes, date_applied)
    print(
        f"\nSuccessfully logged application for {company} ({title}). Status: Applied."
    )


def get_status_color(status: str) -> str:
    """Helper function to assign Rich colors based on status."""
    status_map = {
        "Applied": "cyan",
        "Interview": "bold yellow",
        "Offer": "bold green",
        "Rejected": "dim red",
    }
    return status_map.get(status, "white")


def handle_list():
    """Handles the 'list' command, displaying all jobs in a Rich table."""
    jobs = get_jobs()

    if not jobs:
        console.print("[bold red]No job applications tracked yet![/bold red]")
        return

    table = Table(title="[bold magenta]Job Application Tracker[/bold magenta]")

    # Define table columns
    table.add_column("ID", style="bold", justify="center")
    table.add_column("Company", style="white", justify="left")
    table.add_column("Title", style="white", justify="left")
    table.add_column("Source", style="blue")
    table.add_column("Date", style="dim")
    table.add_column("Status", style="bold", justify="center")

    for job in jobs:
        # Unpack the tuple returned from SQLite
        job_id, company, title, source, status, date_applied = job

        # Color the status using the helper function
        status_colored = f"[{get_status_color(status)}]{status}[/]"

        table.add_row(
            str(job_id),
            company,
            title,
            source,
            date_applied,
            status_colored,
        )

    console.print(table)


def handle_update(job_id: int, new_status: str):
    """Handles the 'update' command."""

    # Simple validation for common status strings
    valid_statuses = ["Applied", "Interview", "Offer", "Rejected"]

    if new_status not in valid_statuses:
        console.print(
            f"[bold red]Error:[/bold red] Invalid status '{new_status}'. Use: {', '.join(valid_statuses)}"
        )
        return

    if update_job_status(job_id, new_status):
        console.print(
            f"[bold green]Success:[/bold green] Job [yellow]#{job_id}[/yellow] status updated to [bold {get_status_color(new_status)}]{new_status}[/]."
        )
    else:
        console.print(
            f"[bold red]Error:[/bold red] Job with ID [yellow]#{job_id}[/yellow] not found."
        )


def main():
    parser = argparse.ArgumentParser(description="Minimal CLI Job Application Tracker.")

    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="Add a new job application.")

    list_parser = subparsers.add_parser("list", help="List all job applications.")

    # Update command setup
    update_parser = subparsers.add_parser(
        "update", help="Update the status of a job (e.g., update 5 Interview)."
    )
    update_parser.add_argument("id", type=int, help="ID of the job to update.")
    update_parser.add_argument(
        "status", type=str, help="New status (Applied, Interview, Offer, Rejected)."
    )

    args = parser.parse_args()

    if args.command == "add":
        handle_add()
    elif args.command == "list":
        handle_list()
    elif args.command == "update":
        handle_update(args.id, args.status)  # Pass arguments to the handler


if __name__ == "__main__":
    main()
