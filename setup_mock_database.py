"""
Automated Invoice Verification Agent - Mock Database Setup
This script initializes SQLite databases for PO records and audit logging.
"""

import sqlite3
from datetime import datetime, timedelta
import os


def create_mock_database(db_path: str = "invoice_verification.db") -> sqlite3.Connection:
    """
    Create and initialize the mock PO and audit log databases.
    
    Args:
        db_path: Path to the SQLite database file
        
    Returns:
        Connection object to the database
    """
    
    # Remove existing database if it exists (for clean testing)
    if os.path.exists(db_path):
        os.remove(db_path)
    
    # Create connection
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print(f"Creating database: {db_path}")
    
    # Create purchase_orders table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS purchase_orders (
            po_number TEXT PRIMARY KEY,
            vendor_name TEXT NOT NULL,
            vendor_tax_id TEXT NOT NULL,
            expected_total_amount REAL NOT NULL,
            status TEXT NOT NULL
        )
    """)
    print("✓ Created 'purchase_orders' table")
    
    # Create audit_log table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_filename TEXT NOT NULL,
            po_number TEXT NOT NULL,
            verification_status TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            approved_by TEXT,
            FOREIGN KEY (po_number) REFERENCES purchase_orders(po_number)
        )
    """)
    print("✓ Created 'audit_log' table")
    
    # Insert mock data into purchase_orders
    mock_purchase_orders = [
        ("PO-2024-001", "Acme Corporation", "TAX-12345678", 15500.00, "ACTIVE"),
        ("PO-2024-002", "Global Supplies Inc", "TAX-87654321", 8750.50, "ACTIVE"),
        ("PO-2024-003", "Tech Solutions Ltd", "TAX-55555555", 22300.75, "ACTIVE"),
        ("PO-2024-004", "Premium Materials Co", "TAX-44444444", 5200.00, "PENDING"),
        ("PO-2024-005", "Reliable Vendors LLC", "TAX-99999999", 31450.25, "ACTIVE"),
    ]
    
    cursor.executemany("""
        INSERT INTO purchase_orders 
        (po_number, vendor_name, vendor_tax_id, expected_total_amount, status)
        VALUES (?, ?, ?, ?, ?)
    """, mock_purchase_orders)
    
    print(f"✓ Inserted {len(mock_purchase_orders)} rows into 'purchase_orders' table")
    
    # Insert sample audit log entries
    base_timestamp = datetime.now()
    mock_audit_logs = [
        ("INV-2024-001.pdf", "PO-2024-001", "PASSED", base_timestamp - timedelta(days=2), "john.smith@company.com"),
        ("INV-2024-002.pdf", "PO-2024-002", "FAILED", base_timestamp - timedelta(days=1), "jane.doe@company.com"),
        ("INV-2024-003.pdf", "PO-2024-003", "PASSED", base_timestamp - timedelta(hours=4), "john.smith@company.com"),
    ]
    
    cursor.executemany("""
        INSERT INTO audit_log 
        (invoice_filename, po_number, verification_status, timestamp, approved_by)
        VALUES (?, ?, ?, ?, ?)
    """, mock_audit_logs)
    
    print(f"✓ Inserted {len(mock_audit_logs)} rows into 'audit_log' table")
    
    # Commit changes
    conn.commit()
    
    return conn


def display_database_contents(conn: sqlite3.Connection) -> None:
    """Display the contents of both tables."""
    
    cursor = conn.cursor()
    
    print("\n" + "="*70)
    print("PURCHASE ORDERS TABLE")
    print("="*70)
    cursor.execute("SELECT * FROM purchase_orders")
    columns = [desc[0] for desc in cursor.description]
    print(f"\n{' | '.join(columns)}")
    print("-" * 70)
    
    for row in cursor.fetchall():
        print(" | ".join(str(val) for val in row))
    
    print("\n" + "="*70)
    print("AUDIT LOG TABLE")
    print("="*70)
    cursor.execute("SELECT * FROM audit_log ORDER BY timestamp DESC")
    columns = [desc[0] for desc in cursor.description]
    print(f"\n{' | '.join(columns)}")
    print("-" * 70)
    
    for row in cursor.fetchall():
        print(" | ".join(str(val) for val in row))
    
    print("\n" + "="*70)


def get_po_stats(conn: sqlite3.Connection) -> None:
    """Display basic statistics about the PO database."""
    
    cursor = conn.cursor()
    
    print("\n" + "="*70)
    print("DATABASE STATISTICS")
    print("="*70)
    
    # Count POs by status
    cursor.execute("SELECT status, COUNT(*) FROM purchase_orders GROUP BY status")
    print("\nPOs by Status:")
    for status, count in cursor.fetchall():
        print(f"  {status}: {count}")
    
    # Total PO value
    cursor.execute("SELECT SUM(expected_total_amount) FROM purchase_orders")
    total = cursor.fetchone()[0]
    print(f"\nTotal PO Value: ${total:,.2f}")
    
    # Verification statistics
    cursor.execute("SELECT verification_status, COUNT(*) FROM audit_log GROUP BY verification_status")
    print("\nVerification Results:")
    for status, count in cursor.fetchall():
        print(f"  {status}: {count}")


if __name__ == "__main__":
    # Create the database
    conn = create_mock_database()
    
    # Display contents
    display_database_contents(conn)
    
    # Display statistics
    get_po_stats(conn)
    
    # Close connection
    conn.close()
    
    print("\n✅ Database initialization complete!")
    print("   Database file: invoice_verification.db")
