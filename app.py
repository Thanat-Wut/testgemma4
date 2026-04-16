"""
Invoice Verification Agent - Streamlit Web Application
A complete workflow for finance staff to verify invoices against POs.
"""

import streamlit as st
import sqlite3
import pandas as pd
import json
from datetime import datetime
import os
import atexit
from io import BytesIO

# PDF text extraction
try:
    from pypdf import PdfReader
except ImportError:
    from PyPDF2 import PdfReader

# Import functions from the invoice verification module
from invoice_verification_agent import extract_invoice_data, verify_against_po, log_verification_result


# Page configuration
st.set_page_config(
    page_title="Invoice Verification Agent",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Custom CSS for styling
st.markdown("""
    <style>
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 15px;
        margin: 10px 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        padding: 15px;
        margin: 10px 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 5px;
        padding: 15px;
        margin: 10px 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 5px;
        padding: 15px;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)


def extract_text_from_pdf(pdf_bytes):
    """Extract text from PDF file."""
    try:
        pdf_reader = PdfReader(BytesIO(pdf_bytes))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text.strip() if text.strip() else None
    except Exception as e:
        print(f"PDF extraction error: {e}")
        return None


def extract_file_content(uploaded_file):
    """Extract text content from uploaded file (PDF or text)."""
    try:
        file_bytes = uploaded_file.read()
        filename = uploaded_file.name.lower()
        
        # Try PDF first if it looks like a PDF
        if filename.endswith('.pdf'):
            pdf_text = extract_text_from_pdf(file_bytes)
            if pdf_text:
                print(f"✓ Extracted {len(pdf_text)} characters from PDF")
                return pdf_text
        
        # Try UTF-8 text decoding (for text files, images with OCR might fail)
        try:
            text = file_bytes.decode('utf-8', errors='ignore')
            if text.strip():
                print(f"✓ Extracted {len(text)} characters from text file")
                return text
        except:
            pass
        
        # If we got here, we couldn't extract meaningful content
        return None
        
    except Exception as e:
        print(f"File extraction error: {e}")
        return None


@st.cache_resource
def get_db_connection():
    """Get or create database connection."""
    # Auto-initialize database if missing (Bug #1)
    if not os.path.exists("invoice_verification.db"):
        st.info("🗄️ Initializing database...")
        try:
            from setup_mock_database import create_mock_database
            create_mock_database()
            st.success("✅ Database initialized successfully")
        except Exception as e:
            st.error(f"❌ Failed to initialize database: {str(e)}")
            st.stop()
    
    conn = sqlite3.connect("invoice_verification.db", check_same_thread=False)
    
    # Register cleanup on exit (Bug #13)
    def cleanup():
        try:
            conn.close()
            print("🔌 Database connection closed")
        except:
            pass
    
    atexit.register(cleanup)
    return conn


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    # Note: Removed unused approval_status tracking (Bug #11)
    pass


def format_currency(value):
    """Format value as currency."""
    return f"${value:,.2f}"


def send_notification(status: str, message: str, invoice_filename: str):
    """Simulate sending notifications via LINE Notify or Email."""
    notification_msg = f"""
    📧 **Notification Alert**
    
    Invoice: {invoice_filename}
    Status: {status}
    Message: {message}
    Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    
    **Notification simulated to:**
    - 📱 LINE Notify
    - 📧 Email: finance-alerts@company.com
    """
    return notification_msg


def export_audit_log_to_csv(db_connection):
    """Export audit log to CSV format."""
    try:
        query = "SELECT * FROM audit_log ORDER BY timestamp DESC"
        df = pd.read_sql_query(query, db_connection)
        
        # Format the dataframe
        df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
        
        # Convert to CSV
        csv_data = df.to_csv(index=False)
        return csv_data, df
    except Exception as e:
        st.error(f"Error exporting audit log: {str(e)}")
        return None, None


def display_invoice_summary(invoice_json: dict):
    """Display invoice data in a formatted way."""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Company Name", invoice_json.get("company_name", "N/A"))
    
    with col2:
        st.metric("Tax ID", invoice_json.get("tax_id", "N/A"))
    
    with col3:
        st.metric("Grand Total", format_currency(invoice_json.get("grand_total", 0)))
    
    # Display items
    if "items" in invoice_json and invoice_json["items"]:
        st.subheader("Invoice Items")
        items_data = []
        for item in invoice_json["items"]:
            items_data.append({
                "Item Name": item.get("name", "N/A"),
                "Quantity": item.get("qty", 0),
                "Unit Price": format_currency(item.get("unit_price", 0)),
                "Total Price": format_currency(item.get("total_price", 0))
            })
        st.dataframe(items_data, width='stretch')


def display_po_details(db_connection, po_number: str):
    """Display PO details from database."""
    try:
        cursor = db_connection.cursor()
        cursor.execute(
            "SELECT po_number, vendor_name, vendor_tax_id, expected_total_amount, status FROM purchase_orders WHERE po_number = ?",
            (po_number,)
        )
        po_record = cursor.fetchone()
        
        if po_record:
            st.subheader("PO Details (from Database)")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("PO Number", po_record[0])
            with col2:
                st.metric("Vendor Name", po_record[1])
            with col3:
                st.metric("Expected Amount", format_currency(po_record[3]))
            with col4:
                st.metric("PO Status", po_record[4])
            
            return po_record
    except Exception as e:
        st.error(f"Error fetching PO details: {str(e)}")
        return None


def main():
    """Main Streamlit application."""
    
    initialize_session_state()
    db_connection = get_db_connection()
    
    # Header
    st.title("📋 Automated Invoice Verification Agent")
    st.markdown("*Finance Staff Portal - Verify Invoices Against Purchase Orders*")
    st.divider()
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Application Settings")
        approver_email = st.text_input(
            "Approver Email",
            value="finance-staff@company.com",
            help="Your email for audit trail"
        )
        
        st.divider()
        
        # Database Info
        st.subheader("📊 Database Info")
        try:
            cursor = db_connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM purchase_orders")
            po_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM audit_log")
            log_count = cursor.fetchone()[0]
            
            st.metric("Total POs", po_count)
            st.metric("Audit Log Entries", log_count)
        except Exception as e:
            st.warning(f"Database error: {str(e)}")
    
    # Main Content - Tabs
    tab1, tab2, tab3 = st.tabs(["📤 Upload & Verify", "📊 Audit Log", "ℹ️ Help"])
    
    # ==================== TAB 1: UPLOAD & VERIFY ====================
    with tab1:
        st.header("Upload Invoice Files")
        st.markdown("Upload PDF or image files containing invoice data for verification.")
        
        # File uploader
        uploaded_files = st.file_uploader(
            "Choose invoice file(s)",
            type=["pdf", "png", "jpg", "jpeg", "gif"],
            accept_multiple_files=True,
            help="Upload one or more invoice files"
        )
        
        if uploaded_files:
            st.success(f"✅ {len(uploaded_files)} file(s) uploaded")
            
            for uploaded_file in uploaded_files:
                st.divider()
                
                invoice_filename = uploaded_file.name
                st.subheader(f"Processing: {invoice_filename}")
                
                # Create a container for each invoice
                with st.container(border=True):
                    
                    try:
                        # Step 1: Extract invoice data (Bug #5: Read actual file content)
                        with st.spinner("🤖 Extracting invoice data using LLM..."):
                            file_content = extract_file_content(uploaded_file)
                            
                            if not file_content:
                                st.error("❌ Could not extract text from file. Please ensure:")
                                st.write("- File is a valid PDF or text document")
                                st.write("- Text is readable (not scanned image)")
                                st.write("- File is not corrupted")
                                st.stop()
                            
                            invoice_data = extract_invoice_data(file_content)
                        
                        st.success("✓ Invoice data extracted successfully")
                        
                        # Display extracted data
                        with st.expander("📄 View Extracted Invoice Data", expanded=True):
                            display_invoice_summary(invoice_data)
                            st.json(invoice_data)
                        
                        # Step 2: Verify against PO
                        with st.spinner("🔍 Verifying against PO database..."):
                            verification_status, verification_message = verify_against_po(
                                invoice_data, 
                                db_connection
                            )
                        
                        # Display PO details
                        po_number = invoice_data.get("po_number")
                        po_details = display_po_details(db_connection, po_number)
                        
                        # Step 3: Display verification result
                        st.divider()
                        
                        if verification_status == "PASSED":
                            st.markdown(
                                '<div class="success-box"><h3>✅ VERIFICATION PASSED</h3><p>' + 
                                verification_message + 
                                '</p></div>',
                                unsafe_allow_html=True
                            )
                            
                            # Show approval buttons for PASSED invoices
                            st.subheader("Human-in-the-Loop Approval")
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                if st.button("✅ Approve", key=f"approve_{invoice_filename}"):
                                    # Log approval to audit trail
                                    log_id = log_verification_result(
                                        db_connection,
                                        invoice_filename,
                                        po_number,
                                        "PASSED",
                                        approver_email
                                    )
                                    
                                    st.markdown(
                                        '<div class="success-box"><h4>✅ Invoice Approved!</h4>' +
                                        f'<p>Audit Log ID: {log_id}</p>' +
                                        f'<p>Approver: {approver_email}</p>' +
                                        f'<p>Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>' +
                                        '<p><strong>Simulation:</strong> Invoice sent to ERP system (SAP/NetSuite)</p>' +
                                        '</div>',
                                        unsafe_allow_html=True
                                    )
                                    
                                    st.balloons()
                            
                            with col2:
                                if st.button("❌ Reject", key=f"reject_{invoice_filename}"):
                                    st.markdown(
                                        '<div class="error-box"><h4>❌ Invoice Rejected</h4>' +
                                        '<p>Please review the invoice and resubmit after corrections.</p>' +
                                        '</div>',
                                        unsafe_allow_html=True
                                    )
                        
                        elif verification_status == "FAILED":
                            st.markdown(
                                '<div class="error-box"><h3>❌ VERIFICATION FAILED</h3><p>' + 
                                verification_message + 
                                '</p></div>',
                                unsafe_allow_html=True
                            )
                            
                            # Send alert notification
                            st.subheader("Alert Notification")
                            alert_msg = send_notification("FAILED", verification_message, invoice_filename)
                            st.markdown(
                                '<div class="info-box"><p>' + alert_msg.replace('\n', '<br>') + '</p></div>',
                                unsafe_allow_html=True
                            )
                            
                            # Log the failed verification
                            log_id = log_verification_result(
                                db_connection,
                                invoice_filename,
                                po_number,
                                "FAILED",
                                approver_email
                            )
                            st.info(f"Logged to audit trail (ID: {log_id})")
                        
                        else:  # ERROR
                            st.markdown(
                                '<div class="warning-box"><h3>⚠️ VERIFICATION ERROR</h3><p>' + 
                                verification_message + 
                                '</p></div>',
                                unsafe_allow_html=True
                            )
                            
                            # Send alert notification
                            st.subheader("Alert Notification")
                            alert_msg = send_notification("ERROR", verification_message, invoice_filename)
                            st.markdown(
                                '<div class="info-box"><p>' + alert_msg.replace('\n', '<br>') + '</p></div>',
                                unsafe_allow_html=True
                            )
                            
                            # Log the error
                            log_id = log_verification_result(
                                db_connection,
                                invoice_filename,
                                po_number,
                                "ERROR",
                                approver_email
                            )
                            st.warning(f"Logged to audit trail (ID: {log_id})")
                    
                    except Exception as e:
                        st.error(f"Error processing file: {str(e)}")
    
    # ==================== TAB 2: AUDIT LOG ====================
    with tab2:
        st.header("Audit Log & Export")
        st.markdown("View all verification results and export to CSV.")
        
        # Display audit log
        try:
            query = "SELECT log_id, invoice_filename, po_number, verification_status, timestamp, approved_by FROM audit_log ORDER BY timestamp DESC"
            df = pd.read_sql_query(query, db_connection)
            
            if not df.empty:
                # Format timestamp (Bug #12: Optimized conversion)
                df['timestamp'] = df['timestamp'].astype(str).str[:19]
                
                # Display with color coding
                st.subheader("All Verification Records")
                st.dataframe(df, width='stretch', hide_index=True)
                
                # Statistics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    passed_count = len(df[df['verification_status'] == 'PASSED'])
                    st.metric("✅ Passed", passed_count)
                with col2:
                    failed_count = len(df[df['verification_status'] == 'FAILED'])
                    st.metric("❌ Failed", failed_count)
                with col3:
                    error_count = len(df[df['verification_status'] == 'ERROR'])
                    st.metric("⚠️ Errors", error_count)
                with col4:
                    total_count = len(df)
                    st.metric("📊 Total", total_count)
                
                st.divider()
                
                # Export to CSV
                st.subheader("Export Audit Log")
                csv_data, export_df = export_audit_log_to_csv(db_connection)
                
                if csv_data:
                    st.download_button(
                        label="📥 Download Audit Log as CSV",
                        data=csv_data,
                        file_name=f"audit_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        help="Download the complete audit log as a CSV file"
                    )
                    
                    st.success("✓ CSV export is ready for download")
            else:
                st.info("No audit log entries yet. Upload and verify invoices to generate audit trails.")
        
        except Exception as e:
            st.error(f"Error loading audit log: {str(e)}")
    
    # ==================== TAB 3: HELP ====================
    with tab3:
        st.header("Help & Documentation")
        
        st.subheader("📖 How to Use")
        st.markdown("""
        1. **Upload Invoice**: Click on the file uploader to select PDF or image files
        2. **Extract Data**: The system uses a Local LLM (Gemma) to extract invoice details
        3. **Verify**: Invoice data is automatically verified against the PO database
        4. **Review Results**: Check the verification status (PASSED/FAILED/ERROR)
        5. **Approve**: For PASSED invoices, click 'Approve' to send to ERP
        6. **Track**: All actions are logged to the audit trail
        """)
        
        st.subheader("✅ Verification Rules")
        st.markdown("""
        - **PASSED**: PO exists and invoice total matches PO expected amount
        - **FAILED**: PO exists but amounts don't match (possible overcharge)
        - **ERROR**: PO not found in database (missing purchase order)
        """)
        
        st.subheader("🔔 Notifications")
        st.markdown("""
        - FAILED/ERROR invoices trigger alerts via:
          - 📱 LINE Notify
          - 📧 Email (finance-alerts@company.com)
        """)
        
        st.subheader("📊 Database Info")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Purchase Orders Table:**")
            try:
                cursor = db_connection.cursor()
                cursor.execute("SELECT COUNT(*) FROM purchase_orders")
                po_count = cursor.fetchone()[0]
                st.write(f"- Total POs: {po_count}")
                
                cursor.execute("SELECT SUM(expected_total_amount) FROM purchase_orders")
                total_value = cursor.fetchone()[0]
                st.write(f"- Total PO Value: {format_currency(total_value)}")
            except Exception as e:
                st.warning(f"Error: {str(e)}")
        
        with col2:
            st.write("**Audit Log Table:**")
            try:
                cursor = db_connection.cursor()
                cursor.execute("SELECT COUNT(*) FROM audit_log")
                log_count = cursor.fetchone()[0]
                st.write(f"- Total Entries: {log_count}")
                
                cursor.execute("SELECT COUNT(*) FROM audit_log WHERE verification_status = 'PASSED'")
                passed_count = cursor.fetchone()[0]
                st.write(f"- Successfully Verified: {passed_count}")
            except Exception as e:
                st.warning(f"Error: {str(e)}")
        
        st.subheader("🛠️ System Architecture")
        st.info("""
        **Components:**
        - **Database**: SQLite with purchase_orders and audit_log tables
        - **Extraction**: Mock LLM (simulates Gemma) for invoice data extraction
        - **Verification**: PO database matching and amount validation
        - **UI**: Streamlit web application for finance staff
        - **Notifications**: Simulated LINE Notify and Email alerts
        - **Export**: CSV download capability for audit reports
        """)


if __name__ == "__main__":
    main()
