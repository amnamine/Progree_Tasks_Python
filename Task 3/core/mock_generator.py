"""
Mock Data Generator.
Creates a realistic unorganized test directory with messy files and rich log streams
containing emails, transaction IDs, IP addresses, timestamps, and error codes for testing.
"""

import os
import random
import time
from pathlib import Path
from typing import Optional, Callable


SAMPLE_EMAILS = [
    "alex.smith@enterprise.co.uk", "billing@globalpay-gateway.io", "support.desk@cloudservice.net",
    "sarah_connor@techcorp.internal", "dev.ops@kubernetes-cluster.dev", "customer.care@ecommerce-store.shop",
    "security-alert@auth0-monitor.com", "accounting@fintech-solutions.org", "contact@freelancer-portal.de"
]

SAMPLE_TXN_PREFIXES = ["TXN", "TRX", "ORD", "PAY", "INV", "REF"]
SAMPLE_IPS = ["192.168.1.105", "10.0.4.52", "172.16.254.1", "198.51.100.42", "203.0.113.195", "127.0.0.1", "8.8.8.8"]
SAMPLE_ENDPOINTS = [
    "https://api.stripe.com/v1/charges", "https://auth.company.com/oauth/v2/token",
    "https://gateway.payment.io/api/checkout", "https://cdn.assets.org/images/logo.png"
]
LOG_LEVELS = ["INFO", "WARN", "WARNING", "ERROR", "CRITICAL", "DEBUG"]

SAMPLE_FILE_NAMES = [
    ("Quarterly_Financial_Report_Q3.pdf", "Financial summary document content..."),
    ("Annual_Tax_Assessment.docx", "Tax documentation notes and deductions..."),
    ("Employee_Salaries_2026.xlsx", "Name, Department, Salary\nJohn, Eng, $110,000\nJane, Product, $125,000"),
    ("Customer_Export_Sept.csv", "id,name,email\n1,Alice,alice@example.com\n2,Bob,bob@corp.io"),
    ("App_Architecture_Diagram.png", "PNG_BINARY_MOCK_DATA_01010101"),
    ("Company_Header_Banner.jpg", "JPEG_IMAGE_STREAM_01100110"),
    ("System_Icon_Set.svg", "<svg><circle cx='50' cy='50' r='40'/></svg>"),
    ("Meeting_Recording_Sync.mp3", "AUDIO_STREAM_BINARY_MOCK"),
    ("Product_Demo_Video.mp4", "VIDEO_H264_DATA_STREAM"),
    ("Backup_Database_Dump.zip", "PK_ZIP_HEADER_DUMMY_ARCHIVE"),
    ("Database_Migration_Script.sql", "CREATE TABLE users (id INT PRIMARY KEY, email VARCHAR(255));"),
    ("deploy_production_worker.py", "import os\nprint('Deploying cluster...')"),
    ("server_environment_config.env", "DB_HOST=127.0.0.1\nPORT=5432\nAPI_KEY=sk_test_9482947192"),
    ("Software_Installer_v3.exe", "MZ_EXECUTABLE_BINARY_PAYLOAD"),
]


def generate_log_line(index: int) -> str:
    """Generates a realistic structured/semi-structured server log line."""
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    level = random.choice(LOG_LEVELS)
    ip = random.choice(SAMPLE_IPS)
    email = random.choice(SAMPLE_EMAILS)
    prefix = random.choice(SAMPLE_TXN_PREFIXES)
    txn_id = f"{prefix}-{random.randint(100000, 999999)}-{random.randint(10, 99)}"
    amount = f"${random.randint(15, 4500)}.{random.randint(10, 99):02d}"
    phone = f"+1-{random.randint(200, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
    endpoint = random.choice(SAMPLE_ENDPOINTS)

    templates = [
        f"[{now}] [{level}] [IP: {ip}] Payment completed for user '{email}' with Transaction ID: {txn_id} (Amount: {amount}) via {endpoint}",
        f"[{now}] [{level}] User {email} requested password reset from {ip}. Audit Phone: {phone}",
        f"[{now}] [ERROR] Gateway timeout while processing invoice {txn_id} for client '{email}'. Endpoint: {endpoint}",
        f"[{now}] [{level}] Order checkout verified: ID={txn_id}, Total={amount}, Buyer={email}, SourceIP={ip}",
        f"[{now}] [CRITICAL] Database deadlock detected on transaction {txn_id}. Alert dispatched to {email}"
    ]
    return random.choice(templates)


def generate_mock_environment(
    target_directory: str,
    num_files: int = 15,
    num_logs: int = 4,
    lines_per_log: int = 40,
    log_callback: Optional[Callable[[str, str], None]] = None
) -> str:
    """
    Populates target_directory with messy unorganized files and flat logs.
    """
    target_path = Path(target_directory)
    target_path.mkdir(parents=True, exist_ok=True)

    if log_callback:
        log_callback("INFO", f"Generating sample mock dataset in '{target_directory}'...")

    # 1. Create standard mixed files
    created_count = 0
    selected_samples = random.sample(SAMPLE_FILE_NAMES, min(num_files, len(SAMPLE_FILE_NAMES)))
    for fname, content in selected_samples:
        file_dest = target_path / fname
        with open(file_dest, "w", encoding="utf-8") as f:
            f.write(content)
        created_count += 1

    # 2. Create rich log files with emails, transaction IDs, IPs, etc.
    log_names = [
        "payment_gateway_audit.log",
        "auth_security_events.log",
        "order_processing_stream.txt",
        "server_diagnostics.err",
        "billing_transactions.log"
    ]

    for i in range(min(num_logs, len(log_names))):
        log_name = log_names[i]
        log_dest = target_path / log_name
        with open(log_dest, "w", encoding="utf-8") as f:
            for line_no in range(lines_per_log):
                f.write(generate_log_line(line_no) + "\n")
        created_count += 1

    if log_callback:
        log_callback("SUCCESS", f"Mock environment ready! Created {created_count} test files in '{target_path.name}/'.")

    return str(target_path.resolve())
