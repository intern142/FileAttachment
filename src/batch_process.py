"""
Batch Processing Module for Invoice Organizer
Processes multiple invoices from CSV file
"""
import csv
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from .organizer import InvoiceOrganizer, ConfigValidationError


class BatchProcessor:
    """Process batch invoices from CSV"""
    
    REQUIRED_COLUMNS = ["source_path", "person", "contractor", "purchased_from", "date"]
    DATE_FORMAT = "%Y-%m-%d"
    
    def __init__(self, config_path: str = "config/contractors.json"):
        self.organizer = InvoiceOrganizer(config_path)
        self.logger = self.organizer.logger
    
    def validate_csv(self, csv_path: Path) -> tuple[bool, List[str]]:
        """Validate CSV structure and content"""
        errors = []
        
        if not csv_path.exists():
            errors.append(f"CSV file not found: {csv_path}")
            return False, errors
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # Check columns
            if reader.fieldnames is None:
                errors.append("CSV file is empty or has no headers")
                return False, errors
            
            missing_cols = set(self.REQUIRED_COLUMNS) - set(reader.fieldnames)
            if missing_cols:
                errors.append(f"Missing required columns: {missing_cols}")
            
            # Check rows
            for i, row in enumerate(reader, start=2):
                for col in self.REQUIRED_COLUMNS:
                    if not row.get(col, '').strip():
                        errors.append(f"Row {i}: Missing value for '{col}'")
                
                # Validate date format
                date_str = row.get('date', '').strip()
                if date_str:
                    try:
                        datetime.strptime(date_str, self.DATE_FORMAT)
                    except ValueError:
                        errors.append(f"Row {i}: Invalid date format '{date_str}' (expected YYYY-MM-DD)")
                
                # Validate source file exists
                source = row.get('source_path', '').strip()
                if source and not Path(source).exists():
                    errors.append(f"Row {i}: Source file not found: {source}")
        
        return len(errors) == 0, errors
    
    def create_sample_csv(self, output_path: Path) -> None:
        """Create a sample CSV template"""
        sample_data = [
            {
                "source_path": "invoices/receipt1.jpg",
                "person": "john_doe",
                "contractor": "ABC Construction",
                "purchased_from": "Home Depot",
                "date": "2026-01-15"
            },
            {
                "source_path": "invoices/receipt2.pdf",
                "person": "jane_smith",
                "contractor": "XYZ Builders",
                "purchased_from": "Lowe's",
                "date": "2026-02-20"
            },
            {
                "source_path": "invoices/receipt3.png",
                "person": "mike_wilson",
                "contractor": "PQR Contractors",
                "purchased_from": "Local Supplier",
                "date": "2026-03-10"
            }
        ]
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.REQUIRED_COLUMNS)
            writer.writeheader()
            writer.writerows(sample_data)
        
        print(f"Sample CSV created: {output_path}")
    
    def process(self, csv_path: Path) -> Dict[str, int]:
        """Process batch CSV"""
        results = {"processed": 0, "skipped": 0, "errors": 0}
        
        is_valid, errors = self.validate_csv(csv_path)
        if not is_valid:
            for err in errors:
                self.logger.error(f"CSV Validation: {err}")
            results["errors"] = len(errors)
            return results
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                source = Path(row["source_path"])
                person = row["person"]
                contractor = row["contractor"]
                purchased_from = row["purchased_from"]
                date_str = row["date"]
                
                try:
                    date = datetime.strptime(date_str, self.DATE_FORMAT)
                except ValueError:
                    self.logger.error(f"Invalid date: {date_str}")
                    results["errors"] += 1
                    continue
                
                success, msg = self.organizer.organize_file(
                    source, person, contractor, purchased_from, date
                )
                
                if success:
                    results["processed"] += 1
                    self.logger.info(f"Batch: {source.name} -> {msg}")
                else:
                    results["errors"] += 1
                    self.logger.warning(f"Batch failed {source.name}: {msg}")
        
        return results


def main():
    """CLI entry point for batch processing"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Batch process invoices from CSV")
    parser.add_argument('csv_file', nargs='?', help='Path to CSV file')
    parser.add_argument('--create-sample', metavar='PATH', help='Create sample CSV template')
    parser.add_argument('--validate-only', action='store_true', help='Only validate CSV, do not process')
    
    args = parser.parse_args()
    
    try:
        processor = BatchProcessor()
    except ConfigValidationError as e:
        print(f"Config Error: {e}")
        return 1
    
    if args.create_sample:
        processor.create_sample_csv(Path(args.create_sample))
        return 0
    
    if not args.csv_file:
        parser.print_help()
        return 1
    
    csv_path = Path(args.csv_file)
    
    if args.validate_only:
        is_valid, errors = processor.validate_csv(csv_path)
        if is_valid:
            print("CSV validation passed!")
            return 0
        else:
            print("CSV validation failed:")
            for err in errors:
                print(f"  - {err}")
            return 1
    
    print(f"Processing batch: {csv_path}")
    results = processor.process(csv_path)
    
    print(f"\nResults:")
    print(f"  Processed: {results['processed']}")
    print(f"  Skipped: {results['skipped']}")
    print(f"  Errors: {results['errors']}")
    
    return 0 if results['errors'] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())