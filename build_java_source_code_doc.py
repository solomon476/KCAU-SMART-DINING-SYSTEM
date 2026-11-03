#!/usr/bin/env python3
"""
KCAU SMART DINING SYSTEM - JAVA SOURCE CODE DOCUMENT GENERATOR
Generates:
  1. KCAU_SMART_DINING_JAVA_SOURCE_CODE.docx
  2. KCAU_SMART_DINING_JAVA_SOURCE_CODE.pdf

Complies strictly with CAT 1 guidelines:
- Consolas monospaced font
- Class name as heading
- Complete source code with package declarations and imports preserved
- Each class begins on a new page
- Accurate ordering: Server, User, MenuItem, Order, OrderItem, and all implemented backend classes.
"""

import os
import sys
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn
import pygments
from pygments.lexers import JavaLexer
from pygments.token import Token

BASE_DIR = "/home/kali/Honeypot"
DOCX_OUT = os.path.join(BASE_DIR, "KCAU_SMART_DINING_JAVA_SOURCE_CODE.docx")
PDF_OUT = os.path.join(BASE_DIR, "KCAU_SMART_DINING_JAVA_SOURCE_CODE.pdf")

# Define the ordered classes per user specifications
JAVA_CLASSES = [
    {
        "num": 1,
        "name": "Server.java",
        "pkg": "com.kcau.dining",
        "path": "src/main/java/com/kcau/dining/Server.java",
        "tier": "Core Server & REST Dispatcher",
        "role": "Central Virtual-Thread HTTP server entrypoint. Initializes SQLite database schema, binds HTTP listener (port 3000), registers REST API context handlers, serves static web assets with SPA fallback, and manages CORS headers."
    },
    {
        "num": 2,
        "name": "User.java",
        "pkg": "com.kcau.dining.model",
        "path": "src/main/java/com/kcau/dining/model/User.java",
        "tier": "Domain Model",
        "role": "Encapsulates user profile and authentication identity. Stores unique user ID, full name, student ID / username, PBKDF2 password hash, and authorization role ('student', 'staff', or 'admin')."
    },
    {
        "num": 3,
        "name": "MenuItem.java",
        "pkg": "com.kcau.dining.model",
        "path": "src/main/java/com/kcau/dining/model/MenuItem.java",
        "tier": "Domain Model",
        "role": "Represents cafeteria food and drink catalog items. Stores item ID, name, description, price (KES), category classification ('breakfast', 'lunch', 'drinks', 'fruits', 'snacks'), image URL, and stock availability flag."
    },
    {
        "num": 4,
        "name": "Order.java",
        "pkg": "com.kcau.dining.model",
        "path": "src/main/java/com/kcau/dining/model/Order.java",
        "tier": "Domain Model",
        "role": "Customer order header entity. Contains order UUID, student/customer ID, customer name, total amount (KES), lifecycle state ('PENDING', 'PREPARING', 'READY', 'COLLECTED', 'CANCELLED'), creation timestamp, and child OrderItem list."
    },
    {
        "num": 5,
        "name": "OrderItem.java",
        "pkg": "com.kcau.dining.model",
        "path": "src/main/java/com/kcau/dining/model/OrderItem.java",
        "tier": "Domain Model",
        "role": "Represents a distinct line item within a customer order. Tracks internal row ID, foreign key reference to order ID, food item ID, food item name, unit price (KES), quantity ordered, and calculates line subtotal."
    },
    {
        "num": 6,
        "name": "Payment.java",
        "pkg": "com.kcau.dining.model",
        "path": "src/main/java/com/kcau/dining/model/Payment.java",
        "tier": "Domain Model",
        "role": "Represents a financial transaction record in the cafeteria ledger. Tracks payment ID, order ID reference, payment method ('MPESA', 'CASH', 'CARD'), amount (KES), transaction reference code, status, and completion timestamp."
    },
    {
        "num": 7,
        "name": "DatabaseConnection.java",
        "pkg": "com.kcau.dining.database",
        "path": "src/main/java/com/kcau/dining/database/DatabaseConnection.java",
        "tier": "Persistence Infrastructure",
        "role": "Provides thread-safe JDBC connection pooling to the local SQLite database ('data/dining.db'). Ensures automatic directory creation and reliable connection retrieval across parallel virtual threads."
    },
    {
        "num": 8,
        "name": "DatabaseInitializer.java",
        "pkg": "com.kcau.dining.database",
        "path": "src/main/java/com/kcau/dining/database/DatabaseInitializer.java",
        "tier": "Persistence Infrastructure",
        "role": "Executes automated DDL table definitions with foreign keys for users, menu_items, orders, order_items, and payments. Seeds initial accounts (students, kitchen staff, admin) and 12+ cafeteria menu items."
    },
    {
        "num": 9,
        "name": "UserService.java",
        "pkg": "com.kcau.dining.service",
        "path": "src/main/java/com/kcau/dining/service/UserService.java",
        "tier": "Business Logic Service",
        "role": "Coordinates user management operations: student and staff registration, cryptographic PBKDF2 password hashing with random salt, credential authentication, JWT token payload construction, and administrative role updates."
    },
    {
        "num": 10,
        "name": "MenuService.java",
        "pkg": "com.kcau.dining.service",
        "path": "src/main/java/com/kcau/dining/service/MenuService.java",
        "tier": "Business Logic Service",
        "role": "Encapsulates cafeteria food catalog business logic. Manages category-based menu retrieval, stock availability toggling (In Stock vs Sold Out), administrative dish creation, and dish deletion."
    },
    {
        "num": 11,
        "name": "OrderService.java",
        "pkg": "com.kcau.dining.service",
        "path": "src/main/java/com/kcau/dining/service/OrderService.java",
        "tier": "Business Logic Service",
        "role": "Implements ACID transactional order processing with batch insertion of line items. Queries kitchen display queue orders, retrieves student order history, and advances order lifecycle status."
    },
    {
        "num": 12,
        "name": "PaymentService.java",
        "pkg": "com.kcau.dining.service",
        "path": "src/main/java/com/kcau/dining/service/PaymentService.java",
        "tier": "Business Logic Service",
        "role": "Processes simulated M-Pesa STK push and cash payments. Records receipts into the payments ledger, validates payment totals against order records, and lists payment audits."
    },
    {
        "num": 13,
        "name": "ReportService.java",
        "pkg": "com.kcau.dining.service",
        "path": "src/main/java/com/kcau/dining/service/ReportService.java",
        "tier": "Business Logic Service",
        "role": "Aggregates real-time cafeteria analytics. Computes total sales revenue, order volumes, order status distribution, and top-selling food items ranked by unit count and revenue."
    },
    {
        "num": 14,
        "name": "HttpHelper.java",
        "pkg": "com.kcau.dining.handler",
        "path": "src/main/java/com/kcau/dining/handler/HttpHelper.java",
        "tier": "REST & Security Infrastructure",
        "role": "Zero-dependency HTTP and security utility engine. Handles request body reading, URL query parameter parsing, JSON serialization/deserialization, CORS preflight headers, PBKDF2 hashing, and HMAC-SHA256 JWT tokens."
    },
    {
        "num": 15,
        "name": "UserHandler.java",
        "pkg": "com.kcau.dining.handler",
        "path": "src/main/java/com/kcau/dining/handler/UserHandler.java",
        "tier": "REST API Controller",
        "role": "Dispatches requests for /api/signup, /api/login, /api/me, and /api/users. Enforces input validation, returns signed JWT bearer tokens, and restricts role modification to administrators."
    },
    {
        "num": 16,
        "name": "MenuHandler.java",
        "pkg": "com.kcau.dining.handler",
        "path": "src/main/java/com/kcau/dining/handler/MenuHandler.java",
        "tier": "REST API Controller",
        "role": "Dispatches requests for /api/menu and /api/menu/availability. Handles GET (filtered catalog), POST (adding new dishes by admin), and PUT (toggling stock status by kitchen staff or admin)."
    },
    {
        "num": 17,
        "name": "OrderHandler.java",
        "pkg": "com.kcau.dining.handler",
        "path": "src/main/java/com/kcau/dining/handler/OrderHandler.java",
        "tier": "REST API Controller",
        "role": "Dispatches requests for /api/orders and /api/orders/status. Handles POST (atomic customer checkout with multiple line items), GET (kitchen queue orders), and PUT (updating order workflow status)."
    },
    {
        "num": 18,
        "name": "PaymentHandler.java",
        "pkg": "com.kcau.dining.handler",
        "path": "src/main/java/com/kcau/dining/handler/PaymentHandler.java",
        "tier": "REST API Controller",
        "role": "Dispatches requests for /api/payments. Handles POST (recording simulated M-Pesa STK push transactions) and GET (retrieving payment audit records)."
    },
    {
        "num": 19,
        "name": "ReportHandler.java",
        "pkg": "com.kcau.dining.handler",
        "path": "src/main/java/com/kcau/dining/handler/ReportHandler.java",
        "tier": "REST API Controller",
        "role": "Dispatches requests for /api/reports/summary (system KPI totals, active revenue) and /api/reports/sales (dish sales ranking and distribution)."
    },
    {
        "num": 20,
        "name": "Server.java (Root Entrypoint)",
        "pkg": "(default package)",
        "path": "Server.java",
        "tier": "Root Application Launcher",
        "role": "Convenience root-level bootstrap launcher. Dynamically loads and runs com.kcau.dining.Server via reflection or process invocation with bundled libraries from lib/*."
    },
    {
        "num": 21,
        "name": "User.java (Root Model Alias)",
        "pkg": "(default package)",
        "path": "User.java",
        "tier": "Architectural Compatibility Alias",
        "role": "Root-level compatibility model extending com.kcau.dining.model.User. Allows seamless root-level imports and standalone compilation."
    },
    {
        "num": 22,
        "name": "MenuItem.java (Root Model Alias)",
        "pkg": "(default package)",
        "path": "MenuItem.java",
        "tier": "Architectural Compatibility Alias",
        "role": "Root-level compatibility model extending com.kcau.dining.model.MenuItem. Supports backward compatibility for root-level class inspections."
    },
    {
        "num": 23,
        "name": "Order.java (Root Model Alias)",
        "pkg": "(default package)",
        "path": "Order.java",
        "tier": "Architectural Compatibility Alias",
        "role": "Root-level compatibility model extending com.kcau.dining.model.Order. Preserves root model inheritance and backward compatibility."
    }
]

ns_w = nsdecls("w")

def apply_consolas(run, size_pt=8.2, color=None, bold=False, italic=False):
    run.font.name = "Consolas"
    run.font.size = Pt(size_pt)
    run.bold = bold
    run.italic = italic
    if color:
        run.font.color.rgb = color
    # Add w:rFonts explicitly for robust Consolas rendering across Word & LibreOffice
    rPr = run._r.get_or_add_rPr()
    rFonts = parse_xml(
        f'<w:rFonts {ns_w} w:ascii="Consolas" w:hAnsi="Consolas" w:cs="Consolas" w:eastAsia="Consolas"/>'
    )
    rPr.append(rFonts)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {ns_w}>'
        f'  <w:top w:w="{top}" w:type="dxa"/>'
        f'  <w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'  <w:left w:w="{left}" w:type="dxa"/>'
        f'  <w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)

def set_cell_shading(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {ns_w} w:fill="{hex_color}"/>')
    tcPr.append(shd)

def set_table_borders(table, color="CBD5E1", sz="4"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {ns_w}>'
        f'  <w:top w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'  <w:left w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'  <w:bottom w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'  <w:right w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'  <w:insideH w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'  <w:insideV w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

def build_document():
    print("Initializing Document...")
    doc = docx.Document()
    
    # Page Setup: A4, 0.65 in margins
    section = doc.sections[0]
    section.page_width = Inches(8.27)
    section.page_height = Inches(11.69)
    section.top_margin = Inches(0.65)
    section.bottom_margin = Inches(0.65)
    section.left_margin = Inches(0.65)
    section.right_margin = Inches(0.65)
    section.different_first_page_header_footer = True
    
    # Header for regular pages
    header = section.header
    hp = header.paragraphs[0]
    hp.text = "KCA UNIVERSITY • SMART DINING SYSTEM — JAVA SOURCE CODE (CAT 1)"
    hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    hr = hp.runs[0]
    hr.font.name = "Arial"
    hr.font.size = Pt(8.0)
    hr.font.color.rgb = RGBColor(100, 116, 139)

    # Footer for regular pages
    footer = section.footer
    fp = footer.paragraphs[0]
    fp.text = "KCAU_SMART_DINING_JAVA_SOURCE_CODE.pdf  •  "
    fr = fp.runs[0]
    fr.font.name = "Arial"
    fr.font.size = Pt(8.0)
    fr.font.color.rgb = RGBColor(100, 116, 139)
    
    run_pg = fp.add_run("Page ")
    run_pg.font.name = "Arial"
    run_pg.font.size = Pt(8.0)
    run_pg.font.color.rgb = RGBColor(100, 116, 139)
    fld1 = parse_xml(f'<w:fldChar {ns_w} w:fldCharType="begin"/>')
    inst1 = parse_xml(f'<w:instrText {ns_w} xml:space="preserve"> PAGE </w:instrText>')
    fld2 = parse_xml(f'<w:fldChar {ns_w} w:fldCharType="separate"/>')
    fld3 = parse_xml(f'<w:fldChar {ns_w} w:fldCharType="end"/>')
    run_pg._r.append(fld1)
    run_pg._r.append(inst1)
    run_pg._r.append(fld2)
    run_pg._r.append(fld3)

    run_of = fp.add_run(" of ")
    run_of.font.name = "Arial"
    run_of.font.size = Pt(8.0)
    run_of.font.color.rgb = RGBColor(100, 116, 139)

    run_num = fp.add_run()
    run_num.font.name = "Arial"
    run_num.font.size = Pt(8.0)
    run_num.font.color.rgb = RGBColor(100, 116, 139)
    fld4 = parse_xml(f'<w:fldChar {ns_w} w:fldCharType="begin"/>')
    inst2 = parse_xml(f'<w:instrText {ns_w} xml:space="preserve"> NUMPAGES </w:instrText>')
    fld5 = parse_xml(f'<w:fldChar {ns_w} w:fldCharType="separate"/>')
    fld6 = parse_xml(f'<w:fldChar {ns_w} w:fldCharType="end"/>')
    run_num._r.append(fld4)
    run_num._r.append(inst2)
    run_num._r.append(fld5)
    run_num._r.append(fld6)

    # -------------------------------------------------------------
    # 1. COVER PAGE
    # -------------------------------------------------------------
    print("Generating Cover Page...")
    p_inst = doc.add_paragraph()
    p_inst.paragraph_format.space_before = Pt(12)
    p_inst.paragraph_format.space_after = Pt(2)
    r_inst = p_inst.add_run("KCA UNIVERSITY")
    r_inst.font.name = "Arial"
    r_inst.font.size = Pt(15)
    r_inst.bold = True
    r_inst.font.color.rgb = RGBColor(194, 65, 12) # Warm University Orange

    p_dept = doc.add_paragraph()
    p_dept.paragraph_format.space_before = Pt(0)
    p_dept.paragraph_format.space_after = Pt(18)
    r_dept = p_dept.add_run("FACULTY OF COMPUTING AND INFORMATION MANAGEMENT\nDEPARTMENT OF SOFTWARE DEVELOPMENT & INFORMATION SYSTEMS")
    r_dept.font.name = "Arial"
    r_dept.font.size = Pt(9.5)
    r_dept.font.color.rgb = RGBColor(71, 85, 105)

    # Title
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(10)
    p_title.paragraph_format.space_after = Pt(4)
    r_title = p_title.add_run("KCAU SMART DINING SYSTEM")
    r_title.font.name = "Arial"
    r_title.font.size = Pt(26)
    r_title.bold = True
    r_title.font.color.rgb = RGBColor(15, 23, 42) # Deep Slate

    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_before = Pt(0)
    p_sub.paragraph_format.space_after = Pt(14)
    r_sub = p_sub.add_run("Continuous Assessment Test 1 (CAT 1) — Comprehensive Java Backend Source Code Document")
    r_sub.font.name = "Arial"
    r_sub.font.size = Pt(13)
    r_sub.font.color.rgb = RGBColor(100, 116, 139)

    # Badge box
    p_badge = doc.add_paragraph()
    p_badge.paragraph_format.space_before = Pt(0)
    p_badge.paragraph_format.space_after = Pt(20)
    r_badge = p_badge.add_run("OFFICIAL DELIVERABLE FILE: KCAU_SMART_DINING_JAVA_SOURCE_CODE.pdf")
    apply_consolas(r_badge, size_pt=9.5, color=RGBColor(194, 65, 12), bold=True)

    # Metadata Table
    meta_table = doc.add_table(rows=8, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_table.autofit = False
    meta_table.columns[0].width = Inches(2.2)
    meta_table.columns[1].width = Inches(4.77)
    set_table_borders(meta_table, color="E2E8F0", sz="4")

    meta_rows = [
        ("Student Name / Author", "Solomon (solomon476)"),
        ("Project Title", "KCAU Smart Dining System (Campus Cafeteria Automation)"),
        ("Academic Course / Unit", "Continuous Assessment Test 1 (CAT 1)"),
        ("Document Specification", "Java Source Code Document (Item 2 of Assessment Portfolio)"),
        ("Backend Architecture", "Modular Java 21/25, Project Loom Virtual Threads, SQLite JDBC"),
        ("Source Code Scope", "23 Java Classes (19 Modular Engine Classes + 4 Compatibility Aliases)"),
        ("Live Web Deployment", "https://kca-cafeteria.vercel.app"),
        ("GitHub Repository", "https://github.com/solomon476/KCAU-SMART-DINING-SYSTEM")
    ]

    for idx, (label, val) in enumerate(meta_rows):
        c0 = meta_table.cell(idx, 0)
        c1 = meta_table.cell(idx, 1)
        set_cell_margins(c0, top=70, bottom=70, left=100, right=100)
        set_cell_margins(c1, top=70, bottom=70, left=100, right=100)
        if idx % 2 == 0:
            set_cell_shading(c0, "F8FAFC")
            set_cell_shading(c1, "F8FAFC")
        else:
            set_cell_shading(c0, "FFFFFF")
            set_cell_shading(c1, "FFFFFF")

        p0 = c0.paragraphs[0]
        p0.paragraph_format.space_before = Pt(0)
        p0.paragraph_format.space_after = Pt(0)
        r0 = p0.add_run(label)
        r0.font.name = "Arial"
        r0.font.size = Pt(8.5)
        r0.bold = True
        r0.font.color.rgb = RGBColor(15, 23, 42)

        p1 = c1.paragraphs[0]
        p1.paragraph_format.space_before = Pt(0)
        p1.paragraph_format.space_after = Pt(0)
        r1 = p1.add_run(val)
        if "http" in val or "pdf" in val:
            apply_consolas(r1, size_pt=8.2, color=RGBColor(30, 41, 59))
        else:
            r1.font.name = "Arial"
            r1.font.size = Pt(8.5)
            r1.font.color.rgb = RGBColor(51, 65, 85)

    p_note = doc.add_paragraph()
    p_note.paragraph_format.space_before = Pt(28)
    p_note.paragraph_format.space_after = Pt(0)
    r_note = p_note.add_run(
        "Note on Document Formatting: This document compiles the complete source code for the KCAU Smart Dining System backend. "
        "Per CAT 1 instructions, all code is formatted using Consolas monospaced typography with preserved indentation, complete imports, "
        "package declarations, and each class starting on a new page."
    )
    r_note.font.name = "Arial"
    r_note.font.size = Pt(8.5)
    r_note.italic = True
    r_note.font.color.rgb = RGBColor(100, 116, 139)

    # -------------------------------------------------------------
    # 2. ARCHITECTURAL OVERVIEW & INDEX
    # -------------------------------------------------------------
    doc.add_page_break()
    print("Generating Architectural Overview & Class Index...")

    p_idx_h = doc.add_paragraph()
    p_idx_h.paragraph_format.space_before = Pt(0)
    p_idx_h.paragraph_format.space_after = Pt(4)
    r_idx_h = p_idx_h.add_run("Backend Architecture & Source Code Directory")
    r_idx_h.font.name = "Arial"
    r_idx_h.font.size = Pt(16)
    r_idx_h.bold = True
    r_idx_h.font.color.rgb = RGBColor(15, 23, 42)

    p_idx_desc = doc.add_paragraph()
    p_idx_desc.paragraph_format.space_before = Pt(0)
    p_idx_desc.paragraph_format.space_after = Pt(10)
    r_idx_desc = p_idx_desc.add_run(
        "The backend is structured into clear separation-of-concerns layers following modern enterprise Java best practices. "
        "The table below indexes all 23 Java source files included in this document:"
    )
    r_idx_desc.font.name = "Arial"
    r_idx_desc.font.size = Pt(8.5)
    r_idx_desc.font.color.rgb = RGBColor(51, 65, 85)

    # Table of All Classes
    idx_table = doc.add_table(rows=len(JAVA_CLASSES) + 1, cols=5)
    idx_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    idx_table.autofit = False
    idx_table.columns[0].width = Inches(0.4)
    idx_table.columns[1].width = Inches(1.8)
    idx_table.columns[2].width = Inches(2.2)
    idx_table.columns[3].width = Inches(1.97)
    idx_table.columns[4].width = Inches(0.6)
    set_table_borders(idx_table, color="CBD5E1", sz="4")

    # Header Row
    headers = ["#", "Class Name", "Package / Directory", "Architectural Tier", "Lines"]
    for col_idx, htext in enumerate(headers):
        cell = idx_table.cell(0, col_idx)
        set_cell_margins(cell, top=60, bottom=60, left=60, right=60)
        set_cell_shading(cell, "0F172A")
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        if col_idx in (0, 4):
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(htext)
        r.font.name = "Arial"
        r.font.size = Pt(8.0)
        r.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)

    # Populate rows
    for i, cls in enumerate(JAVA_CLASSES):
        row_idx = i + 1
        full_path = os.path.join(BASE_DIR, cls["path"])
        with open(full_path, "r", encoding="utf-8") as f:
            line_cnt = len(f.readlines())

        c0 = idx_table.cell(row_idx, 0)
        c1 = idx_table.cell(row_idx, 1)
        c2 = idx_table.cell(row_idx, 2)
        c3 = idx_table.cell(row_idx, 3)
        c4 = idx_table.cell(row_idx, 4)

        for c in (c0, c1, c2, c3, c4):
            set_cell_margins(c, top=45, bottom=45, left=60, right=60)
            if i % 2 == 1:
                set_cell_shading(c, "F8FAFC")
            else:
                set_cell_shading(c, "FFFFFF")

        p0 = c0.paragraphs[0]
        p0.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r0 = p0.add_run(str(cls["num"]))
        r0.font.name = "Arial"
        r0.font.size = Pt(7.8)
        r0.bold = True

        p1 = c1.paragraphs[0]
        r1 = p1.add_run(cls["name"])
        apply_consolas(r1, size_pt=7.8, color=RGBColor(15, 23, 42), bold=True)

        p2 = c2.paragraphs[0]
        r2 = p2.add_run(cls["pkg"])
        apply_consolas(r2, size_pt=7.5, color=RGBColor(71, 85, 105))

        p3 = c3.paragraphs[0]
        r3 = p3.add_run(cls["tier"])
        r3.font.name = "Arial"
        r3.font.size = Pt(7.8)
        r3.font.color.rgb = RGBColor(51, 65, 85)

        p4 = c4.paragraphs[0]
        p4.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r4 = p4.add_run(str(line_cnt))
        apply_consolas(r4, size_pt=7.8, color=RGBColor(194, 65, 12), bold=True)

    # -------------------------------------------------------------
    # 3. CLASS SOURCE CODE SECTIONS
    # -------------------------------------------------------------
    print("Formatting and appending 23 Java classes...")
    lexer = JavaLexer()

    for cls in JAVA_CLASSES:
        print(f"  -> Adding {cls['num']}. {cls['name']} ({cls['path']})...")
        doc.add_page_break()

        # Class Heading
        p_hdr = doc.add_paragraph()
        p_hdr.paragraph_format.space_before = Pt(0)
        p_hdr.paragraph_format.space_after = Pt(4)
        
        r_num = p_hdr.add_run(f"Class {cls['num']}: ")
        r_num.font.name = "Arial"
        r_num.font.size = Pt(14)
        r_num.bold = True
        r_num.font.color.rgb = RGBColor(194, 65, 12)

        r_name = p_hdr.add_run(cls["name"])
        apply_consolas(r_name, size_pt=13, color=RGBColor(15, 23, 42), bold=True)

        # Class Meta Box Table
        full_path = os.path.join(BASE_DIR, cls["path"])
        with open(full_path, "r", encoding="utf-8") as f:
            code_text = f.read()
        lines = code_text.splitlines()
        loc = len(lines)

        meta_tbl = doc.add_table(rows=2, cols=2)
        meta_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        meta_tbl.autofit = False
        meta_tbl.columns[0].width = Inches(3.48)
        meta_tbl.columns[1].width = Inches(3.48)
        set_table_borders(meta_tbl, color="CBD5E1", sz="4")

        # Cell (0,0) - Package & Path
        mc00 = meta_tbl.cell(0, 0)
        set_cell_margins(mc00, top=50, bottom=50, left=80, right=80)
        set_cell_shading(mc00, "F8FAFC")
        mp00 = mc00.paragraphs[0]
        mp00.paragraph_format.space_before = Pt(0)
        mp00.paragraph_format.space_after = Pt(0)
        mr00 = mp00.add_run("Package: ")
        mr00.font.name = "Arial"; mr00.font.size = Pt(7.5); mr00.bold = True
        mr00_val = mp00.add_run(cls["pkg"] + "\n")
        apply_consolas(mr00_val, size_pt=7.5, color=RGBColor(30, 41, 59))
        mr00_p = mp00.add_run("Source Path: ")
        mr00_p.font.name = "Arial"; mr00_p.font.size = Pt(7.5); mr00_p.bold = True
        mr00_pval = mp00.add_run(cls["path"])
        apply_consolas(mr00_pval, size_pt=7.5, color=RGBColor(100, 116, 139))

        # Cell (0,1) - Tier & Lines
        mc01 = meta_tbl.cell(0, 1)
        set_cell_margins(mc01, top=50, bottom=50, left=80, right=80)
        set_cell_shading(mc01, "F8FAFC")
        mp01 = mc01.paragraphs[0]
        mp01.paragraph_format.space_before = Pt(0)
        mp01.paragraph_format.space_after = Pt(0)
        mr01 = mp01.add_run("Layer: ")
        mr01.font.name = "Arial"; mr01.font.size = Pt(7.5); mr01.bold = True
        mr01_val = mp01.add_run(cls["tier"] + "\n")
        mr01_val.font.name = "Arial"; mr01_val.font.size = Pt(7.5); mr01_val.font.color.rgb = RGBColor(194, 65, 12); mr01_val.bold = True
        mr01_l = mp01.add_run("Total Lines: ")
        mr01_l.font.name = "Arial"; mr01_l.font.size = Pt(7.5); mr01_l.bold = True
        mr01_lval = mp01.add_run(f"{loc} lines of Java source code")
        apply_consolas(mr01_lval, size_pt=7.5, color=RGBColor(30, 41, 59))

        # Cell (1,0) spanning 2 columns - Functional Summary
        mc10 = meta_tbl.cell(1, 0)
        mc11 = meta_tbl.cell(1, 1)
        mc10.merge(mc11)
        set_cell_margins(mc10, top=50, bottom=50, left=80, right=80)
        set_cell_shading(mc10, "FFFFFF")
        mp10 = mc10.paragraphs[0]
        mp10.paragraph_format.space_before = Pt(0)
        mp10.paragraph_format.space_after = Pt(0)
        mr10 = mp10.add_run("Functional Role: ")
        mr10.font.name = "Arial"; mr10.font.size = Pt(7.5); mr10.bold = True
        mr10_val = mp10.add_run(cls["role"])
        mr10_val.font.name = "Arial"; mr10_val.font.size = Pt(7.5); mr10_val.font.color.rgb = RGBColor(71, 85, 105)

        # Spacing before code
        p_sp = doc.add_paragraph()
        p_sp.paragraph_format.space_before = Pt(4)
        p_sp.paragraph_format.space_after = Pt(2)
        r_label = p_sp.add_run("Complete Java Source Code:")
        r_label.font.name = "Arial"
        r_label.font.size = Pt(7.8)
        r_label.bold = True
        r_label.font.color.rgb = RGBColor(100, 116, 139)

        # Code Container Paragraphs
        # Replace tabs with 4 spaces for exact indentation preservation
        normalized_code = code_text.replace("\t", "    ")
        
        # We will tokenize with Pygments and append formatted runs to paragraphs
        tokens = lexer.get_tokens(normalized_code)
        
        # Build line-by-line paragraphs for clean layout and smooth multi-page flow
        current_p = doc.add_paragraph()
        current_p.paragraph_format.space_before = Pt(0)
        current_p.paragraph_format.space_after = Pt(0)
        current_p.paragraph_format.line_spacing = 1.05
        current_p.paragraph_format.left_indent = Inches(0.15)

        # Apply left border and soft shading
        pPr = current_p._p.get_or_add_pPr()
        pbdr = parse_xml(f'<w:pBdr {ns_w}><w:left w:val="single" w:sz="12" w:space="8" w:color="EA580C"/></w:pBdr>')
        shd = parse_xml(f'<w:shd {ns_w} w:fill="F8FAFC"/>')
        pPr.append(pbdr)
        pPr.append(shd)

        for ttype, tvalue in tokens:
            # Color mapping
            bold = False
            italic = False
            color = RGBColor(30, 41, 59) # default dark slate

            if ttype in Token.Keyword or ttype in Token.Keyword.Type or ttype in Token.Keyword.Declaration or ttype in Token.Keyword.Namespace:
                color = RGBColor(29, 78, 216) # Rich Blue
                bold = True
            elif ttype in Token.Comment or ttype in Token.Comment.Single or ttype in Token.Comment.Multiline:
                color = RGBColor(100, 116, 139) # Slate Gray
                italic = True
            elif ttype in Token.Literal.String or ttype in Token.Literal.String.Double or ttype in Token.Literal.String.Single:
                color = RGBColor(21, 128, 61) # Emerald Green
            elif ttype in Token.Literal.Number or ttype in Token.Literal.Number.Integer or ttype in Token.Literal.Number.Float:
                color = RGBColor(2, 132, 199) # Cyan
            elif ttype in Token.Name.Decorator:
                color = RGBColor(217, 119, 6) # Amber
                bold = True
            elif ttype in Token.Name.Class:
                color = RGBColor(15, 23, 42) # Deep Slate
                bold = True
            elif ttype in Token.Operator:
                color = RGBColor(71, 85, 105)

            # Check if tvalue has newlines
            if "\n" in tvalue:
                parts = tvalue.split("\n")
                for p_idx, part in enumerate(parts):
                    if part:
                        r = current_p.add_run(part)
                        apply_consolas(r, size_pt=8.0, color=color, bold=bold, italic=italic)
                    if p_idx < len(parts) - 1:
                        # Start new line paragraph
                        current_p = doc.add_paragraph()
                        current_p.paragraph_format.space_before = Pt(0)
                        current_p.paragraph_format.space_after = Pt(0)
                        current_p.paragraph_format.line_spacing = 1.05
                        current_p.paragraph_format.left_indent = Inches(0.15)
                        pPr = current_p._p.get_or_add_pPr()
                        pbdr = parse_xml(f'<w:pBdr {ns_w}><w:left w:val="single" w:sz="12" w:space="8" w:color="EA580C"/></w:pBdr>')
                        shd = parse_xml(f'<w:shd {ns_w} w:fill="F8FAFC"/>')
                        pPr.append(pbdr)
                        pPr.append(shd)
            else:
                r = current_p.add_run(tvalue)
                apply_consolas(r, size_pt=8.0, color=color, bold=bold, italic=italic)

    print(f"Saving Word document to {DOCX_OUT}...")
    doc.save(DOCX_OUT)
    print("Word document generated successfully!")

if __name__ == "__main__":
    build_document()
