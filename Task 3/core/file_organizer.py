"""
Automated File Organizer Core Module.
Handles directory scanning, extension classification, collision resolution,
dry-run previewing, organization execution, and full undo functionality.
"""

import os
import shutil
import time
from pathlib import Path
from typing import Dict, List, Optional, Callable, Tuple


# Default category to extensions mapping
DEFAULT_CATEGORIES: Dict[str, List[str]] = {
    "Documents": [".pdf", ".docx", ".doc", ".txt", ".rtf", ".odt", ".tex", ".md", ".epub"],
    "Spreadsheets": [".xlsx", ".xls", ".csv", ".tsv", ".ods"],
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".tiff", ".ico"],
    "Audio": [".mp3", ".wav", ".aac", ".flac", ".ogg", ".m4a", ".wma"],
    "Video": [".mp4", ".mkv", ".mov", ".avi", ".wmv", ".flv", ".webm"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz"],
    "Code & Scripts": [".py", ".js", ".ts", ".html", ".css", ".java", ".cpp", ".c", ".cs", ".go", ".rs", ".php", ".sh", ".bat", ".ps1"],
    "Logs & Dumps": [".log", ".err", ".out", ".dump", ".crash", ".trace"],
    "Data & Config": [".json", ".xml", ".yaml", ".yml", ".ini", ".env", ".toml", ".sql", ".db", ".sqlite"],
    "Executables": [".exe", ".msi", ".dmg", ".apk", ".appimage", ".iso"],
}


class FileMoveRecord:
    """Stores information about a single file move operation for logging and undo."""
    def __init__(self, original_path: str, new_path: str, category: str, size_bytes: int):
        self.original_path = original_path
        self.new_path = new_path
        self.category = category
        self.size_bytes = size_bytes
        self.timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self) -> dict:
        return {
            "original_path": self.original_path,
            "new_path": self.new_path,
            "category": self.category,
            "size_bytes": self.size_bytes,
            "timestamp": self.timestamp
        }


class FileOrganizer:
    def __init__(self, categories: Optional[Dict[str, List[str]]] = None):
        self.categories = categories or DEFAULT_CATEGORIES.copy()
        self.ext_to_category: Dict[str, str] = {}
        self._rebuild_ext_map()
        self.undo_history: List[List[FileMoveRecord]] = []

    def _rebuild_ext_map(self):
        """Builds a fast lookup dictionary from lowercase extension to category name."""
        self.ext_to_category.clear()
        for category, extensions in self.categories.items():
            for ext in extensions:
                self.ext_to_category[ext.lower()] = category

    def get_category_for_file(self, filename: str) -> str:
        """Determines the target category name based on file extension."""
        ext = Path(filename).suffix.lower()
        return self.ext_to_category.get(ext, "Others")

    def scan_directory(self, target_dir: str, recursive: bool = False) -> List[Path]:
        """Scans directory for files excluding hidden files and system artifacts."""
        target_path = Path(target_dir)
        if not target_path.exists() or not target_path.is_dir():
            raise ValueError(f"Directory '{target_dir}' does not exist or is not a valid folder.")

        files: List[Path] = []
        if recursive:
            for root, dirs, filenames in os.walk(target_dir):
                # Skip category folders if they were already created in root
                for filename in filenames:
                    if filename.startswith('.'):
                        continue
                    p = Path(root) / filename
                    files.append(p)
        else:
            for item in target_path.iterdir():
                if item.is_file() and not item.name.startswith('.'):
                    files.append(item)
        return files

    def preview_organize(
        self,
        target_dir: str,
        recursive: bool = False,
        selected_categories: Optional[List[str]] = None
    ) -> List[Tuple[str, str, str, int]]:
        """
        Dry-run preview of organization.
        Returns list of tuples: (source_filename, original_path, target_category_path, size_bytes)
        """
        files = self.scan_directory(target_dir, recursive=recursive)
        preview_list = []

        target_base = Path(target_dir)

        for file_path in files:
            category = self.get_category_for_file(file_path.name)
            if selected_categories and category not in selected_categories:
                continue

            target_folder = target_base / category
            # If the file is already inside its designated category folder, skip it
            if file_path.parent == target_folder:
                continue

            dest_path = target_folder / file_path.name
            size = file_path.stat().st_size if file_path.exists() else 0
            preview_list.append((file_path.name, str(file_path), str(dest_path), size))

        return preview_list

    def organize(
        self,
        target_dir: str,
        recursive: bool = False,
        selected_categories: Optional[List[str]] = None,
        collision_mode: str = "rename", # 'rename', 'overwrite', 'skip'
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
        log_callback: Optional[Callable[[str, str], None]] = None
    ) -> Tuple[int, int, List[FileMoveRecord]]:
        """
        Executes file organization.
        Returns: (successful_moves_count, error_count, move_records)
        """
        target_base = Path(target_dir)
        files = self.scan_directory(target_dir, recursive=recursive)
        total_files = len(files)
        successful_moves = 0
        error_count = 0
        current_batch_records: List[FileMoveRecord] = []

        if log_callback:
            log_callback("INFO", f"Starting organization in '{target_dir}' ({total_files} files found)...")

        for idx, file_path in enumerate(files, start=1):
            category = self.get_category_for_file(file_path.name)
            
            if selected_categories and category not in selected_categories:
                if progress_callback:
                    progress_callback(idx, total_files, f"Skipped: {file_path.name}")
                continue

            target_folder = target_base / category
            # Avoid moving if already in place
            if file_path.parent == target_folder:
                if progress_callback:
                    progress_callback(idx, total_files, f"Already organized: {file_path.name}")
                continue

            try:
                target_folder.mkdir(parents=True, exist_ok=True)
                dest_path = target_folder / file_path.name

                # Collision resolution
                if dest_path.exists() and dest_path != file_path:
                    if collision_mode == "skip":
                        if log_callback:
                            log_callback("WARN", f"File '{file_path.name}' already exists in {category}. Skipping.")
                        continue
                    elif collision_mode == "rename":
                        stem = file_path.stem
                        suffix = file_path.suffix
                        counter = 1
                        while dest_path.exists():
                            dest_path = target_folder / f"{stem}_{counter}{suffix}"
                            counter += 1

                file_size = file_path.stat().st_size
                shutil.move(str(file_path), str(dest_path))
                record = FileMoveRecord(
                    original_path=str(file_path),
                    new_path=str(dest_path),
                    category=category,
                    size_bytes=file_size
                )
                current_batch_records.append(record)
                successful_moves += 1

                if log_callback:
                    log_callback("SUCCESS", f"Moved '{file_path.name}' -> [{category}]")

            except Exception as e:
                error_count += 1
                if log_callback:
                    log_callback("ERROR", f"Failed to move '{file_path.name}': {str(e)}")

            if progress_callback:
                progress_callback(idx, total_files, f"Processed {file_path.name}")

        if current_batch_records:
            self.undo_history.append(current_batch_records)

        if log_callback:
            log_callback("INFO", f"Organization complete: {successful_moves} files moved, {error_count} errors.")

        return successful_moves, error_count, current_batch_records

    def undo_last(self, log_callback: Optional[Callable[[str, str], None]] = None) -> Tuple[int, int]:
        """
        Reverts the most recent batch of moved files back to their original positions.
        Returns: (restored_count, error_count)
        """
        if not self.undo_history:
            if log_callback:
                log_callback("WARN", "No organization operations available to undo.")
            return 0, 0

        last_batch = self.undo_history.pop()
        restored = 0
        errors = 0

        if log_callback:
            log_callback("INFO", f"Reverting last batch ({len(last_batch)} operations)...")

        for record in reversed(last_batch):
            current_path = Path(record.new_path)
            orig_path = Path(record.original_path)

            if not current_path.exists():
                errors += 1
                if log_callback:
                    log_callback("ERROR", f"Cannot restore '{current_path.name}': file not found.")
                continue

            try:
                orig_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(current_path), str(orig_path))
                restored += 1
                if log_callback:
                    log_callback("SUCCESS", f"Restored '{current_path.name}' -> {orig_path.parent.name}/")
            except Exception as e:
                errors += 1
                if log_callback:
                    log_callback("ERROR", f"Failed to restore '{current_path.name}': {str(e)}")

        if log_callback:
            log_callback("INFO", f"Undo finished: {restored} files restored, {errors} errors.")

        return restored, errors
