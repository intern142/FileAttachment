import argparse
import json
from datetime import datetime
from pathlib import Path
from src.organizer import InvoiceOrganizer


def parse_date(date_str: str) -> datetime:
    formats = ["%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d"]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    raise ValueError(f"Invalid date format: {date_str}. Use YYYY-MM-DD")


def main():
    parser = argparse.ArgumentParser(description="Invoice Organizer - Rename and organize invoice receipts")
    parser.add_argument("source", help="Path to the invoice file or folder")
    parser.add_argument("--person", required=True, help="Accounts team member name")
    parser.add_argument("--contractor", required=True, help="Contractor name")
    parser.add_argument("--purchased-from", required=True, dest="purchased_from", help="Purchased from (store/vendor)")
    parser.add_argument("--date", required=True, help="Invoice date (YYYY-MM-DD)")
    parser.add_argument("--copy", action="store_true", help="Copy instead of move")
    parser.add_argument("--config", default="config/contractors.json", help="Config file path")
    
    args = parser.parse_args()
    
    organizer = InvoiceOrganizer(args.config)
    
    invoice_date = parse_date(args.date)
    source_path = Path(args.source)
    
    if not source_path.exists():
        print(f"Error: Source path does not exist: {source_path}")
        return 1
    
    if source_path.is_file():
        result = organizer.organize_file(
            source_path=str(source_path),
            person=args.person,
            contractor=args.contractor,
            purchased_from=args.purchased_from,
            invoice_date=invoice_date,
            move=not args.copy
        )
        print(f"Organized: {result}")
    elif source_path.is_dir():
        files = list(source_path.glob("*.jpg")) + list(source_path.glob("*.jpeg")) + list(source_path.glob("*.png"))
        print(f"Found {len(files)} image files to process")
        
        for file_path in files:
            try:
                result = organizer.organize_file(
                    source_path=str(file_path),
                    person=args.person,
                    contractor=args.contractor,
                    purchased_from=args.purchased_from,
                    invoice_date=invoice_date,
                    move=not args.copy
                )
                print(f"  Organized: {result}")
            except Exception as e:
                print(f"  Failed: {file_path} - {e}")
    
    return 0


if __name__ == "__main__":
    exit(main())