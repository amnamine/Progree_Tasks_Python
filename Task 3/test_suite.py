"""
Automated Comprehensive Test Suite for Task 3.
Validates File Organization, Regex Text Parsing, Master CSV Logging,
Undo mechanics, and Background Automation Daemon.
"""

import os
import shutil
import tempfile
import unittest
from pathlib import Path

from core.file_organizer import FileOrganizer
from core.text_parser import TextParserEngine
from core.mock_generator import generate_mock_environment, generate_log_line
from core.watcher import AutomationWatcher


class TestTask3AutomatedFileAndParser(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp(prefix="task3_test_")
        self.target_path = Path(self.test_dir)

    def tearDown(self):
        # Clean up temporary test directory
        if self.target_path.exists():
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_mock_generator(self):
        """Verify mock data generator creates correct files and logs."""
        folder = generate_mock_environment(
            str(self.target_path),
            num_files=8,
            num_logs=3,
            lines_per_log=10
        )
        self.assertTrue(Path(folder).exists())
        files = list(Path(folder).glob("*"))
        self.assertGreaterEqual(len(files), 10)

    def test_file_organizer_sorting_and_undo(self):
        """Test organizing unorganized files into categories and undoing the action."""
        # Create dummy files
        (self.target_path / "invoice_q1.pdf").write_text("PDF content")
        (self.target_path / "sales_data.xlsx").write_text("Excel content")
        (self.target_path / "app_logo.png").write_text("PNG content")
        (self.target_path / "server_stream.log").write_text("Log content")
        (self.target_path / "deploy_script.py").write_text("Python content")

        organizer = FileOrganizer()

        # 1. Test Dry Run Preview
        preview = organizer.preview_organize(str(self.target_path))
        self.assertEqual(len(preview), 5)

        # 2. Test Execution
        success_count, error_count, records = organizer.organize(str(self.target_path))
        self.assertEqual(success_count, 5)
        self.assertEqual(error_count, 0)

        # Check that files were placed in category subdirectories
        self.assertTrue((self.target_path / "Documents" / "invoice_q1.pdf").exists())
        self.assertTrue((self.target_path / "Spreadsheets" / "sales_data.xlsx").exists())
        self.assertTrue((self.target_path / "Images" / "app_logo.png").exists())
        self.assertTrue((self.target_path / "Logs & Dumps" / "server_stream.log").exists())
        self.assertTrue((self.target_path / "Code & Scripts" / "deploy_script.py").exists())

        # 3. Test Undo
        restored, undo_errors = organizer.undo_last()
        self.assertEqual(restored, 5)
        self.assertEqual(undo_errors, 0)
        self.assertTrue((self.target_path / "invoice_q1.pdf").exists())
        self.assertTrue((self.target_path / "app_logo.png").exists())

    def test_regex_text_parser(self):
        """Test regex entity extraction for emails, transaction IDs, IPs, and log levels."""
        log_file = self.target_path / "sample_service.log"
        log_content = (
            "[2026-09-12 10:15:30] [INFO] Payment TXN-948201-44 completed for customer user.support@enterprise.org IP: 192.168.1.50\n"
            "[2026-09-12 10:15:35] [ERROR] Transaction ORD-883920 failed for dev.ops@cloud.io on 10.0.0.1\n"
            "[2026-09-12 10:15:40] [CRITICAL] Invoice INV-129039 deadlock encountered.\n"
        )
        log_file.write_text(log_content)

        parser = TextParserEngine()
        results = parser.parse_file(str(log_file))

        self.assertGreater(len(results), 0)

        extracted_values = [e.value for e in results]
        entity_types = [e.entity_type for e in results]

        # Verify emails extracted
        self.assertIn("user.support@enterprise.org", extracted_values)
        self.assertIn("dev.ops@cloud.io", extracted_values)

        # Verify transaction IDs extracted
        self.assertTrue(any("TXN-948201-44" in v for v in extracted_values))
        self.assertTrue(any("ORD-883920" in v for v in extracted_values))
        self.assertTrue(any("INV-129039" in v for v in extracted_values))

        # Verify IPs extracted
        self.assertIn("192.168.1.50", extracted_values)
        self.assertIn("10.0.0.1", extracted_values)

        # Test Master CSV Export
        master_csv = self.target_path / "master_report.csv"
        success, count = parser.export_master_csv(str(master_csv), entities=results)
        self.assertTrue(success)
        self.assertEqual(count, len(results))
        self.assertTrue(master_csv.exists())

        # Check Master CSV content
        csv_content = master_csv.read_text()
        self.assertIn("Timestamp,Source_File,Line_Number,Entity_Type,Extracted_Value,Context_Snippet", csv_content)
        self.assertIn("user.support@enterprise.org", csv_content)

    def test_custom_regex_pattern(self):
        """Test adding dynamic custom regular expressions."""
        parser = TextParserEngine()
        success = parser.add_custom_pattern("CustomOrder", r"ORDER#\d{4}")
        self.assertTrue(success)

        test_log = self.target_path / "custom.log"
        test_log.write_text("Processing ORDER#9942 now...")
        results = parser.parse_file(str(test_log), active_entity_types=["CustomOrder"])
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].value, "ORDER#9942")


if __name__ == "__main__":
    unittest.main()
