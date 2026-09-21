import json
from datetime import datetime
from pathlib import Path
from src.organizer import InvoiceOrganizer


def process_csv_batch(csv_path: str, config_path: str = "config/contractors.json"):
    import csv
    
    organizer = InvoiceOrganizer(config_path)
    
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                source = row['source_path']
                person = row['person']
                contractor = row['contractor']
                purchased_from = row['purchased_from']
                date_str = row['invoice_date']
                move = row.get('move', 'true').lower() == 'true'
                
                invoice_date = datetime.strptime(date_str, "%Y-%m-%d")
                
                result = organizer.organize_file(
                    source_path=source,
                    person=person,
                    contractor=contractor,
                    purchased_from=purchased_from,
                    invoice_date=invoice_date,
                    move=move
                )
                print(f"OK: {result}")
            except Exception as e:
                print(f"ERROR: {row.get('source_path', 'unknown')} - {e}")


def process_json_batch(json_path: str, config_path: str = "config/contractors.json"):
    organizer = InvoiceOrganizer(config_path)
    
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    person = data.get('person')
    contractor = data.get('contractor')
    purchased_from = data.get('purchased_from')
    invoice_date = datetime.strptime(data.get('invoice_date'), "%Y-%m-%d")
    move = data.get('move', True)
    files = data.get('files', [])
    
    for file_path in files:
        try:
            result = organizer.organize_file(
                source_path=file_path,
                person=person,
                contractor=contractor,
                purchased_from=purchased_from,
                invoice_date=invoice_date,
                move=move
            )
            print(f"OK: {result}")
        except Exception as e:
            print(f"ERROR: {file_path} - {e}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python batch_process.py <csv_file|json_file>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    if file_path.endswith('.csv'):
        process_csv_batch(file_path)
    elif file_path.endswith('.json'):
        process_json_batch(file_path)
    else:
        print("Unsupported file format. Use .csv or .json")