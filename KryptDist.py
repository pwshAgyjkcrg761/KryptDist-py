# ==============================================================================
# SCRIPT: KryptDist.py
# VERSION: 2026.09.08__11.42.00
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
import ctypes
import ctypes.wintypes

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
                             QComboBox, QProgressBar, QHBoxLayout, QListWidget)
from PyQt6.QtGui import QActionGroup, QPalette, QColor, QIcon
import ctypes

APP_VERSION = "2026.09.08__11.42.00"
CHECKSUM_EXTS = (
    ".hash", ".b3", ".blake3", ".b2", ".blake2", ".blake2b", ".blake2s",
    ".sha512", ".sha256", ".sha3", ".sha3-256", ".sha3-512",
    ".xx3", ".xxh3", ".xxh", ".sha1", ".sha", ".md5", ".sfv", ".crc32", ".crc"
)

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


class HashWorker(QThread):
    progress = pyqtSignal(int, int, str)
    verification_progress = pyqtSignal(str)
    finished = pyqtSignal(dict)
    verification_finished = pyqtSignal(dict)
    
    def __init__(self, target_dir, algorithm, dist_subfolders, delete_subhashes=False, delete_primary_hash=False):
        super().__init__()
        self.target_dir = os.path.normpath(target_dir)
        self.algorithm = algorithm
        self.dist_subfolders = dist_subfolders
        self.delete_subhashes = delete_subhashes
        self.delete_primary_hash = delete_primary_hash
        
    def run(self):
        root_folder_name = os.path.basename(self.target_dir)
        master_hash_path = os.path.join(self.target_dir, f"{root_folder_name}.hash")

        # Clean existing primary/master .hash file if requested
        if self.delete_primary_hash:
            if os.path.exists(master_hash_path):
                try:
                    os.remove(master_hash_path)
                except Exception as e:
                    print(f"Error removing primary hash: {e}")

        # Clean existing subdirectory checksum files if requested (leaves root .hash file intact)
        if self.delete_subhashes:
            for root, dirs, files in os.walk(self.target_dir):
                # Skip root folder to avoid deleting the master hash file
                if os.path.normpath(root) == self.target_dir:
                    continue
                for f in files:
                    if f.lower().endswith(CHECKSUM_EXTS):
                        try:
                            os.remove(os.path.join(root, f))
                        except Exception as e:
                            print(f"Error removing subfolder checksum file {f}: {e}")
        # 1. Parse existing master .hash file to track previously hashed relative paths
        existing_entries = set()
        root_folder_name = os.path.basename(self.target_dir)
        master_hash_path = os.path.join(self.target_dir, f"{root_folder_name}.hash")
        
        if os.path.exists(master_hash_path):
            try:
                with open(master_hash_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            parts = line.split(maxsplit=1)
                            if len(parts) == 2:
                                rel_p = parts[1].lstrip('*').strip()
                                existing_entries.add(os.path.normpath(rel_p))
            except Exception as e:
                print(f"Error reading existing master hash: {e}")

        # 2. Collect all non-checksum files
        all_files = []
        for root, dirs, files in os.walk(self.target_dir):
            for f in files:
                if not f.lower().endswith(CHECKSUM_EXTS):
                    all_files.append(os.path.join(root, f))

        # 3. Read hashes from existing master file so we have the full record available
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
                                all_known_hashes[rel_p] = h_val
            except Exception as e:
                print(f"Error reading existing master entries: {e}")

        # 4. Filter down strictly to NEW files requiring calculation
        file_list = []
        for file_path in all_files:
            rel_path = os.path.normpath(os.path.relpath(file_path, self.target_dir))
            if rel_path not in existing_entries:
                file_list.append(file_path)

        total_files = len(file_list)
        results = dict(all_known_hashes)  # Seed results with already-known hashes
        
        for idx, file_path in enumerate(file_list, 1):
            rel_path = os.path.relpath(file_path, self.target_dir)
            self.progress.emit(idx, total_files, rel_path)
            
            try:
                if self.algorithm == "SFV / CRC32":
                    crc_val = 0
                    with open(file_path, 'rb') as f:
                        while chunk := f.read(65536):
                            crc_val = zlib.crc32(chunk, crc_val)
                    results[rel_path] = f"{crc_val & 0xFFFFFFFF:08x}"
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
                    results[rel_path] = hasher.hexdigest()
            except Exception as e:
                print(f"Error hashing {file_path}: {e}")
                
        self.finished.emit(results)

    def verify_hash_files(self, hash_file_paths):
        verification_results = {
            "total_checked": 0,
            "passed": 0,
            "failed": [],
            "missing": []
        }

        for hash_file in hash_file_paths:
            base_dir = os.path.dirname(hash_file)
            ext = os.path.splitext(hash_file)[1].lower()
            if ext in (".sha3", ".sha3-256", ".sha3-512"):
                current_algo = "SHA-3"
            elif ext == ".sha256":
                current_algo = "SHA-256"
            elif ext == ".sha512":
                current_algo = "SHA-512"
            elif ext == ".md5":
                current_algo = "MD5"
            elif ext in (".sha1", ".sha"):
                current_algo = "SHA-1"
            elif ext in (".sfv", ".crc32", ".crc"):
                current_algo = "SFV / CRC32"
            elif ext in (".xx3", ".xxh3", ".xxh"):
                current_algo = "xx3"
            elif ext in (".b2", ".blake2", ".blake2b"):
                current_algo = "BLAKE2b"
            elif ext == ".blake2s":
                current_algo = "BLAKE2s"
            else:
                current_algo = "BLAKE3"
            
            try:
                with open(hash_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                for line in lines:
                    line_str = line.strip()
                    if line_str.startswith("# algorithm:"):
                        current_algo = line_str.split(":", 1)[1].strip()
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
                            expected_hash = first_tok
                            rel_path = line_str.split(maxsplit=1)[1].lstrip('*').strip()

                        full_path = os.path.join(base_dir, rel_path)

                        self.verification_progress.emit(rel_path)
                        verification_results["total_checked"] += 1

                        if not os.path.exists(full_path):
                            verification_results["missing"].append((rel_path, hash_file))
                            continue

                        # Resolve effective algorithm using header state & length heuristics
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
                            # 256-bit digest: keep current_algo if it is a 256-bit engine, otherwise default to BLAKE3
                            algo_u = current_algo.upper()
                            if not any(k in algo_u for k in ["BLAKE3", "256", "BLAKE2S", "SHA-3", "SHA3"]):
                                algo = "BLAKE3"
                        elif h_len == 128:
                            # 512-bit digest: keep current_algo if it is a 512-bit engine, otherwise default to BLAKE2b
                            algo_u = current_algo.upper()
                            if not any(k in algo_u for k in ["BLAKE2", "512"]):
                                algo = "BLAKE2b"

                        try:
                            algo_upper = algo.upper()
                            if "CRC" in algo_upper or "SFV" in algo_upper:
                                crc_val = 0
                                with open(full_path, 'rb') as vf:
                                    while chunk := vf.read(65536):
                                        crc_val = zlib.crc32(chunk, crc_val)
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
                                calculated_hash = hasher.hexdigest()

                            if calculated_hash.lower() == expected_hash.lower():
                                verification_results["passed"] += 1
                            else:
                                verification_results["failed"].append((rel_path, expected_hash, calculated_hash, hash_file))
                        except Exception as e:
                            verification_results["failed"].append((rel_path, expected_hash, str(e), hash_file))

            except Exception as e:
                print(f"Error reading hash file {hash_file}: {e}")

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
        
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 4, 8, 4)
        
        self.lbl_file = QLabel("Initializing...")
        self.lbl_file.setStyleSheet("font-size: 11px; color: #ffffff;")
        self.lbl_file.setFixedWidth(380)
        self.lbl_file.setWordWrap(False)
        layout.addWidget(self.lbl_file)
        
        self.setLayout(layout)
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                border: 2px solid #007acc;
                border-radius: 4px;
                padding: 2px;
            }
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


class DropListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)

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
            for url in event.mimeData().urls():
                file_path = os.path.normpath(url.toLocalFile()).replace('/', os.sep)
                if file_path and os.path.exists(file_path):
                    if file_path.lower().endswith(CHECKSUM_EXTS):
                        continue
                    existing = [self.item(i).text() for i in range(self.count())]
                    if file_path not in existing:
                        self.addItem(file_path)
            event.acceptProposedAction()
        else:
            event.ignore()


class KryptDistApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"KryptDist v{APP_VERSION}")
        
        script_dir = os.path.dirname(os.path.realpath(__file__))
        internal_dir = os.path.join(script_dir, "KryptDist_internal")
        os.makedirs(internal_dir, exist_ok=True)
        self.config_file = os.path.join(internal_dir, "KryptDist.config.json")
        
        icon_path = os.path.join(internal_dir, "KryptDist_icon", "KryptDist-icon.svg")
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
        
        # Parse command line inputs (e.g. from SendTo or file drag onto script)
        self.target_paths = []
        if len(sys.argv) > 1:
            for arg in sys.argv[1:]:
                clean_p = os.path.abspath(arg.strip('"\''))
                if os.path.exists(clean_p) and clean_p not in self.target_paths:
                    self.target_paths.append(clean_p)

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
        layout.addWidget(QLabel("Target Files & Folders:"))
        self.path_list = DropListWidget()
        if self.target_paths:
            self.path_list.addItems(self.target_paths)
        layout.addWidget(self.path_list)

        # Path Control Buttons
        btn_layout = QHBoxLayout()
        btn_add_dir = QPushButton("Add Folder")
        btn_add_dir.clicked.connect(self.add_directory)
        btn_layout.addWidget(btn_add_dir)

        btn_add_files = QPushButton("Add Files")
        btn_add_files.clicked.connect(self.add_files)
        btn_layout.addWidget(btn_add_files)

        btn_remove = QPushButton("Remove Selected")
        btn_remove.clicked.connect(self.remove_selected_path)
        btn_layout.addWidget(btn_remove)

        btn_clear = QPushButton("Clear")
        btn_clear.clicked.connect(self.clear_paths)
        btn_layout.addWidget(btn_clear)
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
        self.status_label = QLabel("Status: Ready")
        layout.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        # Action Buttons
        btn_run = QPushButton("Generate Hashes")
        btn_run.clicked.connect(self.run_generation)
        layout.addWidget(btn_run)
        
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
        event.accept()

    def add_directory(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Directory", self.last_directory)
        if dir_path:
            clean_p = os.path.normpath(dir_path).replace('/', os.sep)
            self.last_directory = clean_p
            self.settings.setValue("last_directory", self.last_directory)
            existing = [self.path_list.item(i).text() for i in range(self.path_list.count())]
            if clean_p not in existing:
                self.path_list.addItem(clean_p)

    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Files", self.last_directory)
        if files:
            self.last_directory = os.path.normpath(os.path.dirname(files[0])).replace('/', os.sep)
            self.settings.setValue("last_directory", self.last_directory)
            existing = [self.path_list.item(i).text() for i in range(self.path_list.count())]
            for f in files:
                clean_p = os.path.normpath(f).replace('/', os.sep)
                if not clean_p.lower().endswith(CHECKSUM_EXTS) and clean_p not in existing:
                    self.path_list.addItem(clean_p)

    def remove_selected_path(self):
        for item in self.path_list.selectedItems():
            self.path_list.takeItem(self.path_list.row(item))

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
        
        help_menu = menu_bar.addMenu("&Help")
        manual_action = help_menu.addAction("Manual")
        manual_action.triggered.connect(self.show_manual)
        about_action = help_menu.addAction("About")
        about_action.triggered.connect(self.show_about)

    def apply_theme(self, theme_name):
        app = QApplication.instance()
        app.setStyle("Fusion")
        palette = QPalette()
        
        if theme_name == "Dark":
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
        elif theme_name == "Light":
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
        else:
            is_dark = app.style().standardPalette().color(QPalette.ColorRole.Window).lightness() < 128
            self.apply_theme("Dark" if is_dark else "Light")
            return
            
        app.setPalette(palette)

    def change_theme(self, theme_name):
        self.current_theme = theme_name
        self.apply_theme(theme_name)

    def show_manual(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Manual")
        dialog.resize(650, 500)
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
            f"<p>USAGE GUIDE | Copyright (C) 2026 pwshAgyjkcrg761</p><br>"
            f"<h2>OVERVIEW</h2>"
            f"<p>KryptDist generates and verifies multi-tier checksum file sets across directories and subdirectories in Corz-compatible formatting.</p>"
            f"<h2>HASH ENGINES</h2>"
            f"<ul>"
            f"<li><b>BLAKE3:</b> Ultra-fast multi-threaded cryptographic hash.</li>"
            f"<li><b>BLAKE2b / BLAKE2s:</b> Standard cryptographic hashes natively supported in Python.</li>"
            f"</ul>"
            f"<h2>WORKFLOW</h2>"
            f"<p>Select your root directory, choose your algorithm, and click <b>Generate Hashes</b>. "
            f"KryptDist reads files in a single pass to create a master <code>.hash</code> file and optional distributed subdirectory hashes.</p>"
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
            f"<h1>KryptDist v{APP_VERSION}</h1>"
            "<p>Copyright (C) 2026 <b>pwshAgyjkcrg761</b><br>"
            "Licensed under <b>GPLv3</b></p>"
            "<p>A high-performance checksum generator and distributor supporting BLAKE2, BLAKE3, and Corz-compatible file sidecars.</p>"
            "<p>Official License: <a href=\"https://www.gnu.org/licenses/gpl-3.0.html\">gnu.org/licenses/gpl-3.0.html</a></p>"
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

        if has_failed or has_missing:
            self.osd.trigger_error_flash()
            QApplication.processEvents()
            
            # Create centralized logs directory inside internal folder
            script_dir = os.path.dirname(os.path.realpath(__file__))
            logs_dir = os.path.join(script_dir, "KryptDist_internal", "logs")
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

            self.osd.close()
            msg = f"Verification completed with ERRORS!\n\nCorrupted Files: {len(results['failed'])}\nMissing Files: {len(results['missing'])}\n\nLog created at:\n{log_path}"
            QMessageBox.critical(None, "Verification Errors Detected", msg)
            sys.exit(1)
        else:
            self.osd.close()
            QMessageBox.information(None, "Hash Verification", "Hash checking successful. All data is 100% intact.")
            sys.exit(0)

    def run_generation(self):
        targets = [self.path_list.item(i).text() for i in range(self.path_list.count())]
        if not targets:
            QMessageBox.warning(self, "No Targets", "Please add at least one file or folder to process.")
            return

        algo = self.combo_algo.currentText()
        distribute = self.check_subfolders.isChecked()
        delete_sub = self.check_delete_subhashes.isChecked()
        delete_primary = self.check_delete_primary.isChecked()
        
        target_dir = targets[0] if targets else self.last_directory
        self.worker = HashWorker(target_dir, algo, distribute, delete_sub, delete_primary)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.generation_complete)
        self.worker.start()

    def update_progress(self, current, total, rel_path):
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        self.status_label.setText(f"Hashing [{current}/{total}]: {rel_path}")

    def generation_complete(self, results):
        self.status_label.setText("Status: Writing hash files...")
        algo = self.combo_algo.currentText()
        target_dir = self.worker.target_dir
        root_folder_name = os.path.basename(target_dir)
        master_hash_path = os.path.join(target_dir, f"{root_folder_name}.hash")
        
        header = f"# checksum file generated with KryptDist v{APP_VERSION}\n# algorithm: {algo}\n\n"
        
        # Parse existing master entries and detect last declared algorithm
        existing_master = {}
        last_master_algo = None
        if os.path.exists(master_hash_path):
            try:
                with open(master_hash_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith('# algorithm:'):
                            last_master_algo = line.split(':', 1)[1].strip()
                        elif line and not line.startswith('#'):
                            parts = line.split(maxsplit=1)
                            if len(parts) == 2:
                                existing_master[os.path.normpath(parts[1].lstrip('*').strip())] = parts[0].strip()
            except Exception as e:
                print(f"Error reading existing master entries: {e}")

        # Determine strictly new entries for master file
        new_master_entries = {k: v for k, v in results.items() if os.path.normpath(k) not in existing_master}

        # Write or Append Master Hash if there are new entries or if master doesn't exist
        if new_master_entries or not os.path.exists(master_hash_path):
            try:
                file_exists = os.path.exists(master_hash_path)
                with open(master_hash_path, 'a' if file_exists else 'w', encoding='utf-8') as f:
                    if not file_exists:
                        f.write(header)
                    else:
                        if last_master_algo != algo:
                            f.write(f"\n# algorithm: {algo}\n")
                    for rel_path, file_hash in new_master_entries.items():
                        f.write(f"{file_hash} *{rel_path}\n")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to write master hash file: {e}")
                return

        # Write/Append Distributed Subfolder Hashes if enabled
        if self.check_subfolders.isChecked():
            subfolder_hashes = {}
            for rel_path, file_hash in results.items():
                norm_rel = os.path.normpath(rel_path)
                parts = norm_rel.split(os.sep)
                if len(parts) > 1:
                    sub_dir = os.path.join(target_dir, *parts[:-1])
                    sub_rel_path = parts[-1]
                    subfolder_hashes.setdefault(sub_dir, []).append((file_hash, sub_rel_path))

            for sub_dir, entries in subfolder_hashes.items():
                sub_folder_name = os.path.basename(sub_dir)
                sub_hash_path = os.path.join(sub_dir, f"{sub_folder_name}.hash")
                
                # Parse existing entries and detect last declared algorithm in subfolder hash file
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

                # Filter strictly to new subfolder entries
                new_sub_entries = [
                    (f_hash, s_rel) for f_hash, s_rel in entries 
                    if os.path.normpath(s_rel) not in existing_sub_entries
                ]

                if new_sub_entries or not os.path.exists(sub_hash_path):
                    try:
                        sub_file_exists = os.path.exists(sub_hash_path)
                        with open(sub_hash_path, 'a' if sub_file_exists else 'w', encoding='utf-8') as f:
                            if not sub_file_exists:
                                f.write(header)
                            else:
                                if last_sub_algo != algo:
                                    f.write(f"\n# algorithm: {algo}\n")
                            for file_hash, sub_rel_path in new_sub_entries:
                                f.write(f"{file_hash} *{sub_rel_path}\n")
                    except Exception as e:
                        print(f"Error writing subfolder hash for {sub_dir}: {e}")

        if not new_master_entries:
            self.status_label.setText("Status: No new files.")
            QMessageBox.information(self, "Complete", "No new files. No checksums generated.")
        else:
            self.status_label.setText("Status: Complete!")
            count = len(new_master_entries)
            file_word = "file" if count == 1 else "files"
            QMessageBox.information(self, "Complete", f"Successfully generated checksums for {count} {file_word}.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = KryptDistApp()
    if not hasattr(window, 'hash_files_passed') or not window.hash_files_passed:
        window.show()
    sys.exit(app.exec())