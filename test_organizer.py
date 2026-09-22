"""
Test script to verify the invoice organizer works correctly
"""
import os
import tempfile
import shutil
from datetime import datetime
from pathlib import Path

# Add parent directory to path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from folder_structure import FolderStructureManager
from file_processor import FileProcessor


def test_folder_structure():
    """Test folder structure creation"""
    print("Testing folder structure...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = FolderStructureManager(tmpdir)
        
        # Test various dates
        test_dates = [
            datetime(2024, 1, 15),   # Q1, Week 3
            datetime(2024, 3, 28),   # Q1, Week 5
            datetime(2024, 4, 5),    # Q2, Week 1
            datetime(2024, 6, 20),   # Q2, Week 3
            datetime(2024, 7, 10),   # Q3, Week 2
            datetime(2024, 10, 25),  # Q4, Week 4
            datetime(2024, 12, 31),  # Q4, Week 5
        ]
        
        for dt in test_dates:
            folder = manager.get_target_folder(dt)
            info = manager.get_folder_info(dt)
            print(f"  {dt.strftime('%Y-%m-%d')} -> {info['quarter_name']}/{info['month_folder']}/{info['week_folder']}")
            assert folder.exists(), f"Folder not created: {folder}"
        
        print("  ✓ Folder structure test passed")


def test_file_processor():
    """Test file renaming and processing"""
    print("\nTesting file processor...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        source_dir = tmpdir / "source"
        dest_dir = tmpdir / "dest"
        source_dir.mkdir()
        dest_dir.mkdir()
        
        # Create test config
        config = {
            'destination_root': str(dest_dir),
            'contractor_mappings': {
                'ABC Construction': 'ABC',
                'XYZ Builders': 'XYZ',
                'PQR Contractors': 'PQR',
            },
            'default_contractor_code': 'UNK',
            'purchase_source_mappings': {
                'cement': 'CEM',
                'steel': 'STL',
                'sand': 'SND',
                'brick': 'BRK',
            },
            'default_purchase_source': 'GEN',
            'valid_extensions': ['.jpg', '.jpeg', '.png', '.pdf'],
            'process_existing_files': False,
            'watch_subdirectories': True,
            'log_level': 'INFO',
            'log_file': 'test.log'
        }
        
        processor = FileProcessor(config)
        
        # Create test files
        test_files = [
            ("ABC Construction_cement_20240115.jpg", "ABC Construction"),
            ("XYZ_steel_20240320.png", "XYZ Builders"),
            ("PQR_brick_20240610.pdf", "PQR Contractors"),
            ("Unknown_sand_20240705.jpg", ""),
            ("IMG-20240815-WA0001.jpg", "ABC Construction"),
        ]
        
        for filename, contact in test_files:
            (source_dir / filename).write_bytes(b"fake image data")
        
        # Process files
        results = processor.process_folder(source_dir)
        print(f"  Results: {results}")
        
        # Verify renamed files in destination
        for year_folder in dest_dir.iterdir():
            if year_folder.is_dir():
                for quarter_folder in year_folder.iterdir():
                    for month_folder in quarter_folder.iterdir():
                        for week_folder in month_folder.iterdir():
                            for file in week_folder.iterdir():
                                print(f"  Organized: {file.relative_to(dest_dir)}")
        
        assert results['processed'] == 5, f"Expected 5 processed, got {results['processed']}"
        print("  ✓ File processor test passed")


def test_date_extraction():
    """Test date extraction from filenames"""
    print("\nTesting date extraction...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        dest_dir = tmpdir / "dest"
        dest_dir.mkdir()
        
        config = {
            'destination_root': str(dest_dir),
            'contractor_mappings': {'Test': 'TST'},
            'default_contractor_code': 'UNK',
            'purchase_source_mappings': {'cement': 'CEM'},
            'default_purchase_source': 'GEN',
            'valid_extensions': ['.jpg'],
            'process_existing_files': False,
            'watch_subdirectories': True,
            'log_level': 'INFO',
            'log_file': 'test.log'
        }
        
        processor = FileProcessor(config)
        
        test_cases = [
            ("IMG-20240115-WA0001.jpg", datetime(2024, 1, 15)),
            ("WhatsApp Image 2024-03-20 at 10.30.00.jpg", datetime(2024, 3, 20)),
            ("VID_20240615_143022.mp4", datetime(2024, 6, 15)),
            ("20241225_invoice.jpg", datetime(2024, 12, 25)),
            ("15-01-2024_receipt.jpg", datetime(2024, 1, 15)),
        ]
        
        for filename, expected_date in test_cases:
            file_path = Path(filename)
            extracted = processor.extract_date_from_filename(filename)
            print(f"  {filename} -> {extracted}")
            if extracted:
                assert extracted.year == expected_date.year
                assert extracted.month == expected_date.month
                assert extracted.day == expected_date.day
        
        print("  ✓ Date extraction test passed")


def test_contractor_extraction():
    """Test contractor code extraction"""
    print("\nTesting contractor extraction...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        dest_dir = tmpdir / "dest"
        dest_dir.mkdir()
        
        config = {
            'destination_root': str(dest_dir),
            'contractor_mappings': {
                'ABC Construction': 'ABC',
                'XYZ Builders': 'XYZ',
            },
            'default_contractor_code': 'UNK',
            'purchase_source_mappings': {'cement': 'CEM'},
            'default_purchase_source': 'GEN',
            'valid_extensions': ['.jpg'],
            'process_existing_files': False,
            'watch_subdirectories': True,
            'log_level': 'INFO',
            'log_file': 'test.log'
        }
        
        processor = FileProcessor(config)
        
        test_cases = [
            ("ABC_Construction_cement.jpg", "ABC"),
            ("XYZ Builders_steel.jpg", "XYZ"),
            ("Unknown_vendor_cement.jpg", "UNK"),
            ("invoice_ABC_Construction.pdf", "ABC"),
        ]
        
        for filename, expected in test_cases:
            code = processor.extract_contractor_code(filename, "")
            print(f"  {filename} -> {code} (expected: {expected})")
            assert code == expected, f"Expected {expected}, got {code}"
        
        print("  ✓ Contractor extraction test passed")


if __name__ == "__main__":
    print("=" * 50)
    print("Running Invoice Organizer Tests")
    print("=" * 50)
    
    test_folder_structure()
    test_file_processor()
    test_date_extraction()
    test_contractor_extraction()
    
    print("\n" + "=" * 50)
    print("All tests passed! ✓")
    print("=" * 50)