"""
CLI Interface for Invoice Organizer
"""
import argparse
import sys
from datetime import datetime
from pathlib import Path

from .organizer import InvoiceOrganizer, ConfigValidationError


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="WhatsApp Invoice Organizer - Organize contractor invoices",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m src.cli organize test.jpg --person john_doe --contractor "ABC Construction" --purchased-from "Home Depot" --date 2026-01-15
  python -m src.cli batch examples/batch_example.csv
  python -m src.cli validate
  python -m src.cli list-contractors
  python -m src.cli list-team
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Organize single file
    org_parser = subparsers.add_parser('organize', help='Organize a single invoice file')
    org_parser.add_argument('source', help='Path to source file')
    org_parser.add_argument('--person', required=True, help='Accounts team member')
    org_parser.add_argument('--contractor', required=True, help='Contractor name')
    org_parser.add_argument('--purchased-from', required=True, help='Purchase source')
    org_parser.add_argument('--date', required=True, help='Date (YYYY-MM-DD)')
    
    # Batch process
    batch_parser = subparsers.add_parser('batch', help='Process batch from CSV')
    batch_parser.add_argument('csv_file', help='Path to CSV file')
    
    # Validate config
    subparsers.add_parser('validate', help='Validate configuration')
    
    # List contractors
    subparsers.add_parser('list-contractors', help='List all configured contractors')
    
    # List team
    subparsers.add_parser('list-team', help='List accounts team members')
    
    # Test structure
    subparsers.add_parser('test-structure', help='Test folder structure creation')
    
    return parser


def cmd_organize(args, organizer: InvoiceOrganizer) -> int:
    source = Path(args.source)
    if not source.exists():
        print(f"Error: Source file not found: {source}")
        return 1
    
    try:
        date = datetime.strptime(args.date, "%Y-%m-%d")
    except ValueError:
        print(f"Error: Invalid date format. Use YYYY-MM-DD")
        return 1
    
    success, msg = organizer.organize_file(
        source, args.person, args.contractor, args.purchased_from, date
    )
    
    if success:
        print(f"Success: {msg}")
        return 0
    else:
        print(f"Error: {msg}")
        return 1


def cmd_batch(args, organizer: InvoiceOrganizer) -> int:
    csv_path = Path(args.csv_file)
    if not csv_path.exists():
        print(f"Error: CSV file not found: {csv_path}")
        return 1
    
    print(f"Processing batch: {csv_path}")
    results = organizer.process_batch(csv_path)
    
    print(f"\nResults:")
    print(f"  Processed: {results['processed']}")
    print(f"  Skipped: {results['skipped']}")
    print(f"  Errors: {results['errors']}")
    
    return 0 if results['errors'] == 0 else 1


def cmd_validate(args, organizer: InvoiceOrganizer) -> int:
    print("Configuration is valid!")
    print(f"  Base folder: {organizer.config['base_folder']}")
    print(f"  Contractors: {len(organizer.config['contractors'])}")
    print(f"  Team members: {len(organizer.config['accounts_team'])}")
    print(f"  Supported extensions: {organizer.config['supported_extensions']}")
    return 0


def cmd_list_contractors(args, organizer: InvoiceOrganizer) -> int:
    print("Configured Contractors:")
    for name, details in organizer.config['contractors'].items():
        print(f"  {name} -> {details['short_code']} ({details.get('category', 'N/A')})")
    return 0


def cmd_list_team(args, organizer: InvoiceOrganizer) -> int:
    print("Accounts Team Members:")
    for person in organizer.config['accounts_team']:
        print(f"  {person}")
    return 0


def cmd_test_structure(args, organizer: InvoiceOrganizer) -> int:
    print("Testing folder structure creation...")
    test_dates = [
        datetime(2026, 1, 15),
        datetime(2026, 3, 28),
        datetime(2026, 4, 5),
        datetime(2026, 6, 20),
        datetime(2026, 7, 10),
        datetime(2026, 10, 25),
        datetime(2026, 12, 31),
    ]
    
    for person in organizer.config['accounts_team'][:1]:
        for dt in test_dates:
            folder = organizer.get_target_folder(person, dt)
            print(f"  {person}/{dt.strftime('%Y-%m-%d')} -> {folder.relative_to(organizer.base_folder)}")
    
    print("\nFolder structure test passed!")
    return 0


def main() -> int:
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        organizer = InvoiceOrganizer()
    except ConfigValidationError as e:
        print(f"Config Error: {e}")
        return 1
    except Exception as e:
        print(f"Error initializing organizer: {e}")
        return 1
    
    commands = {
        'organize': cmd_organize,
        'batch': cmd_batch,
        'validate': cmd_validate,
        'list-contractors': cmd_list_contractors,
        'list-team': cmd_list_team,
        'test-structure': cmd_test_structure,
    }
    
    return commands[args.command](args, organizer)


if __name__ == "__main__":
    sys.exit(main())