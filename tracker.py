import argparse
from datetime import date
from database import initialize_db, add_job

# Initialize the database file when the script starts
initialize_db()


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


def main():
    parser = argparse.ArgumentParser(description="Minimal CLI Job Application Tracker.")

    # Setup subcommands for 'add', 'list', etc.
    subparsers = parser.add_subparsers(dest="command", required=True)

    # 'add' command setup
    add_parser = subparsers.add_parser("add", help="Add a new job application.")

    # 'list' command setup (You will implement this next)
    list_parser = subparsers.add_parser("list", help="List all job applications.")

    # Parse the arguments
    args = parser.parse_args()

    # Execute the corresponding function
    if args.command == "add":
        handle_add()
    elif args.command == "list":
        # Placeholder for the next step
        print("Listing function coming soon...")
        pass


if __name__ == "__main__":
    main()
