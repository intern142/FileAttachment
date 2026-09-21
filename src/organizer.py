"""
Core Invoice Organizer Engine
Handles folder structure creation, file renaming, and organization logic
"""
import json
import logging
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from logging.handlers import RotatingFileHandler


class ConfigValidationError(Exception):
    """Raised when configuration validation fails"""
    pass


class InvoiceOrganizer:
    """Main organizer engine"""
    
    def __init__(self, config_path: str = "config/contractors.json"):
        self.config_path = Path(config_path)
        self.config = self._load_and_validate_config()
        self._setup_logging()
        self.logger = logging.getLogger(__name__)
        self.base_folder = Path(self.config["base_folder"])
        self._create_base_structure()
    
    def _load_and_validate_config(self) -> Dict:
        """Load and validate configuration"""
        if not self.config_path.exists():
            raise ConfigValidationError(f"Config file not found: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        self._validate_config(config)
        return config
    
    def _validate_config(self, config: Dict) -> None:
        """Validate required configuration keys"""
        required_keys = ["contractors", "accounts_team", "base_folder"]
        for key in required_keys:
            if key not in config:
                raise ConfigValidationError(f"Missing required config key: {key}")
        
        if not config["contractors"]:
            raise ConfigValidationError("No contractors defined in config")
        
        for name, details in config["contractors"].items():
            if "short_code" not in details:
                raise ConfigValidationError(f"Contractor '{name}' missing short_code")
            if not details["short_code"]:
                raise ConfigValidationError(f"Contractor '{name}' has empty short_code")
        
        if not config["accounts_team"]:
            raise ConfigValidationError("No accounts team members defined")
        
        if "supported_extensions" not in config:
            config["supported_extensions"] = [".jpg", ".jpeg", ".png", ".pdf", ".webp"]
        
        if "filename_format" not in config:
            config["filename_format"] = "{contractor_short}-{purchased_from_short}-{date}{ext}"
        
        if "date_format" not in config:
            config["date_format"] = "%Y-%m-%d"
    
    def _setup_logging(self) -> None:
        """Configure rotating file logging + console"""
        log_config = self.config.get("logging", {})
        log_file = log_config.get("file", "logs/organizer.log")
        log_level = getattr(logging, log_config.get("level", "INFO").upper())
        max_bytes = log_config.get("max_bytes", 1048576)
        backup_count = log_config.get("backup_count", 5)
        
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = RotatingFileHandler(
            log_path, maxBytes=max_bytes, backupCount=backup_count, encoding='utf-8'
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        file_handler.setLevel(log_level)
        
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%H:%M:%S'
        ))
        console_handler.setLevel(log_level)
        
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
    
    def _create_base_structure(self) -> None:
        """Create base folder structure for all team members and quarters"""
        self.base_folder.mkdir(parents=True, exist_ok=True)
        
        for person in self.config["accounts_team"]:
            person_folder = self.base_folder / person
            person_folder.mkdir(exist_ok=True)
            
            for quarter in ["Q1", "Q2", "Q3", "Q4"]:
                quarter_folder = person_folder / quarter
                quarter_folder.mkdir(exist_ok=True)
                
                months = self.config["quarter_months"][quarter]
                for month_num in months:
                    month_name = datetime(2024, month_num, 1).strftime("%B")
                    month_folder = quarter_folder / f"{month_num:02d}_{month_name}"
                    month_folder.mkdir(exist_ok=True)
                    
                    for week in range(1, 6):
                        week_folder = month_folder / f"Week_{week:02d}"
                        week_folder.mkdir(exist_ok=True)
    
    def get_quarter(self, month: int) -> str:
        """Get quarter name for a month"""
        for q, months in self.config["quarter_months"].items():
            if month in months:
                return q
        return "Q1"
    
    def get_week_of_month(self, date: datetime) -> int:
        """Get week number within month (1-5)"""
        first_day = date.replace(day=1)
        day_of_month = date.day
        week_num = ((day_of_month - 1) // 7) + 1
        return min(week_num, 5)
    
    def get_target_folder(self, person: str, date: datetime) -> Path:
        """Get target folder path for a person and date"""
        quarter = self.get_quarter(date.month)
        month_name = date.strftime("%B")
        month_num = date.month
        week = self.get_week_of_month(date)
        
        return self.base_folder / person / quarter / f"{month_num:02d}_{month_name}" / f"Week_{week:02d}"
    
    def get_contractor_short_code(self, contractor_name: str) -> str:
        """Get contractor short code from name"""
        contractor = self.config["contractors"].get(contractor_name)
        if contractor:
            return contractor["short_code"]
        raise ValueError(f"Contractor not found: {contractor_name}")
    
    def get_purchased_from_short(self, purchased_from: str) -> str:
        """Get purchased-from short code"""
        return self.config["purchased_from"].get(purchased_from, purchased_from[:2].upper())
    
    def generate_filename(self, contractor: str, purchased_from: str, 
                          date: datetime, extension: str = None) -> str:
        """Generate organized filename"""
        if extension is None:
            extension = self.config.get("default_extension", ".jpg")
        
        if not extension.startswith('.'):
            extension = '.' + extension
        
        if extension.lower() not in [e.lower() for e in self.config["supported_extensions"]]:
            raise ValueError(f"Unsupported extension: {extension}")
        
        contractor_short = self.get_contractor_short_code(contractor)
        purchased_short = self.get_purchased_from_short(purchased_from)
        date_str = date.strftime(self.config["date_format"].replace("%Y", "%Y").replace("%m", "%m").replace("%d", "%d"))
        date_str = date_str.replace("-", "")
        
        fmt = self.config["filename_format"]
        return fmt.format(
            contractor_short=contractor_short,
            purchased_from_short=purchased_short,
            date=date_str,
            ext=extension
        )
    
    def organize_file(self, source_path: Path, person: str, contractor: str,
                      purchased_from: str, date: datetime) -> Tuple[bool, str]:
        """
        Organize a single file
        Returns: (success, message)
        """
        try:
            if not source_path.exists():
                return False, f"Source file not found: {source_path}"
            
            if person not in self.config["accounts_team"]:
                return False, f"Person not in accounts team: {person}"
            
            if contractor not in self.config["contractors"]:
                return False, f"Contractor not configured: {contractor}"
            
            extension = source_path.suffix.lower()
            if extension not in [e.lower() for e in self.config["supported_extensions"]]:
                return False, f"Unsupported file type: {extension}"
            
            new_filename = self.generate_filename(contractor, purchased_from, date, extension)
            target_folder = self.get_target_folder(person, date)
            target_folder.mkdir(parents=True, exist_ok=True)
            target_path = target_folder / new_filename
            
            counter = 1
            original_target = target_path
            while target_path.exists():
                stem = original_target.stem
                suffix = original_target.suffix
                target_path = target_folder / f"{stem}_{counter}{suffix}"
                counter += 1
            
            shutil.move(str(source_path), str(target_path))
            
            rel_path = target_path.relative_to(self.base_folder)
            self.logger.info(f"Organized: {source_path.name} -> {rel_path}")
            
            return True, f"Moved to {rel_path}"
            
        except Exception as e:
            self.logger.error(f"Error organizing {source_path}: {e}")
            return False, f"Error: {str(e)}"
    
    def process_batch(self, csv_path: Path) -> Dict[str, int]:
        """Process batch from CSV file"""
        import csv
        
        results = {"processed": 0, "skipped": 0, "errors": 0}
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                source = Path(row["source_path"])
                person = row["person"]
                contractor = row["contractor"]
                purchased_from = row["purchased_from"]
                date_str = row["date"]
                
                try:
                    date = datetime.strptime(date_str, "%Y-%m-%d")
                except ValueError:
                    self.logger.error(f"Invalid date format in CSV: {date_str}")
                    results["errors"] += 1
                    continue
                
                success, msg = self.organize_file(source, person, contractor, purchased_from, date)
                if success:
                    results["processed"] += 1
                else:
                    results["errors"] += 1
                    self.logger.warning(f"Batch skipped {source.name}: {msg}")
        
        return results


def main():
    """Test entry point"""
    try:
        organizer = InvoiceOrganizer()
        print("Folder structure created successfully!")
        print(f"Base folder: {organizer.base_folder.absolute()}")
        print(f"Contractors: {len(organizer.config['contractors'])}")
        print(f"Team members: {len(organizer.config['accounts_team'])}")
        return 0
    except ConfigValidationError as e:
        print(f"Config Error: {e}")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())