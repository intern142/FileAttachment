# Work Split: WhatsApp Invoice Organizer
**Total: ~7-8 hours | 2 People | Vertical Slices (each owns full stack for their area)**

---

## Person A: Core Processing Pipeline
**Owner of: File renaming, folder hierarchy, moving, CLI interface**

### Responsibilities (Full Stack)
| Layer | Components |
|-------|------------|
| **Config/Input** | `config.yaml` contractor & source mappings, validation |
| **Backend Logic** | `folder_structure.py`, `file_processor.py` (core classes) |
| **CLI/Frontend** | `main.py` argument parsing, interactive mode, progress display |
| **Testing** | `test_organizer.py` unit tests for processor & folders |

### Deliverables
- [ ] `FileProcessor` class: rename logic, date extraction, contractor mapping
- [ ] `FolderStructureManager`: Year/Q/Month/Week creation
- [ ] CLI: `python main.py --process-existing`, `--dry-run`, `--stats`
- [ ] Unit tests: 90% coverage on processor & folder logic
- [ ] Config validation with clear error messages

### Files Owned
```
folder_structure.py      (full ownership)
file_processor.py        (full ownership)
main.py                  (CLI arguments, main flow)
config.yaml              (mappings section)
test_organizer.py        (processor/folder tests)
```

---

## Person B: Monitoring & Operations
**Owner of: Real-time watching, config management, logging, packaging**

### Responsibilities (Full Stack)
| Layer | Components |
|-------|------------|
| **Config/Input** | `config.yaml` paths, watcher settings, logging config |
| **Backend Logic** | `file_watcher.py`, duplicate detection, file readiness |
| **CLI/Frontend** | `setup.bat`, `run.bat`, system tray / background service |
| **Testing** | Integration tests, end-to-end scenarios |

### Deliverables
- [ ] `WhatsAppFolderWatcher`: watchdog integration, contact extraction
- [ ] Duplicate prevention (hash-based, survives restarts)
- [ ] File readiness detection (wait for WhatsApp write completion)
- [ ] Windows packaging: `setup.bat`, `run.bat`, auto-start option
- [ ] Logging: rotation, levels, structured output
- [ ] Integration tests: watch → process → verify folder structure

### Files Owned
```
file_watcher.py          (full ownership)
setup.bat                (full ownership)
run.bat                  (full ownership)
config.yaml              (paths, watcher, logging sections)
test_organizer.py        (watcher/integration tests)
requirements.txt         (dependency management)
```

---

## Shared / Contract
| Item | Agreement |
|------|-----------|
| **Config format** | YAML, single `config.yaml`, both read/write own sections |
| **Processor API** | `FileProcessor(config).process_file(path, contact_name)` → `(bool, str)` |
| **Folder API** | `FolderStructureManager(root).get_target_folder(date)` → `Path` |
| **Logging** | Standard `logging` module, shared `invoice_organizer.log` |
| **Error handling** | Exceptions bubble up, main.py catches & logs |

---

## Daily Sync (15 min)
| Time | Focus |
|------|-------|
| Morning | Blockers, config changes needed |
| Evening | Merge to main, run integration test |

---

## Integration Points (Touch Once)
1. **config.yaml** - Single source of truth, sections owned separately
2. **main.py** - Person A owns CLI, imports Person B's watcher
3. **test_organizer.py** - Each adds tests for their area

---

## Time Allocation (8 hrs)
| Phase | Person A | Person B |
|-------|----------|----------|
| Setup & Config | 1 hr | 1 hr |
| Core Implementation | 3 hrs | 3 hrs |
| Testing & Polish | 2 hrs | 2 hrs |
| Integration & Docs | 1 hr | 1 hr |
| **Buffer** | **1 hr** | **1 hr** |

---

## Definition of Done
- [ ] `setup.bat` runs clean on fresh machine
- [ ] `run.bat` starts watcher, processes existing files
- [ ] New WhatsApp download → auto-renamed → correct folder in <3 sec
- [ ] Duplicate downloads ignored
- [ ] Logs show clear success/failure per file
- [ ] All tests pass: `python test_organizer.py`