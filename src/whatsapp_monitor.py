import os
import time
import json
import logging
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from src.organizer import InvoiceOrganizer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_whatsapp_download_folder() -> Path:
    """Auto-detect WhatsApp download folder on Windows."""
    user_profile = Path(os.environ.get("USERPROFILE", ""))
    
    possible_paths = [
        user_profile / "WhatsApp Downloads",
        user_profile / "Downloads" / "WhatsApp",
        user_profile / "Documents" / "WhatsApp Downloads",
        Path("C:/Users/Public/WhatsApp Downloads"),
    ]
    
    for path in possible_paths:
        if path.exists():
            logger.info(f"Found WhatsApp downloads at: {path}")
            return path
    
    default = user_profile / "WhatsApp Downloads"
    logger.warning(f"WhatsApp folder not found, using default: {default}")
    return default


def get_whatsapp_business_download_folder() -> Path:
    """Auto-detect WhatsApp Business download folder on Windows."""
    user_profile = Path(os.environ.get("USERPROFILE", ""))
    
    possible_paths = [
        user_profile / "WhatsApp Business Downloads",
        user_profile / "Downloads" / "WhatsApp Business",
        user_profile / "Documents" / "WhatsApp Business Downloads",
    ]
    
    for path in possible_paths:
        if path.exists():
            logger.info(f"Found WhatsApp Business downloads at: {path}")
            return path
    
    return user_profile / "WhatsApp Business Downloads"


class WhatsAppDownloadHandler(FileSystemEventHandler):
    def __init__(self, organizer: InvoiceOrganizer, person: str, contractor: str, purchased_from: str):
        self.organizer = organizer
        self.person = person
        self.contractor = contractor
        self.purchased_from = purchased_from
        self.processed_files = set()
    
    def on_created(self, event):
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        if file_path.suffix.lower() not in ['.jpg', '.jpeg', '.png', '.pdf']:
            return
        
        if str(file_path) in self.processed_files:
            return
        
        time.sleep(1)
        
        try:
            invoice_date = datetime.now()
            result = self.organizer.organize_file(
                source_path=str(file_path),
                person=self.person,
                contractor=self.contractor,
                purchased_from=self.purchased_from,
                invoice_date=invoice_date,
                move=True
            )
            logger.info(f"Auto-organized: {result}")
            self.processed_files.add(str(file_path))
        except Exception as e:
            logger.error(f"Failed to auto-organize {file_path}: {e}")


class WhatsAppMonitor:
    def __init__(self, config_path: str = "config/contractors.json"):
        self.organizer = InvoiceOrganizer(config_path)
        self.observer = None
    
    def start_monitoring(
        self,
        download_folder: str,
        person: str,
        contractor: str,
        purchased_from: str
    ):
        download_path = Path(download_folder)
        download_path.mkdir(parents=True, exist_ok=True)
        
        event_handler = WhatsAppDownloadHandler(
            self.organizer, person, contractor, purchased_from
        )
        
        self.observer = Observer()
        self.observer.schedule(event_handler, str(download_path), recursive=False)
        self.observer.start()
        
        logger.info(f"Monitoring {download_folder} for new downloads...")
        logger.info(f"Files will be organized for {person} - {contractor} - {purchased_from}")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.observer.stop()
            logger.info("Monitoring stopped")
        
        self.observer.join()
    
    def stop_monitoring(self):
        if self.observer:
            self.observer.stop()
            self.observer.join()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Monitor WhatsApp downloads folder and auto-organize invoices")
    parser.add_argument("--download-folder", help="WhatsApp downloads folder path (auto-detect if omitted)")
    parser.add_argument("--business", action="store_true", help="Use WhatsApp Business folder")
    parser.add_argument("--person", required=True, help="Accounts team member")
    parser.add_argument("--contractor", required=True, help="Contractor name")
    parser.add_argument("--purchased-from", required=True, dest="purchased_from", help="Purchased from")
    parser.add_argument("--config", default="config/contractors.json", help="Config file")
    
    args = parser.parse_args()
    
    if args.download_folder:
        download_folder = args.download_folder
    elif args.business:
        download_folder = str(get_whatsapp_business_download_folder())
    else:
        download_folder = str(get_whatsapp_download_folder())
    
    monitor = WhatsAppMonitor(args.config)
    monitor.start_monitoring(
        download_folder=download_folder,
        person=args.person,
        contractor=args.contractor,
        purchased_from=args.purchased_from
    )


if __name__ == "__main__":
    main()