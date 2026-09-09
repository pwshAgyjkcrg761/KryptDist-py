# <img src="KryptDist_internal/icons/KryptDist_ghost_icon.svg" width="32" height="32"> KryptDist™ <img src="KryptDist_internal/icons/KryptDist_ghost_icon.svg" width="32" height="32">
**A high-performance checksum generator and integrity verification utility supporting primary and distributed subdirectory hash structures.**

---

## Overview
KryptDist™ is a high-performance checksum generation and integrity verification utility designed to produce and validate hierarchical checksum file sets across directories and nested subdirectories. It offers flexible multi-algorithm hashing, incremental updates for existing hash sets, and a streamlined On-Screen Display (OSD) verification workflow.

**Primary Environment:** Developed and tested on **Python 3.14.5** using the **PyQt6** framework. It is intended for archivists, system administrators, and data managers who require deterministic integrity verification, distributed subdirectory checksum sets, and fast multi-engine hashing.

### The Hashing & Verification Engine
The utility combines high-throughput hashing algorithms with intelligent directory traversal and validation routines.

Key operational features include:
1. **MultiHash & Distributed Subdirectory Hashes:** In MultiHash mode, KryptDist generates a root primary `.hash` file representing the entire directory hierarchy alongside individual `.hash` files inside each nested subdirectory in a single, efficient disk-read pass.
2. **Multi-Engine Algorithm Suite:** Supports cutting-edge cryptographic hash functions (BLAKE3, BLAKE2b, BLAKE2s, SHA-512, SHA-256, SHA-3) alongside fast checksum and legacy algorithms (xx3 / xxHash3, SHA-1, MD5, SFV / CRC32).
3. **Smart Incremental Caching:** Automatically parses pre-existing primary and subdirectory hash files, skipping previously verified files and appending only newly detected files to conserve time and disk I/O.
4. **Configurable Exclusion & Ignore Engine:** Automatically filters out checksum files, temporary artifacts, OS metadata (e.g. `desktop.ini`, `thumbs.db`, `.DS_Store`), development caches (`__pycache__`, `.git`, `node_modules`), and system volumes. Full wildcard (`*`, `?`) matching is configurable via **Tools > Preferences**.
5. **Pre-Generation Hash Cleaning:** Optional pre-execution controls allow automatically purging prior primary hash files, existing subdirectory hashes, or both before beginning a fresh hash pass.
6. **Real-Time Verification OSD:** Passing checksum files via the command line, drag-and-drop, or the Windows **SendTo** menu triggers an instant verification pass monitored by a compact, draggable On-Screen Display widget with persistent screen positioning.
7. **Headless CLI & Single-File Verification:** Features direct command-line arguments (`-v` / `--verify-file`) to verify individual files against local or parent hash containers headlessly with zero GUI overhead, returning standard process exit codes (`0` for intact, `2` for mismatch/missing) for integration with managers such as HashMan.
8. **Automated Error Logging:** Detects hash mismatches, corrupted files, and missing assets during verification. Triggers a visual alert and compiles an error log report in `KryptDist_internal/logs/`, opening it automatically on Windows systems.
9. **Drag & Drop Target Management:** Easily queue files and folders through an interactive drop target list with path controls for directory browsing, file selection, and individual item removal.
10. **Persistent UI State & Theming:** Remembers window geometry, OSD screen coordinates, algorithm choices, processing options, ignore rules, and user-selected Dark, Light, or System-synced UI palettes.

---

## Feature Reference

| Option / Feature | Description |
| :--- | :--- |
| **MultiHash Mode** | Generates a root primary `.hash` file and distributed subdirectory `.hash` files throughout the directory tree. |
| **Primary Hash Only Mode** | Generates only the root directory's primary `.hash` file without distributing hashes to subfolders. |
| **Incremental Smart Hashing** | Skips already-hashed relative paths recorded in existing checksum files and appends newly discovered files. |
| **Preferences & Ignore Rules** | Configures comma-separated extensions, filenames, and directory exclusions with wildcard support. |
| **Delete Primary Hashes First** | Automatically deletes existing root `.hash` files before scanning and calculating new digests. |
| **Delete Subdirectory Hashes First** | Traverses nested subfolders to remove existing checksum files while leaving primary hashes intact. |
| **Verification OSD** | A lightweight, frameless status overlay providing live feedback during file verification passes. |
| **Headless CLI Verification** | Verifies individual line items via `-v <file>` without initializing the GUI, returning standard exit codes (`0` or `2`). |
| **Automated Log Reports** | Compiles detailed mismatch and missing-file records to `KryptDist_internal/logs/` upon verification failure. |
| **Theme Engine** | Full support for Dark, Light, and System-synced palettes via a customized `QPalette` implementation. |

---

## Command Line Usage

### Headless Single-File Verification
```text
python.exe KryptDist.py -v "path/to/target_file.mkv"
python.exe KryptDist.py --verify-file "target_file.mkv" --hash-file "custom_name.hash"
```
* **Exit Code `0`:** Checksum verified successfully.
* **Exit Code `2`:** Checksum mismatch, missing file, or invalid entry.

### Container Verification (OSD Mode)
```text
python.exe KryptDist.py "path/to/folder.hash"
```

---

## Assets & Licensing
This software is released under the **GNU General Public License v3**.

### Icon Credits
* **File:** `KryptDist_ghost_icon.svg`
    * **Asset:** Ghost SVG Vector
    * **Source:** <a href="https://www.svgrepo.com/svg/54269/ghost" target="_blank">https://www.svgrepo.com/svg/54269/ghost</a>
    * **License:** <a href="https://creativecommons.org/publicdomain/zero/1.0/" target="_blank">CC0 License</a>
    * **Modifications:** Modified by pwshAgyjkcrg761.

---

## Dependencies
* **OS:** Microsoft Windows 10 / 11 (Cross-platform compatible).
* **Python:** 3.14.5+ (Recommended).
* **PyQt6:** Required for Graphical User Interface and OSD components.
* **Optional Packages:**
  * `blake3` (for hardware-accelerated BLAKE3 hashing)
  * `xxhash` (for fast xx3 / xxh3_64 hashing)

## Support & Maintenance
**This repository is provided "as-is" for archival purposes.** The author is not actively looking for feedback, feature requests, or bug reports. The issue tracker is disabled.

## Disclaimer
*KryptDist™ is an integrity hashing and verification utility. The author is not responsible for data loss resulting from hardware failure, storage degradation, or improper file handling. Always maintain verified secondary and off-site backup copies.*

---
> **Document Control**<br>
> *This document is up-to-date with the following version of KryptDist™.*<br>
> *2026.09.08__18.53.26*