# ==============================================================================
# SCRIPT: KryptDist.py
# VERSION: 2026.09.11__20.14.32
# TARGET: Python 3.14.5
#
# Copyright (C) 2026 pwshAgyjkcrg761
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/gpl-3.0.html>.
# ==============================================================================
# <PROTECTED>
# ==============================================================================
# AI INSTRUCTIONS
# Copyright (c) 2026 pwshAgyjkcrg761
# License: MIT
# Source: https://git.disroot.org/pwshAgyjkcrg761/AI_Instructions
#
# AI INSTRUCTIONS v2026.09.01__04.25.09 : 
#
# 1. MESSAGE STAMP: 
#    - Every response containing code MUST begin with a standalone version stamp.
#    - Use CHICAGO TIME (Central Time), 24-hour clock.
#    - Format: YYYY.MM.DD__HH.MM.SS.
#    - CRITICAL: Use the time provided in the prompt or at 
#      https://www.timeanddate.com/worldclock/usa/chicago. Ensure minutes are exact.
#
# 2. VERSION SNIPPET PROHIBITION:
#    - DO NOT provide code snippets, anchors, or steps to update the script's 
#      internal VERSION comment or $scriptVersion variable. 
#    - The user handles internal file versioning manually based on the Message Stamp.
#
# 3. SCRIPT OUTPUT (SURGICAL FIXES ONLY):
#    - Provide minimal, highly targeted, surgical edits. Do not rewrite large blocks or 
#      entire functions.
#    - Always use a codebox with a copy button.
#    - Multiple modifications MUST be presented strictly ONE step at a time. Wait for 
#      user confirmation before proceeding to the next step. 
#    - DO NOT modify or refactor any code inside <PROTECTED> tags.
#
# 4. VERBATIM ANCHOR PROTOCOL (FOR NOTEPAD++):
#    - To facilitate "Find" in Notepad++, always structure edits with:
#      - "Verbatim Anchor (Before)" - The exact lines of existing code immediately before 
#         the change.
#      - "Verbatim Anchor (After)" - The exact lines of existing code immediately after 
#         the change.
#      - "Snippet to REPLACE" - The exact code block to be deleted.
#      - "What to PASTE in its place" - The new code block to be inserted.
#    - Do not summarize, truncate, or refactor the existing code used as an anchor.
#    - Match spaces, comments, and symbols exactly as they appear in the file.
#
# 5. CONTENT PRESERVATION:
#    - Do not remove, modify, or strip out telemetry data or DevDebug information from any 
#      provided code.
# ==============================================================================
# </PROTECTED>

import sys
import os
import json
import hashlib
import fnmatch
import re
import ctypes
import ctypes.wintypes

APP_VERSION = "2026.09.11__20.14.32"

def natural_sort_key(s):
    """Sort strings containing numbers in human/natural order safely across types."""
    return [(0, int(t)) if t.isdigit() else (1, t.lower()) for t in re.split(r'(\d+)', str(s))]

DEFAULT_IGNORE_TYPES = "hash,b3,blake3,b2,blake2,blake2b,blake2s,sha512,sha256,sha3,sha3-256,sha3-512,xx3,xxh3,xxh,sha1,sha,md5,sfv,crc32,crc,lnk,url,m3u,m3u8,pls,log,tmp,temp,bak,part,crdownload"
DEFAULT_IGNORE_FILES = "desktop.ini,folder.jpg,.desktop,.directory,thumbs.db,ehthumbs.db,ehthumbs_vista.db,md5sums,md5sum.txt,sha256sums,sha256sum.txt,sha512sums,sha512sum.txt,checksums.txt,hashes.txt,.DS_Store,._.DS_Store,._*,~$*,pagefile.sys,hiberfil.sys,swapfile.sys,dumpstack.log.tmp"
DEFAULT_IGNORE_FOLDERS = "RECYCLER,$Recycle.Bin,System Volume Information,.Spotlight-V100,.Trashes,.fseventsd,.Trash-*,__pycache__,.pytest_cache,.git,.svn,.hg,node_modules"

def matches_pattern_list(name, pattern_csv):
    """Checks if a file/folder name matches any wildcard/extension pattern in a comma-separated string."""
    if not pattern_csv:
        return False
    patterns = [p.strip() for p in pattern_csv.split(",") if p.strip()]
    name_lower = name.lower()
    for pat in patterns:
        pat_lower = pat.lower()
        if fnmatch.fnmatch(name_lower, pat_lower):
            return True
        # Match bare extensions like 'log' against '.log'
        if not pat_lower.startswith("*") and not pat_lower.startswith("."):
            if fnmatch.fnmatch(name_lower, f"*.{pat_lower}"):
                return True
    return False

def is_ignored(item_name, is_dir=False, ignore_types="", ignore_files="", ignore_folders=""):
    """Determines whether a file or directory should be ignored based on user rules."""
    if is_dir:
        return matches_pattern_list(item_name, ignore_folders)
    
    # Check ignored file extensions / types
    if matches_pattern_list(item_name, ignore_types):
        return True
    # Check ignored specific file names / wildcards
    if matches_pattern_list(item_name, ignore_files):
        return True
    return False

def get_user_profile_dir():
    """Retrieves the user profile directory safely via Win32 API."""
    buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
    # CSIDL_PROFILE = 40 (0x0028)
    if ctypes.windll.shell32.SHGetFolderPathW(None, 40, None, 0, buf) == 0:
        return buf.value
    return os.path.expanduser("~")

import zlib

try:
    import blake3
    HAS_BLAKE3 = True
except ImportError:
    HAS_BLAKE3 = False

try:
    import xxhash
    HAS_XXHASH = True
except ImportError:
    HAS_XXHASH = False

from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QPushButton, QFileDialog, QLabel, QMessageBox, 
                             QDialog, QCheckBox, QTextBrowser, QDialogButtonBox,
                             QComboBox, QProgressBar, QHBoxLayout, QListWidget,
                             QTabWidget, QLineEdit, QFormLayout, QTreeWidget,
                             QTreeWidgetItem)
from PyQt6.QtGui import QActionGroup, QPalette, QColor, QIcon, QPixmap, QPainter, QPen
import ctypes

def get_status_pixmap(status="success", size=48):
    """Draws a crisp green checkmark or red X badge for dialog message boxes."""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    if status == "success":
        painter.setBrush(QColor("#28a745"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(2, 2, size - 4, size - 4)

        pen = QPen(QColor("#ffffff"), 4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.drawLine(int(size * 0.28), int(size * 0.52), int(size * 0.44), int(size * 0.68))
        painter.drawLine(int(size * 0.44), int(size * 0.68), int(size * 0.72), int(size * 0.34))
    else:
        painter.setBrush(QColor("#dc3545"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(2, 2, size - 4, size - 4)

        pen = QPen(QColor("#ffffff"), 4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        margin = int(size * 0.30)
        painter.drawLine(margin, margin, size - margin, size - margin)
        painter.drawLine(size - margin, margin, margin, size - margin)

    painter.end()
    return pixmap


CHECKSUM_EXTS = (
    ".hash", ".b3", ".blake3", ".b2", ".blake2", ".blake2b", ".blake2s",
    ".sha512", ".sha256", ".sha3", ".sha3-256", ".sha3-512",
    ".xx3", ".xxh3", ".xxh", ".sha1", ".sha", ".md5", ".sfv", ".crc32", ".crc"
)

def compute_file_digest(file_path, algo_name):
    """Calculates digest for a single file using the specified algorithm."""
    algo_u = algo_name.upper()
    if "CRC" in algo_u or "SFV" in algo_u:
        crc_val = 0
        with open(file_path, 'rb') as f:
            while chunk := f.read(65536):
                crc_val = zlib.crc32(chunk, crc_val)
        return f"{crc_val & 0xFFFFFFFF:08x}"
    elif "BLAKE3" in algo_u and HAS_BLAKE3:
        hasher = blake3.blake3()
    elif "BLAKE2S" in algo_u:
        hasher = hashlib.blake2s()
    elif "BLAKE2" in algo_u:
        hasher = hashlib.blake2b()
    elif "512" in algo_u and "SHA" in algo_u:
        hasher = hashlib.sha512()
    elif "SHA-3" in algo_u or "SHA3" in algo_u:
        hasher = hashlib.sha3_256()
    elif "256" in algo_u and "SHA" in algo_u:
        hasher = hashlib.sha256()
    elif ("XX3" in algo_u or "XXH3" in algo_u or "XXH" in algo_u) and HAS_XXHASH:
        hasher = xxhash.xxh3_64()
    elif "SHA-1" in algo_u or "SHA1" in algo_u:
        hasher = hashlib.sha1()
    elif "MD5" in algo_u:
        hasher = hashlib.md5()
    else:
        hasher = blake3.blake3() if HAS_BLAKE3 else hashlib.blake2b()

    with open(file_path, 'rb') as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

def verify_single_file_cli(target_file, specified_hash_file=None):
    """Locates target in parent/local .hash files, computes checksum, and returns 0 (OK) or 2 (FAIL)."""
    abs_target = os.path.abspath(target_file)
    if not os.path.exists(abs_target):
        return 2

    # Discover candidate .hash files in working directory, target directory, and parent
    candidate_hash_files = []
    if specified_hash_file and os.path.exists(specified_hash_file):
        candidate_hash_files.append(os.path.abspath(specified_hash_file))
    else:
        search_dirs = [os.getcwd(), os.path.dirname(abs_target), os.path.dirname(os.path.dirname(abs_target))]
        for sdir in search_dirs:
            if sdir and os.path.exists(sdir):
                for f in os.listdir(sdir):
                    if f.lower().endswith(CHECKSUM_EXTS):
                        cand = os.path.join(sdir, f)
                        if cand not in candidate_hash_files:
                            candidate_hash_files.append(cand)

    is_hex = lambda s: all(c in '0123456789abcdefABCDEF' for c in s)

    for hfile in candidate_hash_files:
        base_dir = os.path.dirname(hfile)
        try:
            rel_to_hash = os.path.normpath(os.path.relpath(abs_target, base_dir))
        except ValueError:
            rel_to_hash = os.path.basename(abs_target)
        file_base = os.path.basename(abs_target)

        current_algo = "BLAKE3"
        ext = os.path.splitext(hfile)[1].lower()
        if ext in (".sha3", ".sha3-256", ".sha3-512"): current_algo = "SHA-3"
        elif ext == ".sha256": current_algo = "SHA-256"
        elif ext == ".sha512": current_algo = "SHA-512"
        elif ext == ".md5": current_algo = "MD5"
        elif ext in (".sha1", ".sha"): current_algo = "SHA-1"
        elif ext in (".sfv", ".crc32", ".crc"): current_algo = "SFV / CRC32"
        elif ext in (".xx3", ".xxh3", ".xxh"): current_algo = "xx3"
        elif ext in (".b2", ".blake2", ".blake2b"): current_algo = "BLAKE2b"
        elif ext == ".blake2s": current_algo = "BLAKE2s"

        try:
            with open(hfile, 'r', encoding='utf-8') as f:
                for line in f:
                    line_str = line.strip()
                    line_lower = line_str.lower()

                    # Detect algorithm declarations and Corz Checksum headers
                    if line_lower.startswith("# algorithm:") or line_lower.startswith("; algorithm:"):
                        current_algo = line_str.split(":", 1)[1].strip()
                        continue
                    if "blake2" in line_lower:
                        current_algo = "BLAKE2s"
                        if line_str.startswith('#') or line_str.startswith(';'):
                            continue
                    if "made with checksum" in line_lower:
                        if current_algo == "BLAKE3":
                            current_algo = "BLAKE2s"
                        continue
                    if not line_str or line_str.startswith('#') or line_str.startswith(';'):
                        continue

                    tokens = line_str.split()
                    if len(tokens) >= 2:
                        first_tok = tokens[0].strip()
                        last_tok = tokens[-1].strip()

                        if len(first_tok) in (8, 16, 32, 40, 64, 128) and is_hex(first_tok):
                            expected_hash = first_tok
                            entry_path = line_str.split(maxsplit=1)[1].lstrip('*').strip()
                        elif len(last_tok) == 8 and is_hex(last_tok):
                            expected_hash = last_tok
                            entry_path = line_str.rsplit(maxsplit=1)[0].lstrip('*').strip()
                        else:
                            continue

                        norm_entry = os.path.normpath(entry_path)
                        if norm_entry in (rel_to_hash, file_base, os.path.normpath(target_file)):
                            # Resolve digest algorithm heuristics
                            h_len = len(expected_hash)
                            algo = current_algo
                            if h_len == 8: algo = "SFV / CRC32"
                            elif h_len == 16: algo = "xx3"
                            elif h_len == 32: algo = "MD5"
                            elif h_len == 40: algo = "SHA-1"
                            elif h_len == 64:
                                if not any(k in current_algo.upper() for k in ["BLAKE3", "256", "BLAKE2S", "SHA-3", "SHA3"]):
                                    algo = "BLAKE3"
                            elif h_len == 128:
                                if not any(k in current_algo.upper() for k in ["BLAKE2", "512"]):
                                    algo = "BLAKE2b"

                            try:
                                calculated = compute_file_digest(abs_target, algo)
                                if calculated.lower() == expected_hash.lower():
                                    return 0
                                else:
                                    return 2
                            except Exception:
                                return 2
        except Exception:
            continue

    return 2

class SettingsWrapper:
    def __init__(self, config_path):
        self.path = config_path
        self.data = {}
        if os.path.exists(self.path):
            try:
                with open(self.path, 'r') as f:
                    self.data = json.load(f)
            except: pass
    def value(self, key, default):
        return self.data.get(key, default)
    def setValue(self, key, value):
        self.data[key] = value
        try:
            with open(self.path, 'w') as f:
                json.dump(self.data, f, indent=4)
        except: pass


class PreferencesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_app = parent
        self.setWindowTitle("Preferences")
        self.resize(560, 320)

        main_layout = QVBoxLayout(self)
        self.tabs = QTabWidget()

        # Tab 1: File Extensions to Ignore
        ignore_tab = QWidget()
        ignore_layout = QVBoxLayout(ignore_tab)

        form_layout = QFormLayout()
        form_layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapLongRows)

        self.txt_ignore_types = QLineEdit()
        self.txt_ignore_types.setToolTip("Comma-separated list of file extensions to skip (e.g., md5, sha1, log, bak, *.tmp)")
        form_layout.addRow("Ignored Extensions / Types:", self.txt_ignore_types)

        self.txt_ignore_files = QLineEdit()
        self.txt_ignore_files.setToolTip("Comma-separated list of specific file names or wildcard patterns to skip")
        form_layout.addRow("Ignored File Names:", self.txt_ignore_files)

        self.txt_ignore_folders = QLineEdit()
        self.txt_ignore_folders.setToolTip("Comma-separated list of folder names or wildcard patterns to skip")
        form_layout.addRow("Ignored Folder Names:", self.txt_ignore_folders)

        ignore_layout.addLayout(form_layout)

        lbl_hint = QLabel("<small><i>Values are comma-separated and support wildcards (e.g., *.tmp, thumbs.*, etc.).</i></small>")
        lbl_hint.setStyleSheet("color: #888888;")
        ignore_layout.addWidget(lbl_hint)

        btn_defaults = QPushButton("Restore Defaults")
        btn_defaults.setFixedWidth(130)
        btn_defaults.clicked.connect(self.restore_defaults)
        ignore_layout.addWidget(btn_defaults, alignment=Qt.AlignmentFlag.AlignLeft)
        ignore_layout.addStretch()

        self.tabs.addTab(ignore_tab, "File Extensions to Ignore")

        # Tab 2: Options
        options_tab = QWidget()
        options_layout = QVBoxLayout(options_tab)
        self.chk_disable_sound = QCheckBox("Disable Notification Sounds")
        self.chk_disable_sound.setToolTip("Mutes all audio chimes and notification sounds for completion alerts.")
        options_layout.addWidget(self.chk_disable_sound)
        options_layout.addStretch()

        self.tabs.addTab(options_tab, "Options")
        main_layout.addWidget(self.tabs)

        # Dialog Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.save_and_close)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)

        self.load_values()

    def load_values(self):
        if self.parent_app and hasattr(self.parent_app, 'settings'):
            s = self.parent_app.settings
            self.txt_ignore_types.setText(s.value("ignore_types", DEFAULT_IGNORE_TYPES))
            self.txt_ignore_files.setText(s.value("ignore_files", DEFAULT_IGNORE_FILES))
            self.txt_ignore_folders.setText(s.value("ignore_folders", DEFAULT_IGNORE_FOLDERS))
            self.chk_disable_sound.setChecked(s.value("disable_notification_sounds", False))

    def restore_defaults(self):
        self.txt_ignore_types.setText(DEFAULT_IGNORE_TYPES)
        self.txt_ignore_files.setText(DEFAULT_IGNORE_FILES)
        self.txt_ignore_folders.setText(DEFAULT_IGNORE_FOLDERS)

    def save_and_close(self):
        if self.parent_app and hasattr(self.parent_app, 'settings'):
            s = self.parent_app.settings
            s.setValue("ignore_types", self.txt_ignore_types.text().strip())
            s.setValue("ignore_files", self.txt_ignore_files.text().strip())
            s.setValue("ignore_folders", self.txt_ignore_folders.text().strip())
            s.setValue("disable_notification_sounds", self.chk_disable_sound.isChecked())
        self.accept()


class HashWorker(QThread):
    progress = pyqtSignal(int, int, str)
    verification_progress = pyqtSignal(str)
    finished = pyqtSignal(dict)
    verification_finished = pyqtSignal(dict)
    
    def __init__(self, targets, algorithm, dist_subfolders, delete_subhashes=False, delete_primary_hash=False,
                 ignore_types="", ignore_files="", ignore_folders=""):
        super().__init__()
        if isinstance(targets, str):
            self.targets = [os.path.normpath(targets)]
        else:
            self.targets = [os.path.normpath(t) for t in targets]
        self.target_dir = self.targets[0] if self.targets else ""
        self.algorithm = algorithm
        self.dist_subfolders = dist_subfolders
        self.delete_subhashes = delete_subhashes
        self.delete_primary_hash = delete_primary_hash
        self.ignore_types = ignore_types
        self.ignore_files = ignore_files
        self.ignore_folders = ignore_folders
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True
        
    def run(self):
        all_targets_data = {}
        total_files_to_hash = []

        for target in self.targets:
            if not os.path.exists(target):
                continue

            if os.path.isdir(target):
                target_dir = target
                root_folder_name = os.path.basename(target_dir)
                master_hash_path = os.path.join(target_dir, f"{root_folder_name}.hash")

                # Clean existing primary/master .hash file if requested
                if self.delete_primary_hash and os.path.exists(master_hash_path):
                    try:
                        os.remove(master_hash_path)
                    except Exception as e:
                        print(f"Error removing primary hash: {e}")

                # Clean existing subdirectory checksum files if requested
                if self.delete_subhashes:
                    for root, dirs, files in os.walk(target_dir):
                        dirs[:] = [d for d in dirs if not is_ignored(d, is_dir=True, ignore_folders=self.ignore_folders)]
                        if os.path.normpath(root) == target_dir:
                            continue
                        for f in files:
                            if f.lower().endswith(CHECKSUM_EXTS):
                                try:
                                    os.remove(os.path.join(root, f))
                                except Exception as e:
                                    print(f"Error removing subfolder checksum file {f}: {e}")

                existing_entries = set()
                all_known_hashes = {}
                if os.path.exists(master_hash_path):
                    try:
                        with open(master_hash_path, 'r', encoding='utf-8') as f:
                            for line in f:
                                line = line.strip()
                                if line and not line.startswith('#'):
                                    parts = line.split(maxsplit=1)
                                    if len(parts) == 2:
                                        h_val = parts[0].strip()
                                        rel_p = os.path.normpath(parts[1].lstrip('*').strip())
                                        existing_entries.add(rel_p)
                                        all_known_hashes[rel_p] = h_val
                    except Exception as e:
                        print(f"Error reading existing master hash: {e}")

                target_new_files = []
                for root, dirs, files in os.walk(target_dir):
                    dirs[:] = [d for d in dirs if not is_ignored(d, is_dir=True, ignore_folders=self.ignore_folders)]
                    for f in files:
                        if not f.lower().endswith(CHECKSUM_EXTS) and not is_ignored(
                            f, is_dir=False, ignore_types=self.ignore_types, ignore_files=self.ignore_files
                        ):
                            f_path = os.path.join(root, f)
                            rel_p = os.path.normpath(os.path.relpath(f_path, target_dir))
                            if rel_p not in existing_entries:
                                target_new_files.append((f_path, rel_p))
                                total_files_to_hash.append((target_dir, f_path, rel_p))

                all_targets_data[target_dir] = {
                    "is_dir": True,
                    "known": all_known_hashes,
                    "results": dict(all_known_hashes),
                    "new_count": len(target_new_files)
                }
            else:
                f_path = target
                target_dir = os.path.dirname(f_path)
                rel_p = os.path.basename(f_path)
                total_files_to_hash.append((target_dir, f_path, rel_p))
                all_targets_data.setdefault(target_dir, {
                    "is_dir": False,
                    "known": {},
                    "results": {},
                    "new_count": 0
                })
                all_targets_data[target_dir]["new_count"] += 1

        total_files = len(total_files_to_hash)

        for idx, (target_dir, file_path, rel_path) in enumerate(total_files_to_hash, 1):
            if self._is_cancelled:
                return
            self.progress.emit(idx, total_files, file_path)

            try:
                if self.algorithm == "SFV / CRC32":
                    crc_val = 0
                    with open(file_path, 'rb') as f:
                        while chunk := f.read(65536):
                            crc_val = zlib.crc32(chunk, crc_val)
                    digest = f"{crc_val & 0xFFFFFFFF:08x}"
                else:
                    if self.algorithm == "BLAKE3":
                        hasher = blake3.blake3() if HAS_BLAKE3 else hashlib.blake2b()
                    elif self.algorithm in ("BLAKE2", "BLAKE2b"):
                        hasher = hashlib.blake2b()
                    elif self.algorithm == "BLAKE2s":
                        hasher = hashlib.blake2s()
                    elif self.algorithm == "SHA-512":
                        hasher = hashlib.sha512()
                    elif self.algorithm == "SHA-256":
                        hasher = hashlib.sha256()
                    elif self.algorithm == "SHA-3":
                        hasher = hashlib.sha3_256()
                    elif self.algorithm == "xx3":
                        hasher = xxhash.xxh3_64() if HAS_XXHASH else hashlib.blake2b()
                    elif self.algorithm == "SHA-1":
                        hasher = hashlib.sha1()
                    elif self.algorithm == "MD5":
                        hasher = hashlib.md5()
                    else:
                        hasher = hashlib.blake2b()

                    with open(file_path, 'rb') as f:
                        while chunk := f.read(65536):
                            hasher.update(chunk)
                    digest = hasher.hexdigest()

                all_targets_data[target_dir]["results"][rel_path] = digest
            except Exception as e:
                print(f"Error hashing {file_path}: {e}")

        self.finished.emit(all_targets_data)

    def verify_hash_files(self, hash_file_paths):
        import time

        verification_results = {
            "total_checked": 0,
            "passed": 0,
            "failed": [],
            "missing": []
        }

        items_to_verify = []
        total_verify_bytes = 0

        for hash_file in hash_file_paths:
            base_dir = os.path.dirname(hash_file)
            ext = os.path.splitext(hash_file)[1].lower()
            if ext in (".sha3", ".sha3-256", ".sha3-512"):
                file_algo = "SHA-3"
            elif ext == ".sha256":
                file_algo = "SHA-256"
            elif ext == ".sha512":
                file_algo = "SHA-512"
            elif ext == ".md5":
                file_algo = "MD5"
            elif ext in (".sha1", ".sha"):
                file_algo = "SHA-1"
            elif ext in (".sfv", ".crc32", ".crc"):
                file_algo = "SFV / CRC32"
            elif ext in (".xx3", ".xxh3", ".xxh"):
                file_algo = "xx3"
            elif ext in (".b2", ".blake2", ".blake2b"):
                file_algo = "BLAKE2b"
            elif ext == ".blake2s":
                file_algo = "BLAKE2s"
            else:
                file_algo = "BLAKE3"

            try:
                with open(hash_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
            except Exception as e:
                print(f"Error reading hash file {hash_file}: {e}")
                continue

            current_algo = file_algo
            for line in lines:
                line_str = line.strip()
                line_lower = line_str.lower()

                # Detect algorithm declarations and Corz Checksum headers
                if line_lower.startswith("# algorithm:") or line_lower.startswith("; algorithm:"):
                    current_algo = line_str.split(":", 1)[1].strip()
                    continue
                if "blake2" in line_lower:
                    current_algo = "BLAKE2s"
                    if line_str.startswith('#') or line_str.startswith(';'):
                        continue
                if "made with checksum" in line_lower:
                    if current_algo == "BLAKE3":
                        current_algo = "BLAKE2s"
                    continue
                if not line_str or line_str.startswith('#') or line_str.startswith(';'):
                    continue

                tokens = line_str.split()
                if len(tokens) >= 2:
                    first_tok = tokens[0].strip()
                    last_tok = tokens[-1].strip()
                    is_hex = lambda s: all(c in '0123456789abcdefABCDEF' for c in s)

                    if len(first_tok) in (8, 16, 32, 40, 64, 128) and is_hex(first_tok):
                        expected_hash = first_tok
                        rel_path = line_str.split(maxsplit=1)[1].lstrip('*').strip()
                    elif len(last_tok) == 8 and is_hex(last_tok):
                        expected_hash = last_tok
                        rel_path = line_str.rsplit(maxsplit=1)[0].lstrip('*').strip()
                    else:
                        continue

                    full_path = os.path.join(base_dir, rel_path)
                    f_size = os.path.getsize(full_path) if os.path.isfile(full_path) else 0
                    total_verify_bytes += f_size
                    items_to_verify.append((hash_file, base_dir, rel_path, full_path, expected_hash, current_algo, f_size))

        start_time = time.time()
        bytes_hashed = 0
        last_emit_time = 0

        for hash_file, base_dir, rel_path, full_path, expected_hash, current_algo, f_size in items_to_verify:
            if self._is_cancelled:
                return

            self.verification_progress.emit(rel_path)
            verification_results["total_checked"] += 1

            if not os.path.exists(full_path):
                verification_results["missing"].append((rel_path, hash_file))
                continue

            h_len = len(expected_hash)
            algo = current_algo
            if h_len == 8:
                algo = "SFV / CRC32"
            elif h_len == 16:
                algo = "xx3"
            elif h_len == 32:
                algo = "MD5"
            elif h_len == 40:
                algo = "SHA-1"
            elif h_len == 64:
                algo_u = current_algo.upper()
                if not any(k in algo_u for k in ["BLAKE3", "256", "BLAKE2S", "SHA-3", "SHA3"]):
                    algo = "BLAKE3"
            elif h_len == 128:
                algo_u = current_algo.upper()
                if not any(k in algo_u for k in ["BLAKE2", "512"]):
                    algo = "BLAKE2b"

            def _emit_stream(b_done, b_tot, el_sec, eta_s, r_path):
                if sys.stdout is not None:
                    try:
                        sys.stdout.write(f"VERIFY_PROGRESS:{b_done}:{b_tot}:{el_sec}:{eta_s}:{r_path}\n")
                        sys.stdout.flush()
                    except Exception:
                        pass

            try:
                algo_upper = algo.upper()
                if "CRC" in algo_upper or "SFV" in algo_upper:
                    crc_val = 0
                    with open(full_path, 'rb') as vf:
                        while chunk := vf.read(65536):
                            crc_val = zlib.crc32(chunk, crc_val)
                            bytes_hashed += len(chunk)
                            now = time.time()
                            if now - last_emit_time >= 0.25:
                                elapsed = max(1, int(now - start_time))
                                speed = bytes_hashed / elapsed
                                eta = int((total_verify_bytes - bytes_hashed) / speed) if speed > 0 and total_verify_bytes > bytes_hashed else 0
                                _emit_stream(bytes_hashed, total_verify_bytes, elapsed, eta, rel_path)
                                last_emit_time = now
                    calculated_hash = f"{crc_val & 0xFFFFFFFF:08x}"
                else:
                    if "BLAKE3" in algo_upper and HAS_BLAKE3:
                        hasher = blake3.blake3()
                    elif "BLAKE2S" in algo_upper:
                        hasher = hashlib.blake2s()
                    elif "BLAKE2" in algo_upper:
                        hasher = hashlib.blake2b()
                    elif "512" in algo_upper and "SHA" in algo_upper:
                        hasher = hashlib.sha512()
                    elif "SHA-3" in algo_upper or "SHA3" in algo_upper:
                        hasher = hashlib.sha3_256()
                    elif "256" in algo_upper and "SHA" in algo_upper:
                        hasher = hashlib.sha256()
                    elif ("XX3" in algo_upper or "XXH3" in algo_upper) and HAS_XXHASH:
                        hasher = xxhash.xxh3_64()
                    elif "SHA-1" in algo_upper or "SHA1" in algo_upper:
                        hasher = hashlib.sha1()
                    elif "MD5" in algo_upper:
                        hasher = hashlib.md5()
                    else:
                        hasher = hashlib.blake2b()

                    with open(full_path, 'rb') as vf:
                        while chunk := vf.read(65536):
                            hasher.update(chunk)
                            bytes_hashed += len(chunk)
                            now = time.time()
                            if now - last_emit_time >= 0.25:
                                elapsed = max(1, int(now - start_time))
                                speed = bytes_hashed / elapsed
                                eta = int((total_verify_bytes - bytes_hashed) / speed) if speed > 0 and total_verify_bytes > bytes_hashed else 0
                                _emit_stream(bytes_hashed, total_verify_bytes, elapsed, eta, rel_path)
                                last_emit_time = now
                    calculated_hash = hasher.hexdigest()

                if calculated_hash.lower() == expected_hash.lower():
                    verification_results["passed"] += 1
                else:
                    verification_results["failed"].append((rel_path, expected_hash, calculated_hash, hash_file))
            except Exception as e:
                verification_results["failed"].append((rel_path, expected_hash, str(e), hash_file))

        elapsed_total = max(1, int(time.time() - start_time))
        if sys.stdout is not None:
            try:
                sys.stdout.write(f"VERIFY_PROGRESS:{total_verify_bytes}:{total_verify_bytes}:{elapsed_total}:0:Done\n")
                sys.stdout.flush()
            except Exception:
                pass
        self.verification_finished.emit(verification_results)


class VerificationOSD(QWidget):
    def __init__(self, hash_files, parent_app):
        super().__init__()
        self.hash_files = hash_files
        self.parent_app = parent_app
        
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(6)

        script_dir = os.path.dirname(os.path.realpath(__file__))
        icon_path = os.path.join(script_dir, "KryptDist_internal", "icons", "KryptDist_ghost_icon.svg")
        if os.path.exists(icon_path):
            lbl_icon = QLabel()
            lbl_icon.setStyleSheet("background: transparent; border: none; padding: 0px;")
            pixmap = QIcon(icon_path).pixmap(16, 16)
            lbl_icon.setPixmap(pixmap)
            lbl_icon.setFixedSize(16, 16)
            layout.addWidget(lbl_icon)
        
        theme = "System"
        if self.parent_app and hasattr(self.parent_app, 'current_theme'):
            theme = self.parent_app.current_theme
        elif self.parent_app and hasattr(self.parent_app, 'settings'):
            theme = self.parent_app.settings.value("theme", "System")

        if theme == "System":
            app = QApplication.instance()
            is_dark = app.style().standardPalette().color(QPalette.ColorRole.Window).lightness() < 128 if app else True
            effective_theme = "Dark" if is_dark else "Light"
        else:
            effective_theme = theme

        if effective_theme == "Light":
            bg_color = "#f0f0f0"
            border_color = "#0078d7"
            text_color = "#000000"
        else:
            bg_color = "#1e1e1e"
            border_color = "#007acc"
            text_color = "#ffffff"

        self.lbl_file = QLabel("Initializing...")
        self.lbl_file.setStyleSheet(f"font-size: 11px; color: {text_color};")
        self.lbl_file.setFixedWidth(380)
        self.lbl_file.setWordWrap(False)
        layout.addWidget(self.lbl_file)
        
        self.setLayout(layout)
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {bg_color};
                border: 2px solid {border_color};
                border-radius: 4px;
                padding: 2px;
            }}
        """)
        self.adjustSize()
        
        # Fully opaque (0% transparent)
        self.setWindowOpacity(1.0)

        # Position at saved coordinates or Top-Left Corner of primary screen
        saved_x = self.parent_app.settings.value("osd_x", None) if (self.parent_app and hasattr(self.parent_app, 'settings')) else None
        saved_y = self.parent_app.settings.value("osd_y", None) if (self.parent_app and hasattr(self.parent_app, 'settings')) else None
        
        if saved_x is not None and saved_y is not None:
            self.move(saved_x, saved_y)
        else:
            screen = QApplication.primaryScreen().availableGeometry()
            self.move(screen.left() + 20, screen.top() + 20)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and hasattr(self, '_drag_pos'):
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = self.pos()
            if self.parent_app and hasattr(self.parent_app, 'settings'):
                self.parent_app.settings.setValue("osd_x", pos.x())
                self.parent_app.settings.setValue("osd_y", pos.y())
            event.accept()
        
    def update_file(self, rel_path):
        metrics = self.lbl_file.fontMetrics()
        elided = metrics.elidedText(f"Checking: {rel_path}", Qt.TextElideMode.ElideMiddle, 360)
        self.lbl_file.setText(elided)

    def trigger_error_flash(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #3b0000;
                border: 2px solid #ff3333;
                border-radius: 4px;
                padding: 2px;
            }
        """)
        self.lbl_file.setStyleSheet("font-size: 11px; font-weight: bold; color: #ff3333;")
        self.lbl_file.setText("KryptDist | CORRUPTION DETECTED!")


class DropTreeWidget(QTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHeaderHidden(True)
        self.setAcceptDrops(True)
        self.setRootIsDecorated(True)
        self.setWordWrap(True)
        self.header().setStretchLastSection(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            all_paths = self.get_all_paths()
            for url in event.mimeData().urls():
                file_path = os.path.normpath(url.toLocalFile()).replace('/', os.sep)
                if file_path and os.path.exists(file_path):
                    if file_path.lower().endswith(CHECKSUM_EXTS):
                        continue
                    if file_path not in all_paths:
                        all_paths.append(file_path)
            all_paths.sort(key=natural_sort_key)
            self.set_paths(all_paths)
            event.acceptProposedAction()
        else:
            event.ignore()

    def get_all_paths(self):
        paths = []
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            path = item.data(0, Qt.ItemDataRole.UserRole)
            if path:
                paths.append(path)
        return paths

    def set_paths(self, paths):
        self.clear()
        for p in paths:
            self.add_path(p)

    def add_path(self, path):
        clean_p = os.path.normpath(os.path.abspath(path)).replace('/', os.sep)
        existing = self.get_all_paths()
        if clean_p in existing:
            return
        name = os.path.basename(clean_p) or clean_p
        parent_item = QTreeWidgetItem(self, [name])
        parent_item.setData(0, Qt.ItemDataRole.UserRole, clean_p)
        parent_item.setToolTip(0, clean_p)
        child_item = QTreeWidgetItem(parent_item, [""])
        child_item.setData(0, Qt.ItemDataRole.UserRole, clean_p)

        path_label = QLabel(clean_p)
        path_label.setWordWrap(True)
        path_label.setStyleSheet("background: transparent;")
        self.setItemWidget(child_item, 0, path_label)


class KryptDistApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"KryptDist v{APP_VERSION}")
        
        script_dir = os.path.dirname(os.path.realpath(__file__))
        internal_dir = os.path.join(script_dir, "KryptDist_internal")
        os.makedirs(internal_dir, exist_ok=True)
        self.config_file = os.path.join(internal_dir, "KryptDist.config.json")
        
        icon_path = os.path.join(internal_dir, "icons", "KryptDist_ghost_icon.svg")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
            
        if sys.platform == "win32":
            myappid = f"pwshAgyjkcrg761.kryptdist.{APP_VERSION}"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
            
        self.default_size = (600, 380)
        self.settings = SettingsWrapper(self.config_file)
        self.load_geometry()
        
        self.current_theme = self.settings.value("theme", "System")
        self.apply_theme(self.current_theme)
        self.last_directory = os.path.normpath(self.settings.value("last_directory", os.getcwd()))
        
        self.is_headless = any(arg.lower() in ("-headless", "--headless", "/headless") for arg in sys.argv)

        # Parse command line inputs (e.g. from SendTo or file drag onto script)
        self.target_paths = []
        if len(sys.argv) > 1:
            for arg in sys.argv[1:]:
                clean_arg = arg.strip('"\'')
                if clean_arg.startswith("-") or clean_arg.startswith("/"):
                    continue
                clean_p = os.path.abspath(clean_arg)
                if os.path.exists(clean_p) and clean_p not in self.target_paths:
                    self.target_paths.append(clean_p)

        self.target_paths.sort(key=natural_sort_key)

        self.init_ui()
        self.load_saved_settings()

        # Check if any checksum files were passed via arguments (e.g. SendTo)
        self.hash_files_passed = [p for p in self.target_paths if p.lower().endswith(CHECKSUM_EXTS)]
        if self.hash_files_passed:
            self.start_direct_verification(self.hash_files_passed)

    def init_ui(self):
        self.create_menu()
        layout = QVBoxLayout()
        
        # Target Paths List
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("Target Files & Folders:"))
        header_layout.addStretch()
        self.btn_toggle_targets = QPushButton("▶")
        self.btn_toggle_targets.setToolTip("Expand/Collapse All Target Paths")
        self.btn_toggle_targets.setFlat(True)
        self.btn_toggle_targets.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_toggle_targets.setFixedSize(24, 20)
        self.btn_toggle_targets.setStyleSheet("QPushButton { border: none; font-size: 11px; color: palette(text); padding: 0px; } QPushButton:hover { color: #007acc; }")
        self.btn_toggle_targets.clicked.connect(self.toggle_all_targets)
        header_layout.addWidget(self.btn_toggle_targets)
        layout.addLayout(header_layout)

        self.path_list = DropTreeWidget()
        if self.target_paths:
            self.path_list.set_paths(self.target_paths)
        layout.addWidget(self.path_list)

        # Path Control Buttons
        btn_layout = QHBoxLayout()
        self.btn_add_dir = QPushButton("Add Folder")
        self.btn_add_dir.clicked.connect(self.add_directory)
        btn_layout.addWidget(self.btn_add_dir)

        self.btn_add_files = QPushButton("Add Files")
        self.btn_add_files.clicked.connect(self.add_files)
        btn_layout.addWidget(self.btn_add_files)

        self.btn_remove = QPushButton("Remove Selected")
        self.btn_remove.clicked.connect(self.remove_selected_path)
        btn_layout.addWidget(self.btn_remove)

        self.btn_clear = QPushButton("Clear")
        self.btn_clear.clicked.connect(self.clear_paths)
        btn_layout.addWidget(self.btn_clear)
        layout.addLayout(btn_layout)
        
        # Algorithm Configuration
        algo_layout = QHBoxLayout()
        algo_label = QLabel("Hash Algorithm:")
        self.combo_algo = QComboBox()
        
        algo_items = [
            ("Cryptographic Algorithms", False),
            ("BLAKE3", True),
            ("BLAKE2", True),
            ("SHA-512", True),
            ("SHA-256", True),
            ("SHA-3", True),
            ("Fast Checksum / Legacy Algorithms", False),
            ("xx3", True),
            ("SHA-1", True),
            ("MD5", True),
            ("SFV / CRC32", True)
        ]
        for text, enabled in algo_items:
            self.combo_algo.addItem(text)
            if not enabled:
                item_model = self.combo_algo.model().item(self.combo_algo.count() - 1)
                item_model.setEnabled(False)

        self.combo_algo.setCurrentText("BLAKE3")
        algo_layout.addWidget(algo_label)
        algo_layout.addWidget(self.combo_algo)
        layout.addLayout(algo_layout)
        
        # Options
        options_row1 = QHBoxLayout()
        self.lbl_mode = QLabel("Mode: MultiHash")
        self.lbl_mode.setStyleSheet("font-weight: bold; color: #007acc;")
        options_row1.addWidget(self.lbl_mode)

        self.check_delete_primary = QCheckBox("Delete Primary Hashes First")
        self.check_delete_primary.setToolTip("Removes existing root master .hash file before scanning and hashing.")
        options_row1.addWidget(self.check_delete_primary)
        layout.addLayout(options_row1)

        options_row2 = QHBoxLayout()
        self.check_subfolders = QCheckBox("Distribute Hashes to Subdirectories")
        self.check_subfolders.setToolTip("Creates individual .hash files inside subdirectories in addition to the root .hash file.")
        self.check_subfolders.toggled.connect(self.update_mode_indicator)
        options_row2.addWidget(self.check_subfolders)

        self.check_delete_subhashes = QCheckBox("Delete Existing Subdirectory Hashes First")
        self.check_delete_subhashes.setToolTip("Removes all existing .hash files in subdirectories before scanning and hashing.")
        options_row2.addWidget(self.check_delete_subhashes)
        layout.addLayout(options_row2)

        # Progress Section
        self.status_tree = QTreeWidget()
        self.status_tree.setHeaderHidden(True)
        self.status_tree.setRootIsDecorated(True)
        self.status_tree.header().setStretchLastSection(True)
        self.status_tree.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.status_tree.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.status_tree.setAutoScroll(False)
        self.status_tree.setFixedHeight(75)
        self.status_tree_root = QTreeWidgetItem(self.status_tree, ["Status: Ready"])
        self.status_tree_path = QTreeWidgetItem(self.status_tree_root, [""])
        self.status_path_label = QLabel("")
        self.status_path_label.setWordWrap(True)
        self.status_path_label.setMinimumHeight(36)
        self.status_path_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.status_path_label.setStyleSheet("background: transparent;")
        self.status_tree.setItemWidget(self.status_tree_path, 0, self.status_path_label)
        layout.addWidget(self.status_tree)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        # Action Buttons
        self.btn_run = QPushButton("Generate Hashes")
        self.btn_run.clicked.connect(self.handle_run_or_cancel)
        layout.addWidget(self.btn_run)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def load_saved_settings(self):
        if os.path.exists(self.config_file):
            try:
                self.check_delete_primary.setChecked(self.settings.value("delete_primary_hash", False))
                self.check_subfolders.setChecked(self.settings.value("distribute_subfolders", True))
                self.check_delete_subhashes.setChecked(self.settings.value("delete_subhashes", False))
                saved_algo = self.settings.value("algorithm", "BLAKE3")
                idx = self.combo_algo.findText(saved_algo)
                if idx >= 0:
                    self.combo_algo.setCurrentIndex(idx)
                if hasattr(self, 'status_tree_root'):
                    self.status_tree_root.setExpanded(self.settings.value("progress_expanded", False))
                    self.status_tree.scheduleDelayedItemsLayout()
                if hasattr(self, 'btn_toggle_targets'):
                    targets_expanded = self.settings.value("targets_expanded", False)
                    self.btn_toggle_targets.setText("▼" if targets_expanded else "▶")
                    if targets_expanded:
                        self.path_list.expandAll()
                    else:
                        self.path_list.collapseAll()
            except Exception as e:
                print(f"Error loading saved settings: {e}")
        self.update_mode_indicator()

    def load_geometry(self):
        self.resize(*self.default_size)
        if os.path.exists(self.config_file):
            try:
                if "x" in self.settings.data and "y" in self.settings.data:
                    self.move(self.settings.value("x", 100), self.settings.value("y", 100))
                else:
                    self.center_window()
                self.resize(self.settings.value("width", self.default_size[0]),
                            self.settings.value("height", self.default_size[1]))
            except Exception as e:
                print(f"Error loading geometry: {e}")
                self.center_window()
        else:
            self.center_window()

    def center_window(self):
        frame_geo = self.frameGeometry()
        screen = QApplication.primaryScreen().availableGeometry().center()
        frame_geo.moveCenter(screen)
        self.move(frame_geo.topLeft())

    def closeEvent(self, event):
        pos = self.pos()
        self.settings.setValue("x", pos.x())
        self.settings.setValue("y", pos.y())
        self.settings.setValue("width", self.width())
        self.settings.setValue("height", self.height())
        self.settings.setValue("delete_primary_hash", self.check_delete_primary.isChecked())
        self.settings.setValue("distribute_subfolders", self.check_subfolders.isChecked())
        self.settings.setValue("delete_subhashes", self.check_delete_subhashes.isChecked())
        self.settings.setValue("algorithm", self.combo_algo.currentText())
        self.settings.setValue("theme", self.current_theme)
        if hasattr(self, 'status_tree_root'):
            self.settings.setValue("progress_expanded", self.status_tree_root.isExpanded())
        if hasattr(self, 'btn_toggle_targets'):
            self.settings.setValue("targets_expanded", self.btn_toggle_targets.text() == "▼")
        event.accept()

    def toggle_all_targets(self):
        is_expanded = self.btn_toggle_targets.text() == "▼"
        if is_expanded:
            self.path_list.collapseAll()
            self.btn_toggle_targets.setText("▶")
        else:
            self.path_list.expandAll()
            self.btn_toggle_targets.setText("▼")

    def add_directory(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Directory", self.last_directory)
        if dir_path:
            clean_p = os.path.normpath(dir_path).replace('/', os.sep)
            self.last_directory = clean_p
            self.settings.setValue("last_directory", self.last_directory)
            self.path_list.add_path(clean_p)
            if self.btn_toggle_targets.text() == "▼":
                self.path_list.expandAll()

    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Files", self.last_directory)
        if files:
            self.last_directory = os.path.normpath(os.path.dirname(files[0])).replace('/', os.sep)
            self.settings.setValue("last_directory", self.last_directory)
            files.sort(key=natural_sort_key)
            for f in files:
                clean_p = os.path.normpath(f).replace('/', os.sep)
                if not clean_p.lower().endswith(CHECKSUM_EXTS):
                    self.path_list.add_path(clean_p)

    def remove_selected_path(self):
        for item in self.path_list.selectedItems():
            parent = item.parent()
            target_item = parent if parent is not None else item
            index = self.path_list.indexOfTopLevelItem(target_item)
            if index >= 0:
                self.path_list.takeTopLevelItem(index)

    def clear_paths(self):
        self.path_list.clear()

    def update_mode_indicator(self):
        if hasattr(self, 'check_subfolders') and hasattr(self, 'lbl_mode'):
            if self.check_subfolders.isChecked():
                self.lbl_mode.setText("Mode: MultiHash")
            else:
                self.lbl_mode.setText("Mode: Primary Hash Only")

    def create_menu(self):
        menu_bar = self.menuBar()
        
        file_menu = menu_bar.addMenu("&File")
        exit_action = file_menu.addAction("Exit")
        exit_action.triggered.connect(self.close)
        
        tools_menu = menu_bar.addMenu("&Tools")
        themes_menu = tools_menu.addMenu("&Themes")
        
        self.theme_group = QActionGroup(self)
        self.theme_group.setExclusive(True)
        
        for theme in ["Dark", "Light", "System"]:
            action = themes_menu.addAction(theme)
            action.setCheckable(True)
            self.theme_group.addAction(action)
            action.triggered.connect(lambda checked, t=theme: self.change_theme(t))
            
        saved_theme = self.settings.value("theme", "System")
        for action in self.theme_group.actions():
            if action.text() == saved_theme:
                action.setChecked(True)
        
        tools_menu.addSeparator()
        pref_action = tools_menu.addAction("&Preferences")
        pref_action.triggered.connect(self.show_preferences)

        help_menu = menu_bar.addMenu("&Help")
        manual_action = help_menu.addAction("Manual")
        manual_action.triggered.connect(self.show_manual)
        about_action = help_menu.addAction("About")
        about_action.triggered.connect(self.show_about)

    def show_preferences(self):
        dialog = PreferencesDialog(self)
        dialog.exec()

    def apply_theme(self, theme_name):
        app = QApplication.instance()
        app.setStyle("Fusion")
        
        if theme_name == "System":
            is_dark = app.style().standardPalette().color(QPalette.ColorRole.Window).lightness() < 128
            effective_theme = "Dark" if is_dark else "Light"
        else:
            effective_theme = theme_name

        palette = QPalette(app.style().standardPalette())
        
        if effective_theme == "Dark":
            text_color = "#ffffff"
            palette.setColor(QPalette.ColorRole.Window, QColor("#1e1e1e"))
            palette.setColor(QPalette.ColorRole.WindowText, QColor("#ffffff"))
            palette.setColor(QPalette.ColorRole.Base, QColor("#2d2d2d"))
            palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#1e1e1e"))
            palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#252526"))
            palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#ffffff"))
            palette.setColor(QPalette.ColorRole.Text, QColor("#ffffff"))
            palette.setColor(QPalette.ColorRole.Button, QColor("#333333"))
            palette.setColor(QPalette.ColorRole.ButtonText, QColor("#ffffff"))
            palette.setColor(QPalette.ColorRole.PlaceholderText, QColor("#aaaaaa"))
            palette.setColor(QPalette.ColorRole.Highlight, QColor("#007acc"))
            palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
        else:
            text_color = "#000000"
            palette.setColor(QPalette.ColorRole.Window, QColor("#f0f0f0"))
            palette.setColor(QPalette.ColorRole.WindowText, QColor("#000000"))
            palette.setColor(QPalette.ColorRole.Base, QColor("#ffffff"))
            palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#fcfcfc"))
            palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#ffffff"))
            palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#000000"))
            palette.setColor(QPalette.ColorRole.Text, QColor("#000000"))
            palette.setColor(QPalette.ColorRole.Button, QColor("#e1e1e1"))
            palette.setColor(QPalette.ColorRole.ButtonText, QColor("#000000"))
            palette.setColor(QPalette.ColorRole.PlaceholderText, QColor("#777777"))
            palette.setColor(QPalette.ColorRole.Highlight, QColor("#0078d7"))
            palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
            
        app.setPalette(palette)
        app.setStyleSheet(f"QTreeWidget QLabel {{ color: {text_color}; background: transparent; }}")

    def change_theme(self, theme_name):
        self.current_theme = theme_name
        self.apply_theme(theme_name)

    def show_manual(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Manual")
        dialog.resize(650, 540)

        script_dir = os.path.dirname(os.path.realpath(__file__))
        icon_path = os.path.join(script_dir, "KryptDist_internal", "icons", "KryptDist_ghost_icon.svg")
        if os.path.exists(icon_path):
            dialog.setWindowIcon(QIcon(icon_path))

        layout = QVBoxLayout(dialog)

        text_browser = QTextBrowser()
        text_browser.setOpenExternalLinks(True)
        text_browser.setStyleSheet("""
            QTextBrowser {
                font-family: 'Segoe UI', sans-serif;
                font-size: 14px;
                line-height: 1.6;
                color: palette(text);
                background-color: palette(base);
                border: none;
                padding: 20px;
            }
            h1 { color: #007acc; font-size: 22px; margin-bottom: 0px; }
            h2 { color: #007acc; font-size: 18px; border-bottom: 1px solid #444; padding-bottom: 5px; margin-top: 25px; }
            b { color: #007acc; }
            code { font-family: 'Consolas', monospace; background-color: rgba(128, 128, 128, 0.2); padding: 2px 5px; }
        """)

        manual_text = (
            f"<h1>KryptDist v{APP_VERSION}</h1>"
            f"<p>MANUAL &amp; USAGE GUIDE | Copyright (C) 2026 pwshAgyjkcrg761</p><br>"
            f"<h2>OVERVIEW</h2>"
            f"<p>KryptDist is a high-performance checksum generator and integrity verifier designed to produce "
            f"primary and distributed subdirectory checksum sets (<code>.hash</code>).</p>"
            f"<h2>OPERATIONAL MODES &amp; BATCH HASHING</h2>"
            f"<ul>"
            f"<li><b>MultiHash Mode:</b> Generates both a root primary <code>.hash</code> file and individual "
            f"subdirectory hashes within every subfolder in a single scanning pass.</li>"
            f"<li><b>Primary Hash Only Mode:</b> Generates only the root directory's primary <code>.hash</code> file.</li>"
            f"<li><b>Batch Processing:</b> Add multiple folders and files simultaneously via Drag &amp; Drop or Windows <b>SendTo</b>. "
            f"KryptDist processes every root target independently in a single, unified queue.</li>"
            f"<li><b>Execution Control:</b> While generating hashes, the execution button transforms into a <b>Cancel</b> button "
            f"with confirmation, and input controls/options are safely locked until completion or cancellation.</li>"
            f"</ul>"
            f"<h2>HASHING OPTIONS</h2>"
            f"<ul>"
            f"<li><b>Incremental Smart Hashing:</b> KryptDist scans existing primary hash files and skips already verified files, "
            f"only hashing new files and appending them to the hash files.</li>"
            f"<li><b>Delete Primary Hashes First:</b> Deletes any existing root primary <code>.hash</code> file before generating new checksums.</li>"
            f"<li><b>Delete Subdirectory Hashes First:</b> Cleans out existing subhashes across all subfolders prior to generation.</li>"
            f"</ul>"
            f"<h2>PREFERENCES &amp; OPTIONS</h2>"
            f"<ul>"
            f"<li><b>Ignore Rules:</b> Configure ignored file extensions, specific file names, and directories under <b>Tools &gt; Preferences &gt; File Extensions to Ignore</b>.</li>"
            f"<li><b>Disable Notification Sounds:</b> Enable under <b>Tools &gt; Preferences &gt; Options</b> to mute completion and alert chimes while retaining visual badges.</li>"
            f"<li><b>Wildcard Support:</b> Patterns accept wildcards (e.g. <code>*.tmp</code>, <code>Thumbs.*</code>, <code>.Trash-*</code>) to cleanly exclude OS metadata, caches, and unwanted artifacts.</li>"
            f"<li><b>Defaults:</b> Preloaded with comprehensive exclusion sets for existing checksum manifests, system volumes, OS caches, and media companion files.</li>"
            f"</ul>"
            f"<h2>SUPPORTED ALGORITHMS</h2>"
            f"<ul>"
            f"<li><b>Cryptographic:</b> BLAKE3, BLAKE2 (2b/2s), SHA-512, SHA-256, SHA-3 (SHA3-256).</li>"
            f"<li><b>Fast Checksum &amp; Legacy:</b> xx3 (xxHash3), SHA-1, MD5, SFV / CRC32.</li>"
            f"</ul>"
            f"<h2>INTERFACE &amp; THEMES</h2>"
            f"<ul>"
            f"<li><b>Tree Navigation:</b> Target lists and progress indicators display clean file/folder names. Click individual disclosure triangles (<code>▶</code> / <code>▼</code>) to view complete, word-wrapped paths with zero horizontal scrolling.</li>"
            f"<li><b>Header Toggle:</b> Click the triangle icon on the far right of <b>Target Files &amp; Folders</b> to expand or collapse all target paths at once.</li>"
            f"<li><b>Persistent UI State:</b> Expanded/collapsed triangle states are remembered across restarts.</li>"
            f"<li><b>Themes:</b> Switch between Dark, Light, and System themes via <b>Tools &gt; Themes</b>. All views and the verification OSD adapt dynamically to the selected theme.</li>"
            f"</ul>"
            f"<h2>VERIFICATION &amp; OSD</h2>"
            f"<p>Pass checksum files via command line or Windows <b>SendTo</b> menu to trigger instant container verification. "
            f"A lightweight On-Screen Display (OSD) provides real-time progress. Completed checks present clear visual status badges "
            f"(green checkmark on success, red X on mismatch). If errors occur, users are prompted whether to generate and open an error log in <code>KryptDist_internal/logs/</code>.</p>"
            f"<h2>CLI &amp; HEADLESS INTEGRATION</h2>"
            f"<ul>"
            f"<li><b>Single-File Verification:</b> Invoke with <code>-v &lt;file&gt;</code> or <code>--verify-file &lt;file&gt;</code> "
            f"for instant, headless verification against local or parent hash containers.</li>"
            f"<li><b>Exit Codes:</b> Returns <code>0</code> when files match, or <code>2</code> on mismatch, missing files, or errors, "
            f"enabling seamless integration with external managers like HashMan.</li>"
            f"</ul>"
        )

        text_browser.setHtml(manual_text)
        layout.addWidget(text_browser)

        btn_close = QPushButton("Close")
        btn_close.clicked.connect(dialog.accept)
        layout.addWidget(btn_close, alignment=Qt.AlignmentFlag.AlignRight)

        dialog.exec()

    def show_about(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("About")
        dialog.resize(500, 350)
        
        layout = QVBoxLayout(dialog)
        text_browser = QTextBrowser()
        text_browser.setOpenExternalLinks(True)
        text_browser.setStyleSheet("""
            QTextBrowser {
                font-family: 'Segoe UI', sans-serif;
                font-size: 13px;
                color: palette(text);
                background-color: palette(base);
                border: none;
                padding: 10px;
            }
            h1 { color: #007acc; font-size: 20px; }
            b { color: #007acc; }
        """)
        
        about_text = (
            f"<h1><a href=\"https://git.disroot.org/pwshAgyjkcrg761/KryptDist-py\">KryptDist</a> v{APP_VERSION}</h1>"
            "<p>Copyright (C) 2026 <b>pwshAgyjkcrg761</b><br>"
            "Licensed under <b>GPLv3</b></p>"
            "<p>A high-performance checksum generator and distributor supporting BLAKE2, BLAKE3, and primary and subdirectory hashes.</p>"
            "<p>Official License: <a href=\"https://www.gnu.org/licenses/gpl-3.0.html\">gnu.org/licenses/gpl-3.0.html</a></p>"
            "<hr>"
            "<p>Icon Credits:<br>"
            "'Ghost SVG Vector' by <a href=\"https://www.svgrepo.com/svg/54269/ghost\">SVGRepo</a>.<br>"
            "Used under CC0 License. Modified by pwshAgyjkcrg761.</p>"
        )
        text_browser.setHtml(about_text)
        layout.addWidget(text_browser)
        
        btn_ok = QPushButton("OK")
        btn_ok.clicked.connect(dialog.accept)
        layout.addWidget(btn_ok, alignment=Qt.AlignmentFlag.AlignRight)
        
        dialog.exec()

    def start_direct_verification(self, hash_files):
        self.osd = VerificationOSD(hash_files, self)
        self.osd.show()

        base_dir = os.path.dirname(hash_files[0]) if hash_files else os.getcwd()
        self.worker = HashWorker(base_dir, "BLAKE3", False, False)
        self.worker.verification_progress.connect(self.osd.update_file)
        self.worker.verification_finished.connect(self.handle_verification_finished)
        
        # Execute worker verification in thread
        self.worker.run = lambda: self.worker.verify_hash_files(hash_files)
        self.worker.start()

    def handle_verification_finished(self, results):
        has_failed = len(results["failed"]) > 0
        has_missing = len(results["missing"]) > 0

        script_dir = os.path.dirname(os.path.realpath(__file__))
        internal_dir = os.path.join(script_dir, "KryptDist_internal")
        icon_path = os.path.join(internal_dir, "icons", "KryptDist_ghost_icon.svg")

        if has_failed or has_missing:
            self.osd.trigger_error_flash()
            QApplication.processEvents()
            self.osd.close()

            if getattr(self, 'is_headless', False):
                logs_dir = os.path.join(internal_dir, "logs")
                os.makedirs(logs_dir, exist_ok=True)

                from datetime import datetime
                log_filename = f"Hash_Verification_ERRORS_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                log_path = os.path.join(logs_dir, log_filename)

                try:
                    with open(log_path, 'w', encoding='utf-8') as lf:
                        lf.write("======================================================================\n")
                        lf.write(f"KryptDist Verification Error Log - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                        lf.write("======================================================================\n\n")

                        if has_failed:
                            lf.write("[CORRUPTED / HASH MISMATCH FILES]\n")
                            for item in results["failed"]:
                                lf.write(f"File: {item[0]}\n  Expected  : {item[1]}\n  Calculated: {item[2]}\n  Hash File : {item[3]}\n\n")

                        if has_missing:
                            lf.write("[MISSING FILES]\n")
                            for item in results["missing"]:
                                lf.write(f"File: {item[0]}\n  Hash File : {item[1]}\n\n")
                except Exception as e:
                    print(f"Error writing log file: {e}")
                sys.exit(1)

            msg = (
                f"Verification completed with ERRORS!\n\n"
                f"Corrupted Files: {len(results['failed'])}\n"
                f"Missing Files: {len(results['missing'])}\n\n"
                "Would you like to generate and view an error log?"
            )
            msg_box = QMessageBox(self if self.isVisible() else None)
            msg_box.setWindowFlags(msg_box.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
            msg_box.setWindowTitle("KryptDist - Verification Errors Detected")
            msg_box.setText(msg)
            msg_box.setIconPixmap(get_status_pixmap("error"))
            msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            msg_box.setDefaultButton(QMessageBox.StandardButton.Yes)
            if os.path.exists(icon_path):
                msg_box.setWindowIcon(QIcon(icon_path))

            if msg_box.exec() == QMessageBox.StandardButton.Yes:
                logs_dir = os.path.join(internal_dir, "logs")
                os.makedirs(logs_dir, exist_ok=True)

                from datetime import datetime
                log_filename = f"Hash_Verification_ERRORS_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                log_path = os.path.join(logs_dir, log_filename)

                try:
                    with open(log_path, 'w', encoding='utf-8') as lf:
                        lf.write("======================================================================\n")
                        lf.write(f"KryptDist Verification Error Log - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                        lf.write("======================================================================\n\n")

                        if has_failed:
                            lf.write("[CORRUPTED / HASH MISMATCH FILES]\n")
                            for item in results["failed"]:
                                lf.write(f"File: {item[0]}\n  Expected  : {item[1]}\n  Calculated: {item[2]}\n  Hash File : {item[3]}\n\n")

                        if has_missing:
                            lf.write("[MISSING FILES]\n")
                            for item in results["missing"]:
                                lf.write(f"File: {item[0]}\n  Hash File : {item[1]}\n\n")

                    if sys.platform == "win32":
                        os.startfile(log_path)
                except Exception as e:
                    print(f"Error writing log file: {e}")

            sys.exit(1)
        else:
            self.osd.close()
            if getattr(self, 'is_headless', False):
                sys.exit(0)
            msg_box = QMessageBox(self if self.isVisible() else None)
            msg_box.setWindowFlags(msg_box.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
            msg_box.setWindowTitle("KryptDist - Hash Verification")
            msg_box.setText("Hash checking successful. All data is 100% intact.")
            msg_box.setIconPixmap(get_status_pixmap("success"))
            if os.path.exists(icon_path):
                msg_box.setWindowIcon(QIcon(icon_path))
            msg_box.exec()
            sys.exit(0)

    def show_alert(self, title, text, icon_type="info", buttons=QMessageBox.StandardButton.Ok, default_button=None):
        """Displays a dialog box with optional sound suppression and consistent window icons."""
        sound_disabled = False
        if hasattr(self, 'settings'):
            sound_disabled = self.settings.value("disable_notification_sounds", False)

        script_dir = os.path.dirname(os.path.realpath(__file__))
        internal_dir = os.path.join(script_dir, "KryptDist_internal")
        icon_path = os.path.join(internal_dir, "icons", "KryptDist_ghost_icon.svg")

        msg_box = QMessageBox(self if self.isVisible() else None)
        window_title = title if title.startswith("KryptDist") else f"KryptDist - {title}"
        msg_box.setWindowTitle(window_title)
        msg_box.setText(text)
        msg_box.setStandardButtons(buttons)
        if default_button:
            msg_box.setDefaultButton(default_button)

        if os.path.exists(icon_path):
            msg_box.setWindowIcon(QIcon(icon_path))

        if icon_type == "success":
            msg_box.setIconPixmap(get_status_pixmap("success"))
        elif icon_type == "error":
            msg_box.setIconPixmap(get_status_pixmap("error"))
        elif icon_type == "warning":
            if not sound_disabled:
                msg_box.setIcon(QMessageBox.Icon.Warning)
            else:
                std_icon = self.style().standardIcon(self.style().StandardPixmap.SP_MessageBoxWarning)
                msg_box.setIconPixmap(std_icon.pixmap(48, 48))
        elif icon_type == "question":
            if not sound_disabled:
                msg_box.setIcon(QMessageBox.Icon.Question)
            else:
                std_icon = self.style().standardIcon(self.style().StandardPixmap.SP_MessageBoxQuestion)
                msg_box.setIconPixmap(std_icon.pixmap(48, 48))
        elif icon_type == "info":
            if not sound_disabled:
                msg_box.setIcon(QMessageBox.Icon.Information)
            else:
                std_icon = self.style().standardIcon(self.style().StandardPixmap.SP_MessageBoxInformation)
                msg_box.setIconPixmap(std_icon.pixmap(48, 48))

        return msg_box.exec()

    def set_controls_locked(self, locked):
        self.btn_add_dir.setEnabled(not locked)
        self.btn_add_files.setEnabled(not locked)
        self.btn_remove.setEnabled(not locked)
        self.btn_clear.setEnabled(not locked)
        self.combo_algo.setEnabled(not locked)
        self.check_delete_primary.setEnabled(not locked)
        self.check_subfolders.setEnabled(not locked)
        self.check_delete_subhashes.setEnabled(not locked)
        self.path_list.setAcceptDrops(not locked)

    def handle_run_or_cancel(self):
        if hasattr(self, 'worker') and self.worker.isRunning():
            reply = self.show_alert(
                "Cancel Operation",
                "Are you sure you want to cancel hash generation?",
                icon_type="question",
                buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                default_button=QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.worker.cancel()
                self.worker.wait()
                self.btn_run.setText("Generate Hashes")
                self.set_controls_locked(False)
                self.status_tree_root.setText(0, "Status: Cancelled")
                self.status_path_label.setText("")
        else:
            self.run_generation()

    def run_generation(self):
        targets = self.path_list.get_all_paths()
        if not targets:
            self.show_alert("No Targets", "Please add at least one file or folder to process.", icon_type="warning")
            return

        algo = self.combo_algo.currentText()
        distribute = self.check_subfolders.isChecked()
        delete_sub = self.check_delete_subhashes.isChecked()
        delete_primary = self.check_delete_primary.isChecked()
        
        ignore_types = self.settings.value("ignore_types", DEFAULT_IGNORE_TYPES)
        ignore_files = self.settings.value("ignore_files", DEFAULT_IGNORE_FILES)
        ignore_folders = self.settings.value("ignore_folders", DEFAULT_IGNORE_FOLDERS)

        self.btn_run.setText("Cancel")
        self.set_controls_locked(True)
        self.worker = HashWorker(
            targets, algo, distribute, delete_sub, delete_primary,
            ignore_types=ignore_types, ignore_files=ignore_files, ignore_folders=ignore_folders
        )
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.generation_complete)
        self.worker.start()

    def update_progress(self, current, total, file_path):
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        
        file_name = os.path.basename(file_path) or file_path
        self.status_tree_root.setText(0, f"Hashing [{current}/{total}]: {file_name}")
        self.status_path_label.setText(file_path)

    def generation_complete(self, results):
        self.status_tree_root.setText(0, "Status: Writing hash files...")
        self.status_path_label.setText("")
        algo = self.combo_algo.currentText()
        header = f"# checksum file generated with KryptDist v{APP_VERSION}\n# algorithm: {algo}\n\n"
        
        total_new_files = 0

        for target_dir, data in results.items():
            target_results = data["results"]
            existing_master = data["known"]
            is_dir = data.get("is_dir", True)
            root_folder_name = os.path.basename(target_dir) or "checksums"
            master_hash_path = os.path.join(target_dir, f"{root_folder_name}.hash")

            # Determine strictly new entries for master file
            new_master_entries = {k: v for k, v in target_results.items() if os.path.normpath(k) not in existing_master}
            total_new_files += len(new_master_entries)

            # Check existing file to detect last declared algorithm
            last_master_algo = None
            if os.path.exists(master_hash_path):
                try:
                    with open(master_hash_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            line = line.strip()
                            if line.startswith('# algorithm:'):
                                last_master_algo = line.split(':', 1)[1].strip()
                except Exception as e:
                    print(f"Error reading existing master algorithm: {e}")

            # Write or Append Master Hash if there are new entries or if master doesn't exist
            if new_master_entries or not os.path.exists(master_hash_path):
                try:
                    file_exists = os.path.exists(master_hash_path)
                    with open(master_hash_path, 'a' if file_exists else 'w', encoding='utf-8') as mf:
                        if not file_exists:
                            mf.write(header)
                        else:
                            if last_master_algo != algo:
                                mf.write(f"\n# algorithm: {algo}\n")
                        for rel_path, file_hash in new_master_entries.items():
                            mf.write(f"{file_hash} *{rel_path}\n")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to write master hash file for {target_dir}: {e}")
                    return

            # Write/Append Distributed Subfolder Hashes if enabled
            if is_dir and self.check_subfolders.isChecked():
                subfolder_hashes = {}
                for rel_path, file_hash in target_results.items():
                    norm_rel = os.path.normpath(rel_path)
                    parts = norm_rel.split(os.sep)
                    if len(parts) > 1:
                        sub_dir = os.path.join(target_dir, *parts[:-1])
                        sub_rel_path = parts[-1]
                        subfolder_hashes.setdefault(sub_dir, []).append((file_hash, sub_rel_path))

                for sub_dir, entries in subfolder_hashes.items():
                    sub_folder_name = os.path.basename(sub_dir)
                    sub_hash_path = os.path.join(sub_dir, f"{sub_folder_name}.hash")

                    existing_sub_entries = set()
                    last_sub_algo = None
                    if os.path.exists(sub_hash_path):
                        try:
                            with open(sub_hash_path, 'r', encoding='utf-8') as f:
                                for line in f:
                                    line = line.strip()
                                    if line.startswith('# algorithm:'):
                                        last_sub_algo = line.split(':', 1)[1].strip()
                                    elif line and not line.startswith('#'):
                                        parts = line.split(maxsplit=1)
                                        if len(parts) == 2:
                                            existing_sub_entries.add(os.path.normpath(parts[1].lstrip('*').strip()))
                        except Exception as e:
                            print(f"Error reading existing subfolder hash {sub_hash_path}: {e}")

                    new_sub_entries = [
                        (f_hash, s_rel) for f_hash, s_rel in entries 
                        if os.path.normpath(s_rel) not in existing_sub_entries
                    ]

                    if new_sub_entries or not os.path.exists(sub_hash_path):
                        try:
                            sub_file_exists = os.path.exists(sub_hash_path)
                            with open(sub_hash_path, 'a' if sub_file_exists else 'w', encoding='utf-8') as sf:
                                if not sub_file_exists:
                                    sf.write(header)
                                else:
                                    if last_sub_algo != algo:
                                        sf.write(f"\n# algorithm: {algo}\n")
                                for file_hash, sub_rel_path in new_sub_entries:
                                    sf.write(f"{file_hash} *{sub_rel_path}\n")
                        except Exception as e:
                            print(f"Error writing subfolder hash for {sub_dir}: {e}")

        self.btn_run.setText("Generate Hashes")
        self.set_controls_locked(False)
        if total_new_files == 0:
            self.status_tree_root.setText(0, "Status: No new files.")
            self.status_path_label.setText("")
            self.show_alert("Complete", "No new files. No checksums generated.", icon_type="info")
        else:
            self.status_tree_root.setText(0, "Status: Complete!")
            self.status_path_label.setText("")
            file_word = "file" if total_new_files == 1 else "files"
            self.show_alert("Complete", f"Successfully generated checksums for {total_new_files} {file_word}.", icon_type="info")


if __name__ == "__main__":
    # Headless CLI single-file verification for external managers (e.g. HashMan)
    if "--verify-file" in sys.argv or "-v" in sys.argv:
        flag = "--verify-file" if "--verify-file" in sys.argv else "-v"
        idx = sys.argv.index(flag)
        if idx + 1 < len(sys.argv):
            target_f = sys.argv[idx + 1]
            specified_h = None
            if "--hash-file" in sys.argv:
                h_idx = sys.argv.index("--hash-file")
                if h_idx + 1 < len(sys.argv):
                    specified_h = sys.argv[h_idx + 1]
            exit_code = verify_single_file_cli(target_f, specified_h)
            sys.exit(exit_code)
        sys.exit(2)

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setStyle("Fusion")
    window = KryptDistApp()
    if not hasattr(window, 'hash_files_passed') or not window.hash_files_passed:
        window.show()
    sys.exit(app.exec())