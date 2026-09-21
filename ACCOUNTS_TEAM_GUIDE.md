# Quick Start Guide - Invoice Organizer
## For Accounts Team (Property Taxation Project)

---

## 🎯 What This Does
Automatically renames and files WhatsApp invoice receipts into organized folders:
```
Invoices/
└── john_doe/
    └── Q1_Jan-Mar/
        └── January/
            └── Week_3/
                └── ABC-HOM-2026-01-15.jpg
```
**Format:** `CONTRACTOR-VENDOR-YYYY-MM-DD.jpg`

---

## 🚀 Daily Workflow (30 seconds)

### Option 1: Auto-Monitor (Recommended - Set Once, Forget)
1. **Double-click** `Invoice Monitor` shortcut on Desktop
2. **Select:** `1` (WhatsApp Personal) or `2` (WhatsApp Business)
3. **Enter:** Your name → Contractor → Vendor/Store
4. **Minimize** the window - it runs in background
5. **Work normally** - download invoices from WhatsApp → they auto-organize!

### Option 2: Manual (One-off invoices)
1. **Double-click** `run_gui.bat` (or run `python -m src.gui`)
2. **Fill form:**
   - Person: *your name*
   - Contractor: *select from dropdown*
   - Purchased From: *store/vendor name*
   - Date: *invoice date (YYYY-MM-DD)*
3. **Browse** → select downloaded receipt
4. **Click** "Organize Invoice"
5. **Done!** File is renamed & filed correctly

---

## 📥 How to Download from WhatsApp
1. Open WhatsApp Desktop on office PC
2. Find invoice image in chat
3. **Right-click** → **Save As** → saves to `WhatsApp Downloads` folder
4. **That's it!** Auto-monitor picks it up instantly.

---

## 🔧 First-Time Setup (Run Once)
```cmd
setup.bat
```
- Installs required components
- Creates folder structure
- Detects your WhatsApp folder automatically

---

## 🆘 Troubleshooting

| Problem | Solution |
|---------|----------|
| "File not organized" | Check monitor window is running (black cmd window) |
| Wrong folder | Verify Person/Contractor/Vendor entered correctly |
| Duplicate file | Auto-adds `_1`, `_2` - check Week subfolders |
| "Python not found" | Re-run `setup.bat` as Administrator |

---

## 📁 Where Files Go
```
Invoices\
└── YOUR_NAME\
    ├── Q1_Jan-Mar\ (Jan-Mar)
    ├── Q2_Apr-Jun\ (Apr-Jun)
    ├── Q3_Jul-Sep\ (Jul-Sep)
    └── Q4_Oct-Dec\ (Oct-Dec)
        └── Month\
            └── Week_1 to Week_5\
                └── ABC-HOM-2026-01-15.jpg
```

---

## 📞 Support
- **Dev 1 (Core):** [Name] - logic, batch, config
- **Dev 2 (UI/Monitor):** [Name] - GUI, auto-monitor, shortcuts

**Version:** 1.0 | **Updated:** 2026-09-21