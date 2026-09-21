# Invoice Organizer - Property Taxation Project

Automates downloading, renaming, and organizing WhatsApp invoice receipts for accounts team.

## Folder Structure Created

```
Invoices/
├── john_doe/
│   ├── Q1_Jan-Mar/
│   │   ├── January/
│   │   │   ├── Week_1/
│   │   │   ├── Week_2/
│   │   │   ├── Week_3/
│   │   │   ├── Week_4/
│   │   │   └── Week_5/
│   │   ├── February/
│   │   └── March/
│   ├── Q2_Apr-Jun/
│   ├── Q3_Jul-Sep/
│   └── Q4_Oct-Dec/
├── jane_smith/
└── mike_wilson/
```

## Filename Format

`{contractor_short}-{purchased_from_short}-{YYYY-MM-DD}.jpg`

Examples:
- `ABC-HOM-2026-01-15.jpg` (ABC Construction - Home Depot)
- `XYZ-LOW-2026-02-20.jpg` (XYZ Builders - Lowe's)

## Quick Start (Windows Office Desktop)

### One-Command Setup
```cmd
setup.bat
```
This installs dependencies, creates folder structure, and detects WhatsApp folder.

### Manual Setup
1. **Install Dependencies**
   ```cmd
   pip install -r requirements.txt
   ```

2. **Configure Contractors** (edit `config/contractors.json`)
   ```json
   {
     "contractors": {
       "ABC Construction": "ABC",
       "XYZ Builders": "XYZ"
     },
     "accounts_team": ["john_doe", "jane_smith", "mike_wilson"],
     "base_folder": "Invoices"
   }
   ```

3. **Create Folder Structure**
   ```cmd
   python -m src.organizer
   ```

### Daily Usage - Auto Monitor (Recommended)
```cmd
start_monitor.bat
```
- Select WhatsApp or WhatsApp Business
- Enter person, contractor, purchased-from
- Runs in background, auto-organizes new downloads

### Other Options

#### GUI (Accounts Team)
```cmd
python -m src.gui
```

#### Command Line
```cmd
python -m src.cli "receipt.jpg" --person john_doe --contractor "ABC Construction" --purchased-from "Home Depot" --date 2026-01-15
```

## Usage Options

### Option A: Command Line (Developer 1)
```bash
# Single file
python -m src.cli "C:\Downloads\receipt.jpg" --person john_doe --contractor "ABC Construction" --purchased-from "Home Depot" --date 2026-01-15

# Folder batch
python -m src.cli "C:\Downloads\invoices" --person john_doe --contractor "ABC Construction" --purchased-from "Home Depot" --date 2026-01-15

# Copy instead of move
python -m src.cli ... --copy
```

### Option B: GUI (Accounts Team)
```bash
python -m src.gui
```
- Select person, contractor, purchased from, date
- Browse for file/folder
- Click "Organize Invoice"

### Option C: Auto-Monitor WhatsApp Downloads (Developer 2)
```bash
python -m src.whatsapp_monitor --download-folder "C:\Users\Name\WhatsApp Downloads" --person john_doe --contractor "ABC Construction" --purchased-from "Home Depot"
```
Monitors folder and auto-organizes new downloads.

### Option D: Batch Processing
```bash
# CSV batch
python -m src.batch_process examples/batch_example.csv

# JSON batch
python -m src.batch_process examples/batch_example.json
```

## Work Distribution

### Developer 1 (Core Logic)
- `src/organizer.py` - Main organization logic
- `src/cli.py` - Command line interface
- `src/batch_process.py` - Batch processing
- `config/contractors.json` - Configuration

### Developer 2 (Integration & UI)
- `src/whatsapp_monitor.py` - WhatsApp folder monitoring
- `src/gui.py` - Tkinter GUI for accounts team
- `examples/` - Example batch files
- Testing & documentation

## WhatsApp Integration Notes (Windows)

**Auto-detected paths (no config needed):**
- **WhatsApp Desktop**: `C:\Users\{user}\WhatsApp Downloads\`
- **WhatsApp Business**: `C:\Users\{user}\WhatsApp Business Downloads\`
- **Fallback**: `C:\Users\{user}\Downloads\WhatsApp\`

**Manual override** (if auto-detect fails):
Edit `config/contractors.json`:
```json
{
  "whatsapp_download_folder": "C:\\Users\\Name\\Custom\\Path",
  "whatsapp_business_download_folder": "C:\\Users\\Name\\Custom\\Business\\Path"
}
```

**How it works:**
1. User receives invoice on WhatsApp desktop app
2. Clicks download → saves to WhatsApp Downloads folder
3. Monitor detects new file (1 sec delay for complete write)
4. Auto-renames: `ABC-HOM-2026-01-15.jpg`
5. Moves to: `Invoices\john_doe\Q1_Jan-Mar\January\Week_3\`

## Testing

```bash
# Test folder creation
python -m src.organizer

# Test single file
python -m src.cli test.jpg --person john_doe --contractor "ABC Construction" --purchased-from "Home Depot" --date 2026-01-15

# Run GUI
python -m src.gui
```

## Troubleshooting

- **Permission errors**: Run as administrator or check folder permissions
- **File not found**: Verify source path exists
- **Date format**: Use YYYY-MM-DD (e.g., 2026-01-15)
- **Duplicate files**: Auto-appends `_1`, `_2`, etc.