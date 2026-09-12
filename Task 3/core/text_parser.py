"""
Text Parsing & Regular Expression Extraction Engine.
Extracts structured entities (emails, transaction IDs, IP addresses, timestamps, log levels, etc.)
from flat log files and logs results to a clean Master CSV file.
"""

import os
import re
import csv
import time
from pathlib import Path
from typing import Dict, List, Optional, Callable, Pattern, Any, Tuple


# Predefined high-accuracy regex patterns
DEFAULT_REGEX_PATTERNS: Dict[str, str] = {
    "Email": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
    "Transaction ID": r"\b(?:TXN|TRX|PAY|ORD|INV|REF)-[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*\b|\b(?:ch_|tx_|pi_)[a-zA-Z0-9]{14,24}\b|\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b",
    "IPv4 Address": r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b",
    "Timestamp / Date": r"\b\d{4}-\d{2}-\d{2}(?:[ T]\d{2}:\d{2}:\d{2}(?:\.\d+)?)?(?:Z|[+-]\d{2}:?\d{2})?\b|\b\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2}\b",
    "Log Level": r"\b(?:DEBUG|INFO|NOTICE|WARN|WARNING|ERROR|CRITICAL|FATAL|EXCEPTION)\b",
    "Phone Number": r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}\b",
    "Monetary Amount": r"\b(?:\$|€|£|USD|EUR|GBP)\s?\d+(?:,\d{3})*(?:\.\d{2})?\b|\b\d+(?:,\d{3})*(?:\.\d{2})?\s?(?:USD|EUR|GBP)\b",
    "URL / Endpoint": r"https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*)"
}


class ExtractedEntity:
    """Represents an extracted token match from a log file."""
    def __init__(
        self,
        source_file: str,
        line_number: int,
        entity_type: str,
        value: str,
        context_snippet: str,
        timestamp: Optional[str] = None
    ):
        self.timestamp = timestamp or time.strftime("%Y-%m-%d %H:%M:%S")
        self.source_file = source_file
        self.line_number = line_number
        self.entity_type = entity_type
        self.value = value.strip()
        self.context_snippet = context_snippet.strip()

    def to_csv_row(self) -> List[Any]:
        return [
            self.timestamp,
            self.source_file,
            self.line_number,
            self.entity_type,
            self.value,
            self.context_snippet
        ]

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "source_file": self.source_file,
            "line_number": self.line_number,
            "entity_type": self.entity_type,
            "value": self.value,
            "context_snippet": self.context_snippet
        }


class TextParserEngine:
    def __init__(self, patterns: Optional[Dict[str, str]] = None):
        self.patterns = patterns or DEFAULT_REGEX_PATTERNS.copy()
        self.compiled_patterns: Dict[str, Pattern] = {}
        self._compile_patterns()
        self.extracted_records: List[ExtractedEntity] = []

    def _compile_patterns(self):
        """Compiles regex strings into regex pattern objects."""
        self.compiled_patterns.clear()
        for name, pattern_str in self.patterns.items():
            try:
                self.compiled_patterns[name] = re.compile(pattern_str, re.IGNORECASE)
            except re.error as e:
                print(f"Failed to compile pattern '{name}': {e}")

    def add_custom_pattern(self, name: str, pattern_str: str) -> bool:
        """Adds or updates a custom regex pattern."""
        try:
            compiled = re.compile(pattern_str, re.IGNORECASE)
            self.patterns[name] = pattern_str
            self.compiled_patterns[name] = compiled
            return True
        except re.error:
            return False

    def parse_file(
        self,
        file_path: str,
        active_entity_types: Optional[List[str]] = None,
        max_lines: Optional[int] = None
    ) -> List[ExtractedEntity]:
        """
        Parses a single text or log file and extracts matching patterns.
        """
        path = Path(file_path)
        if not path.is_file():
            return []

        results: List[ExtractedEntity] = []
        selected_types = active_entity_types or list(self.compiled_patterns.keys())

        # Attempt to open with UTF-8, fallback to latin-1 for legacy logs
        for encoding in ("utf-8", "latin-1", "cp1252"):
            try:
                with open(path, "r", encoding=encoding, errors="replace") as f:
                    for line_idx, line in enumerate(f, start=1):
                        if max_lines and line_idx > max_lines:
                            break
                        
                        clean_line = line.strip()
                        if not clean_line:
                            continue

                        for entity_type in selected_types:
                            pattern = self.compiled_patterns.get(entity_type)
                            if not pattern:
                                continue

                            for match in pattern.finditer(clean_line):
                                matched_text = match.group(0)
                                # Generate a contextual snippet around the match
                                start = max(0, match.start() - 30)
                                end = min(len(clean_line), match.end() + 30)
                                snippet = clean_line[start:end]
                                if start > 0:
                                    snippet = "..." + snippet
                                if end < len(clean_line):
                                    snippet = snippet + "..."

                                entity = ExtractedEntity(
                                    source_file=path.name,
                                    line_number=line_idx,
                                    entity_type=entity_type,
                                    value=matched_text,
                                    context_snippet=snippet
                                )
                                results.append(entity)
                break
            except Exception:
                continue

        return results

    def parse_directory(
        self,
        directory_path: str,
        file_extensions: Optional[List[str]] = None,
        active_entity_types: Optional[List[str]] = None,
        recursive: bool = False,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
        log_callback: Optional[Callable[[str, str], None]] = None
    ) -> List[ExtractedEntity]:
        """
        Parses all matching files in a directory.
        """
        dir_path = Path(directory_path)
        if not dir_path.is_dir():
            if log_callback:
                log_callback("ERROR", f"Invalid directory: '{directory_path}'")
            return []

        allowed_exts = [e.lower() for e in (file_extensions or [".log", ".txt", ".csv", ".json", ".out", ".err"])]
        
        target_files = []
        if recursive:
            for root, _, files in os.walk(directory_path):
                for f in files:
                    if Path(f).suffix.lower() in allowed_exts:
                        target_files.append(Path(root) / f)
        else:
            for item in dir_path.iterdir():
                if item.is_file() and item.suffix.lower() in allowed_exts:
                    target_files.append(item)

        total_files = len(target_files)
        if log_callback:
            log_callback("INFO", f"Scanning {total_files} log files in '{directory_path}' for patterns...")

        all_matches: List[ExtractedEntity] = []

        for idx, file_item in enumerate(target_files, start=1):
            if log_callback:
                log_callback("DEBUG", f"Parsing '{file_item.name}'...")

            file_matches = self.parse_file(str(file_item), active_entity_types=active_entity_types)
            all_matches.extend(file_matches)

            if progress_callback:
                progress_callback(idx, total_files, f"Scanned {file_item.name} ({len(file_matches)} matches)")

        self.extracted_records = all_matches
        if log_callback:
            log_callback("SUCCESS", f"Parsing completed. Extracted {len(all_matches)} total entities from {total_files} files.")

        return all_matches

    def export_master_csv(
        self,
        output_csv_path: str,
        entities: Optional[List[ExtractedEntity]] = None,
        append_mode: bool = False,
        log_callback: Optional[Callable[[str, str], None]] = None
    ) -> Tuple[bool, int]:
        """
        Exports extracted entities to a clean, standardized master CSV file.
        Returns: (success_bool, count_written)
        """
        records_to_export = entities if entities is not None else self.extracted_records
        if not records_to_export:
            if log_callback:
                log_callback("WARN", "No entities available to export to Master CSV.")
            return False, 0

        target_file = Path(output_csv_path)
        try:
            target_file.parent.mkdir(parents=True, exist_ok=True)
            file_exists = target_file.exists() and target_file.stat().st_size > 0
            mode = "a" if append_mode else "w"

            header = ["Timestamp", "Source_File", "Line_Number", "Entity_Type", "Extracted_Value", "Context_Snippet"]

            with open(target_file, mode, newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                if not append_mode or not file_exists:
                    writer.writerow(header)

                for entity in records_to_export:
                    writer.writerow(entity.to_csv_row())

            if log_callback:
                log_callback("SUCCESS", f"Exported {len(records_to_export)} records to Master CSV: '{target_file.name}'")

            return True, len(records_to_export)

        except Exception as e:
            if log_callback:
                log_callback("ERROR", f"Failed to export Master CSV: {str(e)}")
            return False, 0

    def get_summary_stats(self, entities: Optional[List[ExtractedEntity]] = None) -> Dict[str, Any]:
        """Generates statistical distribution of extracted entities."""
        data = entities if entities is not None else self.extracted_records
        stats = {
            "total_matches": len(data),
            "by_type": {},
            "by_file": {},
            "unique_values_count": len(set(e.value for e in data))
        }

        for item in data:
            stats["by_type"][item.entity_type] = stats["by_type"].get(item.entity_type, 0) + 1
            stats["by_file"][item.source_file] = stats["by_file"].get(item.source_file, 0) + 1

        return stats
