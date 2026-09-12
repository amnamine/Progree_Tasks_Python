"""
Background Automation Daemon & Folder Watcher.
Monitors a target directory in the background, automatically sorts incoming files
and extracts patterns from new log files into the master CSV.
"""

import time
import threading
from pathlib import Path
from typing import Optional, Callable, Dict, Any, List

from core.file_organizer import FileOrganizer
from core.text_parser import TextParserEngine, ExtractedEntity


class AutomationWatcher:
    def __init__(
        self,
        target_dir: str,
        master_csv_path: str,
        organizer: Optional[FileOrganizer] = None,
        parser: Optional[TextParserEngine] = None,
        poll_interval_sec: float = 3.0,
        auto_organize: bool = True,
        auto_parse_logs: bool = True
    ):
        self.target_dir = target_dir
        self.master_csv_path = master_csv_path
        self.organizer = organizer or FileOrganizer()
        self.parser = parser or TextParserEngine()
        self.poll_interval = poll_interval_sec
        self.auto_organize = auto_organize
        self.auto_parse_logs = auto_parse_logs

        self._is_running = False
        self._is_paused = False
        self._thread: Optional[threading.Thread] = None
        self._processed_files_hash: Dict[str, float] = {}

        # Callbacks
        self.on_log: Optional[Callable[[str, str], None]] = None
        self.on_status_change: Optional[Callable[[str], None]] = None
        self.on_cycle_completed: Optional[Callable[[Dict[str, Any]], None]] = None

        # Statistics
        self.stats = {
            "total_cycles": 0,
            "files_organized": 0,
            "entities_extracted": 0,
            "started_at": None,
            "last_activity": None
        }

    def start(self):
        """Starts the background watcher thread."""
        if self._is_running:
            return

        self._is_running = True
        self._is_paused = False
        self.stats["started_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
        
        self._thread = threading.Thread(target=self._run_loop, daemon=True, name="AutomationWatcherDaemon")
        self._thread.start()

        if self.on_status_change:
            self.on_status_change("RUNNING")
        if self.on_log:
            self.on_log("INFO", f"Background Automation Daemon started. Monitoring '{self.target_dir}' every {self.poll_interval}s.")

    def pause(self):
        """Pauses the watcher."""
        self._is_paused = True
        if self.on_status_change:
            self.on_status_change("PAUSED")
        if self.on_log:
            self.on_log("WARN", "Background watcher paused.")

    def resume(self):
        """Resumes the watcher."""
        self._is_paused = False
        if self.on_status_change:
            self.on_status_change("RUNNING")
        if self.on_log:
            self.on_log("INFO", "Background watcher resumed.")

    def stop(self):
        """Stops the watcher thread."""
        self._is_running = False
        if self.on_status_change:
            self.on_status_change("STOPPED")
        if self.on_log:
            self.on_log("INFO", "Background watcher stopped.")

    @property
    def is_running(self) -> bool:
        return self._is_running

    @property
    def is_paused(self) -> bool:
        return self._is_paused

    def _run_loop(self):
        while self._is_running:
            if not self._is_paused:
                try:
                    self._check_and_process()
                except Exception as e:
                    if self.on_log:
                        self.on_log("ERROR", f"Watcher cycle error: {str(e)}")

            # Sleep in short increments for responsive termination
            sleep_chunks = max(1, int(self.poll_interval / 0.2))
            for _ in range(sleep_chunks):
                if not self._is_running:
                    break
                time.sleep(self.poll_interval / sleep_chunks)

    def _check_and_process(self):
        target_path = Path(self.target_dir)
        if not target_path.exists() or not target_path.is_dir():
            return

        self.stats["total_cycles"] += 1
        new_or_modified_files = []

        # Find top-level unorganized files
        for item in target_path.iterdir():
            if item.is_file() and not item.name.startswith('.'):
                try:
                    mtime = item.stat().st_mtime
                    file_key = str(item.resolve())
                    if file_key not in self._processed_files_hash or self._processed_files_hash[file_key] < mtime:
                        new_or_modified_files.append(item)
                        self._processed_files_hash[file_key] = mtime
                except Exception:
                    continue

        if not new_or_modified_files:
            return

        self.stats["last_activity"] = time.strftime("%H:%M:%S")
        if self.on_log:
            self.on_log("INFO", f"Watcher detected {len(new_or_modified_files)} new/modified files in target folder.")

        # 1. Parse text & logs FIRST if enabled (before moving them)
        if self.auto_parse_logs:
            log_extensions = {".log", ".txt", ".csv", ".json", ".out", ".err"}
            all_extracted: List[ExtractedEntity] = []

            for file_item in new_or_modified_files:
                if file_item.suffix.lower() in log_extensions:
                    entities = self.parser.parse_file(str(file_item))
                    if entities:
                        all_extracted.extend(entities)

            if all_extracted:
                self.parser.export_master_csv(
                    self.master_csv_path,
                    entities=all_extracted,
                    append_mode=True,
                    log_callback=self.on_log
                )
                self.stats["entities_extracted"] += len(all_extracted)
                if self.on_log:
                    self.on_log("SUCCESS", f"Auto-parsed {len(all_extracted)} entity records -> appended to Master CSV.")

        # 2. Auto-organize files into extension folders if enabled
        if self.auto_organize:
            moved, errors, _ = self.organizer.organize(
                target_dir=self.target_dir,
                recursive=False,
                collision_mode="rename",
                log_callback=self.on_log
            )
            self.stats["files_organized"] += moved

        if self.on_cycle_completed:
            self.on_cycle_completed(self.stats.copy())
