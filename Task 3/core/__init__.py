"""Core automation and parsing package."""
from core.file_organizer import FileOrganizer, FileMoveRecord
from core.text_parser import TextParserEngine, ExtractedEntity
from core.watcher import AutomationWatcher
from core.mock_generator import generate_mock_environment

__all__ = [
    "FileOrganizer",
    "FileMoveRecord",
    "TextParserEngine",
    "ExtractedEntity",
    "AutomationWatcher",
    "generate_mock_environment"
]
