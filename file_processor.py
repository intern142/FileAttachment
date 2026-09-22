"""
File Processor
Handles renaming and organizing invoice files
"""
import os
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
import logging

from folder_structure import FolderStructureManager, get_folder_structure_manager


class FileProcessor:
    """Processes invoice files: rename and move to organized structure"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize folder structure manager
        self.folder_manager = get_folder_structure_manager(config['destination_root'])
        
        # Contractor mappings
        self.contractor_mappings = config.get('contractor_mappings', {})
        self.default_contractor = config.get('default_contractor_code', 'UNK')
        
        # Purchase source mappings
        self.source_mappings = config.get('purchase_source_mappings', {})
        self.default_source = config.get('default_purchase_source', 'GEN')
        
        # Valid extensions
        self.valid_extensions = {ext.lower() for ext in config.get('valid_extensions', ['.jpg', '.jpeg', '.png', '.pdf'])}
        
        # Track processed files to avoid duplicates
        self.processed_files = set()
        self._load_processed_log()
    
    def _load_processed_log(self):
        """Load list of already processed files"""
        log_file = Path(self.config['destination_root']) / '.processed_files.log'
        if log_file.exists():
            try:
                with open(log_file, 'r') as f:
                    self.processed_files = {line.strip() for line in f if line.strip()}
            except Exception as e:
                self.logger.warning(f"Could not load processed files log: {e}")
    
    def _save_processed_log(self, file_hash: str):
        """Save processed file hash to log"""
        log_file = Path(self.config['destination_root']) / '.processed_files.log'
        try:
            with open(log_file, 'a') as f:
                f.write(f"{file_hash}\n")
            self.processed_files.add(file_hash)
        except Exception as e:
            self.logger.warning(f"Could not save processed files log: {e}")
    
    def _get_file_hash(self, file_path: Path) -> str:
        """Generate a simple hash for duplicate detection"""
        import hashlib
        stat = file_path.stat()
        # Use filename + size + mtime for quick hash
        content = f"{file_path.name}_{stat.st_size}_{stat.st_mtime}"
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def extract_contractor_code(self, filename: str, contact_name: str = "") -> str:
        """Extract contractor code from filename or contact name"""
        # Try contact name first (from WhatsApp)
        if contact_name and contact_name in self.contractor_mappings:
            return self.contractor_mappings[contact_name]
        
        # Normalize filename for matching (replace separators with space)
        normalized_filename = re.sub(r'[\s_\-]+', ' ', filename).strip().lower()
        
        # Try to find contractor name in filename (normalize both)
        for name, code in self.contractor_mappings.items():
            normalized_name = re.sub(r'[\s_\-]+', ' ', name).strip().lower()
            if normalized_name in normalized_filename:
                return code
        
        # Try common patterns in filename (e.g., "ABC_", "ABC-", "ABC ")
        for name, code in self.contractor_mappings.items():
            # Match first word of contractor name + separator
            first_word = name.split()[0]
            pattern = re.escape(first_word) + r'[\s_\-]'
            if re.search(pattern, filename, re.IGNORECASE):
                return code
        
        return self.default_contractor
    
    def extract_purchase_source(self, filename: str) -> str:
        """Extract purchase source from filename"""
        filename_lower = filename.lower()
        for keyword, code in self.source_mappings.items():
            if keyword.lower() in filename_lower:
                return code
        return self.default_source
    
    def extract_date_from_filename(self, filename: str) -> Optional[datetime]:
        """Try to extract date from filename"""
        # Common date patterns in WhatsApp filenames
        patterns = [
            r'(\d{4})[-_]?(\d{2})[-_]?(\d{2})',  # YYYY-MM-DD or YYYYMMDD
            r'(\d{2})[-_]?(\d{2})[-_]?(\d{4})',  # DD-MM-YYYY or DDMMYYYY
            r'(\d{2})[-_]?(\d{2})[-_]?(\d{2})',  # DD-MM-YY or DDMMYY
            r'IMG[-_]?(\d{4})(\d{2})(\d{2})',    # IMG-YYYYMMDD
            r'VID[-_]?(\d{4})(\d{2})(\d{2})',    # VID-YYYYMMDD
            r'WhatsApp[-_]?Image[-_]?(\d{4})[-_]?(\d{2})[-_]?(\d{2})',  # WhatsApp Image YYYY-MM-DD
        ]
        
        for pattern in patterns:
            match = re.search(pattern, filename)
            if match:
                groups = match.groups()
                try:
                    if len(groups) == 3:
                        # Determine format based on values
                        if 1900 <= int(groups[0]) <= 2100:  # YYYY first
                            year, month, day = int(groups[0]), int(groups[1]), int(groups[2])
                        elif 1900 <= int(groups[2]) <= 2100:  # YYYY last
                            day, month, year = int(groups[0]), int(groups[1]), int(groups[2])
                        else:  # Assume YY
                            year = 2000 + int(groups[2])
                            month, day = int(groups[0]), int(groups[1])
                        
                        # Validate date
                        if 1 <= month <= 12 and 1 <= day <= 31:
                            return datetime(year, month, day)
                except (ValueError, IndexError):
                    continue
        
        return None
    
    def get_file_date(self, file_path: Path) -> datetime:
        """Get the best date for the file: from filename, then file metadata"""
        # Try filename first
        date = self.extract_date_from_filename(file_path.name)
        if date:
            return date
        
        # Fall back to file modification time
        mtime = file_path.stat().st_mtime
        return datetime.fromtimestamp(mtime)
    
    def generate_new_filename(self, file_path: Path, contact_name: str = "") -> str:
        """Generate new filename: contractor_source_YYYYMMDD.ext"""
        contractor_code = self.extract_contractor_code(file_path.name, contact_name)
        source_code = self.extract_purchase_source(file_path.name)
        file_date = self.get_file_date(file_path)
        date_str = file_date.strftime("%Y%m%d")
        extension = file_path.suffix.lower()
        
        new_name = f"{contractor_code}-{source_code}-{date_str}{extension}"
        return new_name
    
    def process_file(self, file_path: Path, contact_name: str = "") -> Tuple[bool, str]:
        """
        Process a single file: rename and move to organized folder
        Returns: (success, message)
        """
        try:
            # Check if valid extension
            if file_path.suffix.lower() not in self.valid_extensions:
                return False, f"Invalid extension: {file_path.suffix}"
            
            # Check for duplicates
            file_hash = self._get_file_hash(file_path)
            if file_hash in self.processed_files:
                return False, f"Already processed (duplicate): {file_path.name}"
            
            # Generate new filename
            new_filename = self.generate_new_filename(file_path, contact_name)
            
            # Get target folder based on file date
            file_date = self.get_file_date(file_path)
            target_folder = self.folder_manager.get_target_folder(file_date)
            target_path = target_folder / new_filename
            
            # Handle filename conflicts
            counter = 1
            original_target = target_path
            while target_path.exists():
                stem = original_target.stem
                suffix = original_target.suffix
                target_path = target_folder / f"{stem}_{counter}{suffix}"
                counter += 1
            
            # Move file
            shutil.move(str(file_path), str(target_path))
            
            # Log processed file
            self._save_processed_log(file_hash)
            
            folder_info = self.folder_manager.get_folder_info(file_date)
            self.logger.info(f"Processed: {file_path.name} -> {new_filename} in {folder_info['full_path']}")
            
            return True, f"Moved to {folder_info['full_path']}\\{target_path.name}"
            
        except Exception as e:
            self.logger.error(f"Error processing {file_path.name}: {e}")
            return False, f"Error: {str(e)}"
    
    def process_folder(self, folder_path: Path, contact_name: str = "") -> Dict[str, int]:
        """Process all valid files in a folder"""
        results = {"processed": 0, "skipped": 0, "errors": 0}
        
        for file_path in folder_path.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in self.valid_extensions:
                success, msg = self.process_file(file_path, contact_name)
                if success:
                    results["processed"] += 1
                elif "Already processed" in msg:
                    results["skipped"] += 1
                else:
                    results["errors"] += 1
                    self.logger.warning(f"Skipped {file_path.name}: {msg}")
        
        return results


def create_file_processor(config: Dict[str, Any]) -> FileProcessor:
    """Factory function to create FileProcessor"""
    return FileProcessor(config)