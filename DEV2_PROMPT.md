# DEV 2 PROMPT (YOU)
## Your Tasks (run in parallel with Dev 1)

### 1. Test GUI End-to-End (15 min)
```bash
python -m src.gui
```
- Fill all fields: person, contractor, purchased-from, date
- Browse → select test image
- Click "Organize Invoice"
- Verify file appears in correct `Invoices\person\Quarter\Month\Week\`
- Click "Create Folder Structure for All" - should be idempotent

### 2. Test Auto-Monitor with Real WhatsApp (20 min)
```bash
# Option A: Use batch file (easiest)
start_monitor.bat
# → Choose 1 (WhatsApp Personal)
# → Enter: john_doe / ABC Construction / Home Depot
# → Drop a test image in your WhatsApp Downloads folder
# → Verify auto-organized

# Option B: Direct command
python -m src.whatsapp_monitor --person john_doe --contractor "ABC Construction" --purchased-from "Home Depot"
```

### 3. Create Desktop Shortcut (10 min)
```bash
# Create start_monitor.lnk or add to Windows Startup
# PowerShell one-liner:
powershell -Command "$s=(New-Object -ComObject WScript.Shell).CreateShortcut('%USERPROFILE%\Desktop\Invoice Monitor.lnk');$s.TargetPath='cmd.exe';$s.Arguments='/c start_monitor.bat';$s.WorkingDirectory='$(pwd)';$s.Save()"
```

### 4. Write 1-Page Quick-Start Guide (20 min)
Create `ACCOUNTS_TEAM_GUIDE.md`:
- Screenshot of GUI
- 3 steps: Open GUI → Fill form → Click Organize
- Daily workflow: Run `start_monitor.bat` once → work normally
- Troubleshooting: "File not moved?" → check monitor running

### 5. Integration Test with Dev 1 (15 min)
```bash
# After Dev 1 pushes config validation
git pull
python -m src.organizer  # Should still work
python -m src.gui        # Should still work
```

---

**Key Files You Own:**
- `src/gui.py`
- `src/whatsapp_monitor.py`
- `setup.bat`, `start_monitor.bat`
- `README.md`, `PROGRESS.md`, `ACCOUNTS_TEAM_GUIDE.md`

**Sync Points with Dev 1:**
- Config schema changes → update GUI dropdowns
- New log file location → add "View Logs" button in GUI
- PDF support → update GUI file filter

---

**Start Here:**
```bash
cd /path/to/FileAttachment
python -m src.gui
```