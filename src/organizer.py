import os
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InvoiceOrganizer:
    def __init__(self, config_path: str = "config/contractors.json"):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.base_folder = Path(self.config.get("base_folder", "Invoices"))
        self.contractors = self.config.get("contractors", {})
        self.accounts_team = self.config.get("accounts_team", [])
        self.filename_format = self.config.get("filename_format", "{contractor_short}-{purchased_from}-{date}.jpg")
    
    def get_contractor_short(self, contractor_name: str) -> str:
        return self.contractors.get(contractor_name, contractor_name[:3].upper())
    
    def get_quarter(self, month: int) -> str:
        if 1 <= month <= 3:
            return "Q1_Jan-Mar"
        elif 4 <= month <= 6:
            return "Q2_Apr-Jun"
        elif 7 <= month <= 9:
            return "Q3_Jul-Sep"
        else:
            return "Q4_Oct-Dec"
    
    def get_week_of_month(self, date: datetime) -> str:
        first_day = date.replace(day=1)
        dom = date.day
        adjusted_dom = dom + first_day.weekday()
        week_num = (adjusted_dom - 1) // 7 + 1
        return f"Week_{week_num}"
    
    def get_target_folder(self, person: str, date: datetime) -> Path:
        quarter = self.get_quarter(date.month)
        month_name = date.strftime("%B")
        week = self.get_week_of_month(date)
        
        return self.base_folder / person / quarter / month_name / week
    
    def generate_filename(self, contractor: str, purchased_from: str, date: datetime) -> str:
        contractor_short = self.get_contractor_short(contractor)
        purchased_short = purchased_from[:3].upper()
        date_str = date.strftime("%Y-%m-%d")
        
        return self.filename_format.format(
            contractor_short=contractor_short,
            purchased_from=purchased_short,
            date=date_str
        )
    
    def organize_file(
        self,
        source_path: str,
        person: str,
        contractor: str,
        purchased_from: str,
        invoice_date: datetime,
        move: bool = True
    ) -> Path:
        target_folder = self.get_target_folder(person, invoice_date)
        target_folder.mkdir(parents=True, exist_ok=True)
        
        filename = self.generate_filename(contractor, purchased_from, invoice_date)
        target_path = target_folder / filename
        
        if target_path.exists():
            base, ext = os.path.splitext(filename)
            counter = 1
            while target_path.exists():
                target_path = target_folder / f"{base}_{counter}{ext}"
                counter += 1
        
        if move:
            shutil.move(source_path, target_path)
            logger.info(f"Moved: {source_path} -> {target_path}")
        else:
            shutil.copy2(source_path, target_path)
            logger.info(f"Copied: {source_path} -> {target_path}")
        
        return target_path
    
    def process_batch(
        self,
        files: List[Dict],
        person: str,
        move: bool = True
    ) -> List[Path]:
        results = []
        for file_info in files:
            try:
                result = self.organize_file(
                    source_path=file_info["source_path"],
                    person=person,
                    contractor=file_info["contractor"],
                    purchased_from=file_info["purchased_from"],
                    invoice_date=file_info["invoice_date"],
                    move=move
                )
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to process {file_info.get('source_path')}: {e}")
        return results
    
    def create_folder_structure(self, person: str, year: int = None) -> None:
        if year is None:
            year = datetime.now().year
        
        for quarter_num in range(1, 5):
            quarter_name = f"Q{quarter_num}_"
            if quarter_num == 1:
                quarter_name += "Jan-Mar"
                months = ["January", "February", "March"]
            elif quarter_num == 2:
                quarter_name += "Apr-Jun"
                months = ["April", "May", "June"]
            elif quarter_num == 3:
                quarter_name += "Jul-Sep"
                months = ["July", "August", "September"]
            else:
                quarter_name += "Oct-Dec"
                months = ["October", "November", "December"]
            
            for month in months:
                for week in range(1, 6):
                    folder = self.base_folder / person / quarter_name / month / f"Week_{week}"
                    folder.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Created folder structure for {person} in {self.base_folder}")


def main():
    organizer = InvoiceOrganizer()
    
    for person in organizer.accounts_team:
        organizer.create_folder_structure(person)
    
    print("Folder structure created successfully!")


if __name__ == "__main__":
    main()