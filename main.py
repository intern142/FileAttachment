"""
Main entry point for WhatsApp Invoice Organizer
CLI Interface - Person A owns this
"""
import sys
import argparse
import logging
import signal
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

from file_processor import create_file_processor
from file_watcher import WhatsAppFolderWatcher
from folder_structure import FolderStructureManager


def setup_logging(config: Dict[str, Any], verbose: bool = False):
    """Configure logging"""
    log_level = logging.DEBUG if verbose else getattr(logging, config.get('log_level', 'INFO').upper())
    log_file = config.get('log_file', 'invoice_organizer.log')
    
    file_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%H:%M:%S'
    )
    
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(log_level)
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(log_level)
    
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    logging.getLogger('watchdog').setLevel(logging.WARNING)


def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """Load configuration from YAML file"""
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def validate_config(config: Dict[str, Any]) -> tuple[bool, list[str]]:
    """Validate configuration, return (is_valid, errors)"""
    errors = []
    
    # Required paths
    whatsapp_path = config.get('whatsapp_download_folder', '')
    if not whatsapp_path or '{username}' in whatsapp_path:
        errors.append("whatsapp_download_folder not configured (contains {username} placeholder)")
    
    dest_path = config.get('destination_root', '')
    if not dest_path:
        errors.append("destination_root not configured")
    
    # Contractor mappings
    if not config.get('contractor_mappings'):
        errors.append("contractor_mappings is empty - add at least one contractor")
    
    return len(errors) == 0, errors


def cmd_watch(args, config: Dict[str, Any]):
    """Watch mode - monitor and auto-process"""
    setup_logging(config, args.verbose)
    logger = logging.getLogger(__name__)
    
    logger.info("Starting WhatsApp Invoice Organizer in WATCH mode")
    
    processor = create_file_processor(config)
    watcher = WhatsAppFolderWatcher(config, processor)
    
    if config.get('process_existing_files', True) and not args.no_existing:
        logger.info("Processing existing files...")
        results = watcher.process_existing()
        logger.info(f"Existing files: {results['processed']} processed, "
                    f"{results['skipped']} skipped, {results['errors']} errors")
    
    if not watcher.start():
        logger.error("Failed to start watcher. Exiting.")
        sys.exit(1)
    
    def signal_handler(signum, frame):
        logger.info("Shutdown signal received")
        watcher.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("Watcher running. Press Ctrl+C to stop.")
    
    try:
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping...")
        watcher.stop()


def cmd_process(args, config: Dict[str, Any]):
    """One-time process existing files"""
    setup_logging(config, args.verbose)
    logger = logging.getLogger(__name__)
    
    logger.info("Starting one-time PROCESS mode")
    
    processor = create_file_processor(config)
    watcher = WhatsAppFolderWatcher(config, processor)
    
    results = watcher.process_existing()
    
    print(f"\nResults:")
    print(f"  Processed: {results['processed']}")
    print(f"  Skipped (duplicates): {results['skipped']}")
    print(f"  Errors: {results['errors']}")
    
    if results['errors'] > 0:
        sys.exit(1)


def cmd_dry_run(args, config: Dict[str, Any]):
    """Simulate processing without moving files"""
    setup_logging(config, args.verbose)
    logger = logging.getLogger(__name__)
    
    logger.info("DRY RUN mode - no files will be moved")
    
    processor = create_file_processor(config)
    watcher = WhatsAppFolderWatcher(config, processor)
    
    # Monkey-patch to simulate
    original_process = processor.process_file
    
    def dry_run_process(file_path, contact_name=""):
        new_name = processor.generate_new_filename(file_path, contact_name)
        file_date = processor.get_file_date(file_path)
        target_folder = processor.folder_manager.get_target_folder(file_date)
        logger.info(f"[DRY RUN] {file_path.name} -> {target_folder}/{new_name}")
        return True, f"[DRY RUN] Would move to {target_folder}/{new_name}"
    
    processor.process_file = dry_run_process
    
    results = watcher.process_existing()
    print(f"\nDry run complete: {results['processed']} files would be processed")


def cmd_stats(args, config: Dict[str, Any]):
    """Show folder structure statistics"""
    setup_logging(config, args.verbose)
    
    dest_root = Path(config.get('destination_root', ''))
    if not dest_root.exists():
        print(f"Destination root not found: {dest_root}")
        return
    
    print(f"\nFolder Statistics for: {dest_root}")
    print("=" * 60)
    
    total_files = 0
    total_size = 0
    
    for year_folder in sorted(dest_root.iterdir()):
        if not year_folder.is_dir():
            continue
        year_files = 0
        year_size = 0
        print(f"\n{year_folder.name}/")
        
        for quarter_folder in sorted(year_folder.iterdir()):
            if not quarter_folder.is_dir():
                continue
            q_files = 0
            print(f"  {quarter_folder.name}/")
            
            for month_folder in sorted(quarter_folder.iterdir()):
                if not month_folder.is_dir():
                    continue
                m_files = 0
                print(f"    {month_folder.name}/")
                
                for week_folder in sorted(month_folder.iterdir()):
                    if not week_folder.is_dir():
                        continue
                    files = list(week_folder.iterdir())
                    if files:
                        print(f"      {week_folder.name}/ ({len(files)} files)")
                        m_files += len(files)
                        for f in files:
                            total_size += f.stat().st_size
                
                q_files += m_files
        
        year_files = q_files
        total_files += year_files
        print(f"  Year total: {year_files} files")
    
    print(f"\n{'='*60}")
    print(f"Total: {total_files} files, {total_size/1024/1024:.2f} MB")


def cmd_validate(args, config: Dict[str, Any]):
    """Validate configuration"""
    is_valid, errors = validate_config(config)
    
    if is_valid:
        print("✓ Configuration is valid")
        print(f"  WhatsApp folder: {config.get('whatsapp_download_folder')}")
        print(f"  Destination: {config.get('destination_root')}")
        print(f"  Contractors: {len(config.get('contractor_mappings', {}))} mapped")
        print(f"  Sources: {len(config.get('purchase_source_mappings', {}))} mapped")
    else:
        print("✗ Configuration errors:")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)


def cmd_test_structure(args, config: Dict[str, Any]):
    """Test folder structure creation"""
    from datetime import datetime
    manager = FolderStructureManager(config.get('destination_root', './test_output'))
    
    test_dates = [
        datetime(2024, 1, 15),
        datetime(2024, 3, 28),
        datetime(2024, 4, 5),
        datetime(2024, 6, 20),
        datetime(2024, 7, 10),
        datetime(2024, 10, 25),
        datetime(2024, 12, 31),
    ]
    
    print("Folder Structure Test:")
    print("=" * 60)
    for dt in test_dates:
        folder = manager.get_target_folder(dt)
        info = manager.get_folder_info(dt)
        print(f"  {dt.strftime('%Y-%m-%d')} -> {info['quarter_name']}/{info['month_folder']}/{info['week_folder']}")
        print(f"    Path: {folder}")
    
    print("\n✓ All folders created successfully")


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser"""
    parser = argparse.ArgumentParser(
        description='WhatsApp Invoice Organizer - Automatically rename and organize invoice receipts',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Watch mode (default)
  python main.py watch              # Explicit watch mode
  python main.py process            # One-time process existing files
  python main.py dry-run            # Simulate without moving
  python main.py stats              # Show folder statistics
  python main.py validate           # Check configuration
  python main.py test-structure     # Test folder hierarchy
        """
    )
    
    parser.add_argument(
        '-c', '--config',
        default='config.yaml',
        help='Path to config file (default: config.yaml)'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable debug logging'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Watch command (default)
    watch_parser = subparsers.add_parser('watch', help='Monitor folder and auto-process (default)')
    watch_parser.add_argument('--no-existing', action='store_true', help='Skip processing existing files')
    
    # Process command
    subparsers.add_parser('process', help='One-time process all existing files')
    
    # Dry run
    subparsers.add_parser('dry-run', help='Simulate processing without moving files')
    
    # Stats
    subparsers.add_parser('stats', help='Show organized folder statistics')
    
    # Validate
    subparsers.add_parser('validate', help='Validate configuration')
    
    # Test structure
    subparsers.add_parser('test-structure', help='Test folder hierarchy creation')
    
    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()
    
    # Default to watch if no command
    if not args.command:
        args.command = 'watch'
    
    # Load config
    try:
        config = load_config(args.config)
    except FileNotFoundError:
        print(f"ERROR: Config file not found: {args.config}")
        print("Run 'python main.py validate' to check configuration")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR loading config: {e}")
        sys.exit(1)
    
    # Validate config for commands that need it
    if args.command in ('watch', 'process', 'dry-run'):
        is_valid, errors = validate_config(config)
        if not is_valid:
            print("Configuration errors:")
            for err in errors:
                print(f"  - {err}")
            print("\nRun 'python main.py validate' for details")
            sys.exit(1)
    
    # Dispatch commands
    commands = {
        'watch': cmd_watch,
        'process': cmd_process,
        'dry-run': cmd_dry_run,
        'stats': cmd_stats,
        'validate': cmd_validate,
        'test-structure': cmd_test_structure,
    }
    
    if args.command in commands:
        commands[args.command](args, config)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()