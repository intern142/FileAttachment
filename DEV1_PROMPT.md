# DEV 1 HANDOFF PROMPT
## Paste this into your opencode terminal:

---

**Context:** Property taxation invoice organizer. Dev 2 handling UI/integration (GUI, WhatsApp monitor, Windows scripts). You own core logic.

**Repo:** Already cloned. Open in VS Code → terminal → `opencode`

**Your Tasks (priority order):**

### 1. Add PDF Support (30 min)
```bash
# Check current extensions in config
cat config/contractors.json
```
- Add `.pdf` to `supported_extensions` in config
- Update `organizer.py` filename_format to handle `.pdf` (keep `.jpg` default)
- Test: `python -m src.cli test.pdf --person john_doe --contractor "ABC Construction" --purchased-from "Home Depot" --date 2026-01-15`

### 2. Add File Logging (20 min)
```bash
# Look at organizer.py logging setup
grep -n "logging" src/organizer.py
```
- Add rotating file handler to `logs/organizer.log`
- Keep console output, add file with timestamps
- Test: run CLI, check `logs/organizer.log`

### 3. Config Validation on Startup (15 min)
```bash
# See config loading in organizer.py __init__
head -40 src/organizer.py
```
- Validate required keys exist: `contractors`, `accounts_team`, `base_folder`
- Validate each contractor has short code
- Exit with clear error if missing

### 4. File Write Completion Check (15 min)
```bash
# See WhatsAppDownloadHandler.on_created in whatsapp_monitor.py
grep -A 20 "on_created" src/whatsapp_monitor.py
```
- Current: `time.sleep(1)` debounce
- Better: poll file size until stable (2 checks, 500ms apart)
- Prevents organizing partial downloads

### 5. Quick Integration Test (15 min)
```bash
# Run all tests
python -m src.organizer
python -m src.cli --help
python -m src.batch_process examples/batch_example.csv
```

---

**Key Files You Own:**
- `src/organizer.py` - Core engine
- `src/cli.py` - CLI
- `src/batch_process.py` - Batch
- `config/contractors.json` - Config

**Don't Touch (Dev 2):**
- `src/gui.py`, `src/whatsapp_monitor.py`
- `setup.bat`, `start_monitor.bat`
- `README.md`, `PROGRESS.md`

---

**Run This First to Verify Setup:**
```bash
cd /path/to/FileAttachment
python -m src.organizer
# Should print: "Folder structure created successfully!"
```

**When Done:** Update `PROGRESS.md` via `python update_progress.py "Task name" --status done`

---

**Questions?** Check `TASKS.md` for full list or ask Dev 2.