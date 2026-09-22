"""
File Watcher
Monitors WhatsApp download folder for new invoice files
"""
import time
import logging
from pathlib import Path
from typing import Optional, Callable
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent, FileMovedEvent

from file_processor import FileProcessor, create_file_processor


class InvoiceFileHandler(FileSystemEventHandler):
    """Handles file system events for invoice files"""
    
    def __init__(self, processor: FileProcessor, valid_extensions: set, 
                 contact_name_extractor: Optional[Callable[[Path], str]] = None):
        self.processor = processor
        self.valid_extensions = {ext.lower() for ext in valid_extensions}
        self.contact_name_extractor = contact_name_extractor
        self.logger = logging.getLogger(__name__)
        self._pending_files = {}  # Track files being written
    
    def _is_valid_file(self, file_path: Path) -> bool:
        """Check if file should be processed"""
        return file_path.is_file() and file_path.suffix.lower() in self.valid_extensions
    
    def _get_contact_name(self, file_path: Path) -> str:
        """Extract contact name from file path or use extractor"""
        if self.contact_name_extractor:
            try:
                return self.contact_name_extractor(file_path)
            except Exception:
                pass
        return ""
    
    def _wait_for_file_ready(self, file_path: Path, max_wait: int = 10) -> bool:
        """Wait for file to be fully written (size stable)"""
        last_size = -1
        stable_count = 0
        
        for _ in range(max_wait):
            try:
                current_size = file_path.stat().st_size
                if current_size == last_size and current_size > 0:
                    stable_count += 1
                    if stable_count >= 2:  # Stable for 2 checks
                        return True
                else:
                    stable_count = 0
                last_size = current_size
                time.sleep(0.5)
            except (OSError, FileNotFoundError):
                time.sleep(0.5)
        
        return False
    
    def on_created(self, event: FileCreatedEvent):
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        if not self._is_valid_file(file_path):
            return
        
        self.logger.info(f"New file detected: {file_path.name}")
        
        # Wait for file to be fully written
        if not self._wait_for_file_ready(file_path):
            self.logger.warning(f"File not ready after wait: {file_path.name}")
            return
        
        # Process file
        contact_name = self._get_contact_name(file_path)
        success, msg = self.processor.process_file(file_path, contact_name)
        if success:
            self.logger.info(f"Auto-processed: {msg}")
        else:
            self.logger.warning(f"Failed to process {file_path.name}: {msg}")
    
    def on_moved(self, event: FileMovedEvent):
        if event.is_directory:
            return
        
        dest_path = Path(event.dest_path)
        if not self._is_valid_file(dest_path):
            return
        
        self.logger.info(f"File moved/renamed: {dest_path.name}")
        
        # Wait for file to be ready
        if not self._wait_for_file_ready(dest_path):
            self.logger.warning(f"Moved file not ready: {dest_path.name}")
            return
        
        # Process file
        contact_name = self._get_contact_name(dest_path)
        success, msg = self.processor.process_file(dest_path, contact_name)
        if success:
            self.logger.info(f"Auto-processed (moved): {msg}")
        else:
            self.logger.warning(f"Failed to process moved file {dest_path.name}: {msg}")


class WhatsAppFolderWatcher:
    """Watches WhatsApp download folder for new invoice files"""
    
    def __init__(self, config: Dict[str, Any], processor: FileProcessor):
        self.config = config
        self.processor = processor
        self.logger = logging.getLogger(__name__)
        self.observer: Optional[Observer] = None
        self.handler: Optional[InvoiceFileHandler] = None
    
    def _extract_contact_from_path(self, file_path: Path) -> str:
        """
        Extract contact name from WhatsApp folder structure.
        WhatsApp typically organizes by contact in subfolders.
        """
        # WhatsApp Images folder structure:
        # WhatsApp Images/Contact Name/IMG_20240115.jpg
        # Or: WhatsApp Images/Private/Contact Name/IMG_20240115.jpg
        try:
            # Get relative path from WhatsApp root
            whatsapp_root = Path(self.config['whatsapp_download_folder']).resolve()
            file_resolved = file_path.resolve()
            
            if whatsapp_root in file_resolved.parents:
                rel_path = file_resolved.relative_to(whatsapp_root)
                # First part after root is usually contact name
                parts = rel_path.parts
                if len(parts) >= 2:
                    return parts[0]  # Contact folder name
                elif len(parts) == 1:
                    return "Unknown_Contact"
        except Exception:
            pass
        return ""
    
    def start(self):
        """Start watching the folder"""
        watch_folder = Path(self.config['whatsapp_download_folder'])
        
        # Expand user path
        watch_folder = Path(str(watch_folder).replace('{username}', 
                            os.getenv('USERNAME', os.getenv('USER', 'User'))))
        
        if not watch_folder.exists():
            self.logger.error(f"Watch folder does not exist: {watch_folder}")
            self.logger.info("Please update config.yaml with correct WhatsApp folder path")
            return False
        
        self.logger.info(f"Starting watcher on: {watch_folder}")
        
        # Create handler
        self.handler = InvoiceFileHandler(
            processor=self.processor,
            valid_extensions=self.config.get('valid_extensions', ['.jpg', '.jpeg', '.png', '.pdf']),
            contact_name_extractor=self._extract_contact_from_path
        )
        
        # Create observer
        self.observer = Observer()
        recursive = self.config.get('watch_subdirectories', True)
        self.observer.schedule(self.handler, str(watch_folder), recursive=recursive)
        self.observer.start()
        
        self.logger.info("Watcher started successfully")
        return True
    
    def stop(self):
        """Stop watching"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.logger.info("Watcher stopped")
    
    def process_existing(self) -> Dict[str, int]:
        """Process all existing files in watch folder"""
        watch_folder = Path(self.config['whatsapp_download_folder'])
        watch_folder = Path(str(watch_folder).replace('{username}', 
                            os.getenv('USERNAME', os.getenv('USER', 'User'))))
        
        if not watch_folder.exists():
            self.logger.error(f"Watch folder does not exist: {watch_folder}")
            return {"processed": 0, "skipped": 0, "errors": 0}
        
        self.logger.info(f"Processing existing files in: {watch_folder}")
        return self.processor.process_folder(watch_folder)


import os  # Moved import to top in actual file