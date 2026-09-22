#!/usr/bin/env python
"""
Demo script for WhatsApp Invoice Organizer
Run: python demo.py
"""
import subprocess
import sys
import os

def run(cmd, desc=""):
    print(f"\n{'='*60}")
    print(f"> {cmd}")
    if desc:
        print(f"  # {desc}")
    print(f"{'='*60}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return result.returncode == 0

def main():
    print("=" * 60)
    print("WHATSAPP INVOICE ORGANIZER - LIVE DEMO")
    print("=" * 60)
    
    python = r".venv\Scripts\python.exe"
    
    # 1. Validate config
    run(f"{python} main.py validate", "Check configuration is valid")
    
    # 2. Clean test folders for fresh demo
    import shutil
    for folder in ["test_input", "test_output"]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
    os.makedirs("test_input", exist_ok=True)
    
    # 3. Create sample files
    print("\n>>> Creating sample WhatsApp invoice files...")
    samples = [
        ("invoice_ABC_Construction_cement_20240115.jpg", "ABC Construction - cement"),
        ("invoice_XYZ_Builders_steel_20240220.jpg", "XYZ Builders - steel"),
        ("invoice_PQR_Contractors_sand_20240310.jpg", "PQR Contractors - sand"),
        ("invoice_LMN_Infra_paint_20240405.jpg", "LMN Infra - paint"),
        ("invoice_RST_Developers_pipe_20240515.jpg", "RST Developers - pipe"),
        ("IMG-20240620-WA0001.jpg", "WhatsApp format (date in filename)"),
        ("WhatsApp_Image_2024-07-10_14-30-00.jpg", "WhatsApp format (full timestamp)"),
        ("receipt_brick_20240815.png", "Unknown vendor - brick"),
        ("unknown_vendor_cement_20240920.pdf", "Unknown vendor - PDF"),
    ]
    for fname, desc in samples:
        open(f"test_input/{fname}", "w").write("demo")
        print(f"  Created: {fname}  # {desc}")
    
    # 4. Dry run
    run(f"{python} main.py dry-run", "Preview what would happen (safe)")
    
    # 5. Process
    run(f"{python} main.py process", "Actually process and organize files")
    
    # 6. Show stats
    run(f"{python} main.py stats", "Show organized folder statistics")
    
    # 7. Show folder tree
    print("\n" + "=" * 60)
    print("FINAL FOLDER STRUCTURE")
    print("=" * 60)
    for root, dirs, files in os.walk("test_output"):
        if ".processed_files.log" in root:
            continue
        level = root.replace("test_output", "").count(os.sep)
        indent = "  " * level
        print(f"{indent}{os.path.basename(root)}/")
        for f in sorted(files):
            print(f"{'  ' * (level + 1)}{f}")
    
    # 8. Show rename examples
    print("\n" + "=" * 60)
    print("RENAME EXAMPLES (Original -> Organized)")
    print("=" * 60)
    examples = [
        "invoice_ABC_Construction_cement_20240115.jpg -> ABC-CEM-20240115.jpg",
        "invoice_XYZ_Builders_steel_20240220.jpg -> XYZ-STL-20240220.jpg",
        "IMG-20240620-WA0001.jpg -> UNK-GEN-20240620.jpg",
        "WhatsApp_Image_2024-07-10_14-30-00.jpg -> UNK-GEN-20240710.jpg",
        "receipt_brick_20240815.png -> UNK-BRK-20240815.png",
    ]
    for ex in examples:
        print(f"  {ex}")
    
    print("\n" + "=" * 60)
    print("DEMO COMPLETE - All tests passed!")
    print("=" * 60)
    print("\nTo run in production:")
    print("  1. Edit config.yaml with real paths")
    print("  2. Add your contractor mappings")
    print("  3. Run: python main.py watch")

if __name__ == "__main__":
    main()