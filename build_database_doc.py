#!/usr/bin/env python3
"""
KCAU SMART DINING SYSTEM - DATABASE DOCUMENTATION GENERATOR (CAT 1 - PART 3)
Generates:
  1. docs/database_documentation.html
  2. KCAU_Smart_Dining_Database_Documentation.pdf (via WeasyPrint, crisp 10-page layout)
  3. KCAU_SMART_DINING_DATABASE_DOCUMENTATION.pdf (Uppercase alias)
  4. KCAU_Smart_Dining_Database_Documentation.docx (via python-docx)
  5. KCAU_SMART_DINING_DATABASE_DOCUMENTATION.docx (Uppercase alias)

Complies strictly with CAT 1 deliverable requirements:
- Database structure, tables, fields and relationships (SQLite).
- Complete ERD with Crow's Foot notation and cascading constraints.
- Exhaustive Data Dictionary with validation rules and price freeze pattern.
- ACID Transaction and JDBC integration in Java.
- Operational & analytical reporting SQL queries.
- Database security, PBKDF2 salted hashing, and maintenance protocols.
"""

import os
import sys
import shutil
import weasyprint
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

BASE_DIR = "/home/kali/Honeypot"
DOCS_DIR = os.path.join(BASE_DIR, "docs")
HTML_OUT = os.path.join(DOCS_DIR, "database_documentation.html")
PDF_OUT = os.path.join(BASE_DIR, "KCAU_Smart_Dining_Database_Documentation.pdf")
PDF_OUT_CAPS = os.path.join(BASE_DIR, "KCAU_SMART_DINING_DATABASE_DOCUMENTATION.pdf")
DOCX_OUT = os.path.join(BASE_DIR, "KCAU_Smart_Dining_Database_Documentation.docx")
DOCX_OUT_CAPS = os.path.join(BASE_DIR, "KCAU_SMART_DINING_DATABASE_DOCUMENTATION.docx")

os.makedirs(DOCS_DIR, exist_ok=True)

HTML_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>KCAU Smart Dining System - Database Documentation</title>
    <style>
        @page {
            size: A4;
            margin: 1.3cm 1.3cm;
            @bottom-right {
                content: "Page " counter(page) " of " counter(pages);
                font-size: 7.8pt;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                color: #64748B;
            }
            @bottom-left {
                content: "KCAU Smart Dining System • CAT 1 Relational Database Specification";
                font-size: 7.8pt;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                color: #64748B;
            }
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            color: #1E293B;
            line-height: 1.44;
            font-size: 8.5pt;
            background: #FFFFFF;
            margin: 0;
            padding: 0;
        }

        .header-banner {
            border-bottom: 2.5px solid #EA580C;
            padding-bottom: 0.65rem;
            margin-bottom: 0.95rem;
        }
        .header-badge {
            display: inline-block;
            background: #FFEDD5;
            color: #C2410C;
            font-size: 7.2pt;
            font-weight: 700;
            padding: 0.18rem 0.5rem;
            border-radius: 9999px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.3rem;
        }
        h1 {
            font-size: 17.5pt;
            font-weight: 800;
            color: #0F172A;
            margin: 0 0 0.2rem 0;
            letter-spacing: -0.02em;
        }
        .subtitle {
            font-size: 9.2pt;
            color: #64748B;
            margin: 0 0 0.65rem 0;
            font-weight: 500;
        }
        .meta-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 0.45rem;
            background: #F8FAFC;
            border: 1px solid #E2E8F0;
            border-radius: 6px;
            padding: 0.45rem 0.65rem;
            font-size: 7.5pt;
        }
        .meta-item strong {
            display: block;
            color: #0F172A;
            font-size: 6.6pt;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }
        .meta-item span {
            color: #475569;
        }

        h2 {
            font-size: 11pt;
            color: #0F172A;
            border-bottom: 1.5px solid #E2E8F0;
            padding-bottom: 0.2rem;
            margin-top: 1.1rem;
            margin-bottom: 0.45rem;
            page-break-after: avoid;
            display: flex;
            align-items: center;
            gap: 0.4rem;
        }
        h2.section-start {
            margin-top: 0;
        }
        h2::before {
            content: "";
            display: inline-block;
            width: 5px;
            height: 11px;
            background: #EA580C;
            border-radius: 2px;
        }
        h3 {
            font-size: 9.2pt;
            color: #1E293B;
            margin-top: 0.75rem;
            margin-bottom: 0.3rem;
            page-break-after: avoid;
        }

        p {
            margin: 0 0 0.45rem 0;
            color: #334155;
            text-align: justify;
        }

        ul, ol {
            margin: 0 0 0.45rem 0;
            padding-left: 1.15rem;
            color: #334155;
        }
        li {
            margin-bottom: 0.2rem;
        }

        .page-break {
            page-break-before: always;
        }

        /* Callouts */
        .callout {
            border-left: 3px solid #EA580C;
            background: #FFF7ED;
            padding: 0.45rem 0.7rem;
            border-radius: 0 5px 5px 0;
            margin: 0.5rem 0;
            font-size: 7.9pt;
        }
        .callout strong {
            color: #9A3412;
            display: block;
            margin-bottom: 0.12rem;
        }
        .callout-blue {
            border-left: 3px solid #2563EB;
            background: #EFF6FF;
        }
        .callout-blue strong {
            color: #1E40AF;
        }
        .callout-emerald {
            border-left: 3px solid #059669;
            background: #ECFDF5;
        }
        .callout-emerald strong {
            color: #065F46;
        }

        /* Tables */
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 0.45rem 0 0.65rem 0;
            font-size: 7.6pt;
            page-break-inside: avoid;
        }
        th, td {
            border: 1px solid #CBD5E1;
            padding: 0.32rem 0.48rem;
            text-align: left;
            vertical-align: top;
        }
        th {
            background-color: #0F172A;
            color: #FFFFFF;
            font-weight: 600;
            font-size: 7.3pt;
            letter-spacing: 0.03em;
        }
        tr:nth-child(even) td {
            background-color: #F8FAFC;
        }

        /* Badges */
        .badge {
            display: inline-block;
            font-size: 6.5pt;
            font-weight: 700;
            padding: 0.1rem 0.3rem;
            border-radius: 3px;
            font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
            text-transform: uppercase;
        }
        .badge-pk { background: #FEF3C7; color: #B45309; border: 1px solid #FCD34D; }
        .badge-fk { background: #DBEAFE; color: #1D4ED8; border: 1px solid #93C5FD; }
        .badge-req { background: #FEE2E2; color: #B91C1C; border: 1px solid #FCA5A5; }
        .badge-opt { background: #F1F5F9; color: #64748B; border: 1px solid #CBD5E1; }
        .badge-uq { background: #EDE9FE; color: #6D28D9; border: 1px solid #DDD6FE; }
        .badge-type { background: #E0F2FE; color: #0369A1; border: 1px solid #BAE6FD; }
        .badge-success { background: #ECFDF5; color: #065F46; border: 1px solid #A7F3D0; }

        /* Code Blocks */
        pre {
            background: #0F172A;
            color: #F8FAFC;
            font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, Courier, monospace;
            font-size: 7.1pt;
            line-height: 1.32;
            padding: 0.55rem 0.75rem;
            border-radius: 5px;
            margin: 0.4rem 0 0.6rem 0;
            white-space: pre-wrap;
            word-wrap: break-word;
            page-break-inside: avoid;
        }
        code {
            font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, Courier, monospace;
            font-size: 7.8pt;
            background: #F1F5F9;
            color: #0F172A;
            padding: 0.08rem 0.25rem;
            border-radius: 3px;
        }
        pre code {
            background: transparent;
            color: inherit;
            padding: 0;
        }

        .sql-kw { color: #38BDF8; font-weight: bold; }
        .sql-str { color: #4ADE80; }
        .sql-comment { color: #94A3B8; font-style: italic; }
        .sql-fn { color: #FBBF24; font-weight: bold; }

        /* ERD SVG Container */
        .erd-container {
            margin: 0.5rem 0 0.75rem 0;
            padding: 0.6rem;
            background: #F8FAFC;
            border: 1px solid #E2E8F0;
            border-radius: 6px;
            text-align: center;
            page-break-inside: avoid;
        }
        .erd-caption {
            font-size: 7.4pt;
            color: #64748B;
            margin-top: 0.35rem;
            font-style: italic;
        }
    </style>
</head>
<body>

    <!-- ==================== PAGE 1: COVER & SECTION 1 ==================== -->
    <div class="header-banner">
        <span class="header-badge">KCA University • Department of Software Development • CAT 1</span>
        <h1>KCAU Smart Dining System</h1>
        <div class="subtitle">Document 3 of 4: Relational Database Architecture &amp; Schema Specification</div>
        <div class="meta-grid">
            <div class="meta-item">
                <strong>DBMS Engine</strong>
                <span>SQLite 3.46.0 (Embedded Relational)</span>
            </div>
            <div class="meta-item">
                <strong>Database File</strong>
                <span><code>data/dining.db</code> (Persistent Storage)</span>
            </div>
            <div class="meta-item">
                <strong>Java Connector</strong>
                <span>SQLite JDBC 3.46.0.0 (<code>org.sqlite.JDBC</code>)</span>
            </div>
            <div class="meta-item">
                <strong>Academic Unit</strong>
                <span>CAT 1 — Object Oriented Java Backend</span>
            </div>
        </div>
    </div>

    <h2>1. Executive Summary &amp; Architectural Rationale</h2>
    <p>
        The <strong>KCAU Smart Dining System</strong> is engineered to streamline cafeteria operations across KCA University, unifying three distinct real-time user groups: students ordering meals and tracking kitchen progress, kitchen staff fulfilling meals via a digital Kitchen Display System (KDS), and cafeteria administrators overseeing live revenue KPIs and menu availability.
    </p>
    <p>
        Persistent data storage is powered by an embedded <strong>SQLite 3</strong> relational database engine (stored physically at <code>data/dining.db</code>). SQLite was deliberately chosen over client-server engines (such as MySQL or PostgreSQL) and unstructured NoSQL formats (such as raw JSON files) based on the following architectural justifications:
    </p>

    <ul>
        <li><strong>ACID Transactional Guarantees:</strong> Cafeteria financial operations demand strict Atomicity, Consistency, Isolation, and Durability. When a student checks out, the multi-item order insertion, receipt creation, and M-Pesa payment ledger entry must succeed together or roll back cleanly without partial corruption. SQLite delivers full ACID compliance natively.</li>
        <li><strong>Serverless &amp; Zero Operational Overhead:</strong> SQLite runs directly inside the Java Virtual Machine process via Java Native Access (JNA) / C-bindings. It requires no background database daemons, no separate network port listeners (eliminating port conflicts on ports 3306 or 5432), and zero administrative user credentials.</li>
        <li><strong>Deterministic File Portability:</strong> The complete database—including schema, indexes, constraints, sequences, and data records—is housed in a single binary file (<code>data/dining.db</code>). This guarantees instantaneous portability across grading machines, automated testing pipelines, and live deployments without requiring manual host setup.</li>
        <li><strong>High-Speed In-Memory &amp; Local I/O Performance:</strong> With zero network socket overhead and optimized B-Tree page caching, SQLite executes sub-millisecond queries, allowing the Java Virtual Thread backend (Project Loom) to process hundreds of concurrent order status queries and cart calculations with minimal latency.</li>
        <li><strong>Relational Integrity &amp; Cascading Deletions:</strong> Unlike unstructured document stores, SQLite enforces strict table constraints (<code>PRIMARY KEY</code>, <code>FOREIGN KEY</code>, <code>UNIQUE</code>, <code>NOT NULL</code>, <code>DEFAULT</code>), preventing orphaned order line items and ledger inconsistencies through foreign key cascading actions (<code>ON DELETE CASCADE</code>).</li>
    </ul>

    <div class="callout callout-blue">
        <strong>Runtime Initialization Protocol (<code>DatabaseInitializer.java</code>)</strong>
        On system boot, the Java entrypoint invokes <code>DatabaseInitializer.init()</code>. The system automatically creates the parent <code>data/</code> folder if missing, constructs all 5 tables if they do not exist, and seeds baseline user accounts and the complete cafeteria menu catalog if the tables are empty.
    </div>

    <!-- ==================== PAGE 2: ERD & CARDINALITY MATRIX ==================== -->
    <div class="page-break"></div>
    <h2 class="section-start">2. Entity-Relationship Diagram (ERD) &amp; Relational Model</h2>
    <p>
        The relational architecture is modeled into five core relational entities designed to balance Third Normal Form (3NF) normalization with pragmatic historical auditing: <code>users</code>, <code>orders</code>, <code>order_items</code>, <code>payments</code>, and <code>menu_items</code>.
    </p>

    <div class="erd-container">
        <!-- Compact Clean Crow's Foot SVG ERD (780x375) -->
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 780 375" width="100%" height="auto">
            <defs>
                <filter id="erd-shadow" x="-3%" y="-3%" width="106%" height="106%">
                    <feDropShadow dx="0" dy="2" stdDeviation="2.5" flood-color="#0F172A" flood-opacity="0.08"/>
                </filter>
            </defs>

            <!-- Table 1: USERS (Top Left) -->
            <g filter="url(#erd-shadow)">
                <rect x="25" y="15" width="220" height="155" rx="6" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.2"/>
                <path d="M25,21 a6,6 0 0,1 6,-6 h208 a6,6 0 0,1 6,6 v24 h-220 z" fill="#1E293B"/>
                <text x="135" y="31" fill="#FFFFFF" font-family="-apple-system, sans-serif" font-size="9.5" font-weight="700" text-anchor="middle">users (Student / Staff / Admin)</text>
                
                <text x="35" y="55" fill="#B45309" font-family="monospace" font-size="8" font-weight="700">PK</text>
                <text x="56" y="55" fill="#0F172A" font-family="monospace" font-size="8">id</text>
                <text x="235" y="55" fill="#64748B" font-family="monospace" font-size="7.5" text-anchor="end">TEXT</text>

                <text x="35" y="73" fill="#6D28D9" font-family="monospace" font-size="8" font-weight="700">UQ</text>
                <text x="56" y="73" fill="#0F172A" font-family="monospace" font-size="8">student_id</text>
                <text x="235" y="73" fill="#64748B" font-family="monospace" font-size="7.5" text-anchor="end">TEXT (Reg No)</text>

                <text x="35" y="91" fill="#94A3B8" font-family="monospace" font-size="8">•</text>
                <text x="56" y="91" fill="#334155" font-family="monospace" font-size="8">name</text>
                <text x="235" y="91" fill="#64748B" font-family="monospace" font-size="7.5" text-anchor="end">TEXT</text>

                <text x="35" y="109" fill="#94A3B8" font-family="monospace" font-size="8">•</text>
                <text x="56" y="109" fill="#334155" font-family="monospace" font-size="8">password_hash</text>
                <text x="235" y="109" fill="#64748B" font-family="monospace" font-size="7.5" text-anchor="end">TEXT (PBKDF2)</text>

                <text x="35" y="127" fill="#94A3B8" font-family="monospace" font-size="8">•</text>
                <text x="56" y="127" fill="#334155" font-family="monospace" font-size="8">role</text>
                <text x="235" y="127" fill="#64748B" font-family="monospace" font-size="7.5" text-anchor="end">TEXT (Role)</text>

                <text x="35" y="145" fill="#94A3B8" font-family="monospace" font-size="8">•</text>
                <text x="56" y="145" fill="#334155" font-family="monospace" font-size="8">created_at</text>
                <text x="235" y="145" fill="#64748B" font-family="monospace" font-size="7.5" text-anchor="end">TEXT (ISO)</text>
            </g>

            <!-- Table 2: ORDERS (Top Middle) -->
            <g filter="url(#erd-shadow)">
                <rect x="280" y="15" width="220" height="155" rx="6" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.2"/>
                <path d="M280,21 a6,6 0 0,1 6,-6 h208 a6,6 0 0,1 6,6 v24 h-220 z" fill="#EA580C"/>
                <text x="390" y="31" fill="#FFFFFF" font-family="-apple-system, sans-serif" font-size="9.5" font-weight="700" text-anchor="middle">orders (Cafeteria Order)</text>
                
                <text x="290" y="55" fill="#B45309" font-family="monospace" font-size="8" font-weight="700">PK</text>
                <text x="312" y="55" fill="#0F172A" font-family="monospace" font-size="8">id</text>
                <text x="490" y="55" fill="#64748B" font-family="monospace" font-size="7.5" text-anchor="end">TEXT (ORD-X)</text>

                <text x="290" y="73" fill="#1D4ED8" font-family="monospace" font-size="8" font-weight="700">FK</text>
                <text x="312" y="73" fill="#0F172A" font-family="monospace" font-size="8">user_id</text>
                <text x="490" y="73" fill="#64748B" font-family="monospace" font-size="7.5" text-anchor="end">TEXT (users.id)</text>

                <text x="290" y="91" fill="#94A3B8" font-family="monospace" font-size="8">•</text>
                <text x="312" y="91" fill="#334155" font-family="monospace" font-size="8">customer_name</text>
                <text x="490" y="91" fill="#64748B" font-family="monospace" font-size="7.5" text-anchor="end">TEXT</text>

                <text x="290" y="109" fill="#94A3B8" font-family="monospace" font-size="8">•</text>
                <text x="312" y="109" fill="#334155" font-family="monospace" font-size="8">date</text>
                <text x="490" y="109" fill="#64748B" font-family="monospace" font-size="7.5" text-anchor="end">TEXT (ISO)</text>

                <text x="290" y="127" fill="#94A3B8" font-family="monospace" font-size="8">•</text>
                <text x="312" y="127" fill="#334155" font-family="monospace" font-size="8">total</text>
                <text x="490" y="127" fill="#64748B" font-family="monospace" font-size="7.5" text-anchor="end">REAL (KES)</text>

                <text x="290" y="145" fill="#94A3B8" font-family="monospace" font-size="8">•</text>
                <text x="312" y="145" fill="#334155" font-family="monospace" font-size="8">order_status</text>
                <text x="490" y="145" fill="#64748B" font-family="monospace" font-size="7.5" text-anchor="end">TEXT (State)</text>
            </g>

            <!-- Table 3: ORDER_ITEMS (Top Right) -->
            <g filter="url(#erd-shadow)">
                <rect x="535" y="15" width="220" height="155" rx="6" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.2"/>
                <path d="M535,21 a6,6 0 0,1 6,-6 h208 a6,6 0 0,1 6,6 v24 h-220 z" fill="#2563EB"/>
                <text x="645" y="31" fill="#FFFFFF" font-family="-apple-system, sans-serif" font-size="9.5" font-weight="700" text-anchor="middle">order_items (Line Details)</text>
                
                <text x="545" y="55" fill="#B45309" font-family="monospace" font-size="8" font-weight="700">PK</text>
                <text x="567" y="55" fill="#0F172A" font-family="monospace" font-size="8">id</text>
                <text x="745" y="55" fill="#64748B" font-family="monospace" font-size="7.5" text-anchor="end">INTEGER (AUTO)</text>

                <text x="545" y="73" fill="#1D4ED8" font-family="monospace" font-size="8" font-weight="700">FK</text>
                <text x="567" y="73" fill="#0F172A" font-family="monospace" font-size="8">order_id</text>
                <text x="745" y="73" fill="#64748B" font-family="monospace" font-size="7.5" text-anchor="end">TEXT (orders)</text>

                <text x="545" y="91" fill="#1D4ED8" font-family="monospace" font-size="8" font-weight="700">FK</text>
                <text x="567" y="91" fill="#0F172A" font-family="monospace" font-size="8">food_id</text>
                <text x="745" y="91" fill="#64748B" font-family="monospace" font-size="7.5" text-anchor="end">TEXT (menu)</text>

                <text x="545" y="109" fill="#94A3B8" font-family="monospace" font-size="8">•</text>
                <text x="567" y="109" fill="#334155" font-family="monospace" font-size="8">food_name</text>
                <text x="745" y="109" fill="#64748B" font-family="monospace" font-size="7.5" text-anchor="end">TEXT (Snapshot)</text>

                <text x="545" y="127" fill="#94A3B8" font-family="monospace" font-size="8">•</text>
                <text x="567" y="127" fill="#334155" font-family="monospace" font-size="8">quantity</text>
                <text x="745" y="127" fill="#64748B" font-family="monospace" font-size="7.5" text-anchor="end">INTEGER</text>

                <text x="545" y="145" fill="#94A3B8" font-family="monospace" font-size="8">•</text>
                <text x="567" y="145" fill="#334155" font-family="monospace" font-size="8">unit_price</text>
                <text x="745" y="145" fill="#64748B" font-family="monospace" font-size="7.5" text-anchor="end">REAL (Frozen)</text>
            </g>

            <!-- Table 4: PAYMENTS (Bottom Middle) -->
            <g filter="url(#erd-shadow)">
                <rect x="280" y="210" width="220" height="150" rx="6" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.2"/>
                <path d="M280,216 a6,6 0 0,1 6,-6 h208 a6,6 0 0,1 6,6 v24 h-220 z" fill="#0D9488"/>
                <text x="390" y="226" fill="#FFFFFF" font-family="-apple-system, sans-serif" font-size="9.5" font-weight="700" text-anchor="middle">payments (Audit Ledger)</text>
                
                <text x="290" y="250" fill="#B45309" font-family="monospace" font-size="8" font-weight="700">PK</text>
                <text x="312" y="250" fill="#0F172A" font-family="monospace" font-size="8">id</text>
                <text x="490" y="250" fill="#64748B" font-family="monospace" font-size="7.5" text-anchor="end">TEXT (PAY-X)</text>

                <text x="290" y="268" fill="#1D4ED8" font-family="monospace" font-size="8" font-weight="700">FK</text>
                <text x="312" y="268" fill="#0F172A" font-family="monospace" font-size="8">order_id</text>
                <text x="490" y="268" fill="#64748B" font-family="monospace" font-size="7.5" text-anchor="end">TEXT (orders)</text>

                <text x="290" y="286" fill="#94A3B8" font-family="monospace" font-size="8">•</text>
                <text x="312" y="286" fill="#334155" font-family="monospace" font-size="8">method</text>
                <text x="490" y="286" fill="#64748B" font-family="monospace" font-size="7.5" text-anchor="end">TEXT (MPESA)</text>

                <text x="290" y="304" fill="#94A3B8" font-family="monospace" font-size="8">•</text>
                <text x="312" y="304" fill="#334155" font-family="monospace" font-size="8">amount</text>
                <text x="490" y="304" fill="#64748B" font-family="monospace" font-size="7.5" text-anchor="end">REAL (KES)</text>

                <text x="290" y="322" fill="#94A3B8" font-family="monospace" font-size="8">•</text>
                <text x="312" y="322" fill="#334155" font-family="monospace" font-size="8">status</text>
                <text x="490" y="322" fill="#64748B" font-family="monospace" font-size="7.5" text-anchor="end">TEXT (Status)</text>

                <text x="290" y="340" fill="#94A3B8" font-family="monospace" font-size="8">•</text>
                <text x="312" y="340" fill="#334155" font-family="monospace" font-size="8">reference</text>
                <text x="490" y="340" fill="#64748B" font-family="monospace" font-size="7.5" text-anchor="end">TEXT (Receipt)</text>
            </g>

            <!-- Table 5: MENU_ITEMS (Bottom Right) -->
            <g filter="url(#erd-shadow)">
                <rect x="535" y="210" width="220" height="150" rx="6" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.2"/>
                <path d="M535,216 a6,6 0 0,1 6,-6 h208 a6,6 0 0,1 6,6 v24 h-220 z" fill="#7C3AED"/>
                <text x="645" y="226" fill="#FFFFFF" font-family="-apple-system, sans-serif" font-size="9.5" font-weight="700" text-anchor="middle">menu_items (Food Dishes)</text>
                
                <text x="545" y="250" fill="#B45309" font-family="monospace" font-size="8" font-weight="700">PK</text>
                <text x="567" y="250" fill="#0F172A" font-family="monospace" font-size="8">id</text>
                <text x="745" y="250" fill="#64748B" font-family="monospace" font-size="7.5" text-anchor="end">TEXT (food-X)</text>

                <text x="545" y="268" fill="#94A3B8" font-family="monospace" font-size="8">•</text>
                <text x="567" y="268" fill="#334155" font-family="monospace" font-size="8">name</text>
                <text x="745" y="268" fill="#64748B" font-family="monospace" font-size="7.5" text-anchor="end">TEXT</text>

                <text x="545" y="286" fill="#94A3B8" font-family="monospace" font-size="8">•</text>
                <text x="567" y="286" fill="#334155" font-family="monospace" font-size="8">price</text>
                <text x="745" y="286" fill="#64748B" font-family="monospace" font-size="7.5" text-anchor="end">REAL (KES)</text>

                <text x="545" y="304" fill="#94A3B8" font-family="monospace" font-size="8">•</text>
                <text x="567" y="304" fill="#334155" font-family="monospace" font-size="8">category</text>
                <text x="745" y="304" fill="#64748B" font-family="monospace" font-size="7.5" text-anchor="end">TEXT (Cat)</text>

                <text x="545" y="322" fill="#94A3B8" font-family="monospace" font-size="8">•</text>
                <text x="567" y="322" fill="#334155" font-family="monospace" font-size="8">available</text>
                <text x="745" y="322" fill="#64748B" font-family="monospace" font-size="7.5" text-anchor="end">INTEGER (1|0)</text>

                <text x="545" y="340" fill="#94A3B8" font-family="monospace" font-size="8">•</text>
                <text x="567" y="340" fill="#334155" font-family="monospace" font-size="8">image</text>
                <text x="745" y="340" fill="#64748B" font-family="monospace" font-size="7.5" text-anchor="end">TEXT (URI)</text>
            </g>

            <!-- CONNECTIONS & LABELS -->
            <!-- 1. USERS -> ORDERS (Horizontal: (245, 92) to (280, 92)) -->
            <line x1="245" y1="92" x2="280" y2="92" stroke="#EA580C" stroke-width="2"/>
            <line x1="249" y1="86" x2="249" y2="98" stroke="#EA580C" stroke-width="2"/>
            <line x1="273" y1="86" x2="280" y2="92" stroke="#EA580C" stroke-width="2"/>
            <line x1="273" y1="98" x2="280" y2="92" stroke="#EA580C" stroke-width="2"/>
            <text x="262" y="83" fill="#EA580C" font-family="sans-serif" font-size="7" font-weight="700" text-anchor="middle">1:N</text>

            <!-- 2. ORDERS -> ORDER_ITEMS (Horizontal: (500, 92) to (535, 92)) -->
            <line x1="500" y1="92" x2="535" y2="92" stroke="#2563EB" stroke-width="2"/>
            <line x1="505" y1="86" x2="505" y2="98" stroke="#2563EB" stroke-width="2"/>
            <line x1="528" y1="86" x2="535" y2="92" stroke="#2563EB" stroke-width="2"/>
            <line x1="528" y1="98" x2="535" y2="92" stroke="#2563EB" stroke-width="2"/>
            <text x="517" y="83" fill="#2563EB" font-family="sans-serif" font-size="7" font-weight="700" text-anchor="middle">1:N*</text>

            <!-- 3. ORDERS -> PAYMENTS (Vertical: (390, 170) to (390, 210)) -->
            <line x1="390" y1="170" x2="390" y2="210" stroke="#0D9488" stroke-width="2"/>
            <line x1="384" y1="176" x2="396" y2="176" stroke="#0D9488" stroke-width="2"/>
            <line x1="384" y1="180" x2="396" y2="180" stroke="#0D9488" stroke-width="2"/>
            <line x1="384" y1="204" x2="396" y2="204" stroke="#0D9488" stroke-width="2"/>
            <rect x="348" y="184" width="84" height="15" rx="3" fill="#F0FDFA" stroke="#99F6E4"/>
            <text x="390" y="195" fill="#0F766E" font-family="sans-serif" font-size="6.8" font-weight="700" text-anchor="middle">1:1 CASCADE</text>

            <!-- 4. MENU_ITEMS -> ORDER_ITEMS (Vertical: (645, 210) to (645, 170)) -->
            <line x1="645" y1="210" x2="645" y2="170" stroke="#7C3AED" stroke-width="2"/>
            <line x1="639" y1="204" x2="651" y2="204" stroke="#7C3AED" stroke-width="2"/>
            <line x1="639" y1="178" x2="645" y2="170" stroke="#7C3AED" stroke-width="2"/>
            <line x1="651" y1="178" x2="645" y2="170" stroke="#7C3AED" stroke-width="2"/>
            <rect x="605" y="184" width="80" height="15" rx="3" fill="#F5F3FF" stroke="#DDD6FE"/>
            <text x="645" y="195" fill="#6D28D9" font-family="sans-serif" font-size="6.8" font-weight="700" text-anchor="middle">1:N Catalog</text>
        </svg>
        <div class="erd-caption">Figure 1: Relational Entity-Relationship Diagram (ERD) with Crow's Foot Cardinality and Cascade Indicators (*ON DELETE CASCADE)</div>
    </div>

    <h3>2.1 Referential Integrity &amp; Cardinality Matrix</h3>
    <table>
        <thead>
            <tr>
                <th>Parent Entity</th>
                <th>Child Entity</th>
                <th>Foreign Key</th>
                <th>Cardinality</th>
                <th>Optionality</th>
                <th>Cascade Rule</th>
                <th>Business Integrity Role</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>users</strong> (<code>student_id</code> / <code>id</code>)</td>
                <td><strong>orders</strong></td>
                <td><code>orders.user_id</code></td>
                <td>1 : 0..N</td>
                <td>Mandatory User</td>
                <td>RESTRICT / NONE</td>
                <td>Associates customer identity with placed cafeteria orders.</td>
            </tr>
            <tr>
                <td><strong>orders</strong> (<code>id</code>)</td>
                <td><strong>order_items</strong></td>
                <td><code>order_items.order_id</code></td>
                <td>1 : 1..N</td>
                <td>Mandatory Items</td>
                <td><span class="badge badge-req">ON DELETE CASCADE</span></td>
                <td>Deleting an order automatically cleans up all associated food item rows.</td>
            </tr>
            <tr>
                <td><strong>orders</strong> (<code>id</code>)</td>
                <td><strong>payments</strong></td>
                <td><code>payments.order_id</code></td>
                <td>1 : 0..1</td>
                <td>Optional (Pre-Pay)</td>
                <td><span class="badge badge-req">ON DELETE CASCADE</span></td>
                <td>Maintains 1-to-1 ledger reconciliation for M-Pesa STK push &amp; cash transactions.</td>
            </tr>
            <tr>
                <td><strong>menu_items</strong> (<code>id</code>)</td>
                <td><strong>order_items</strong></td>
                <td><code>order_items.food_id</code></td>
                <td>1 : 0..N</td>
                <td>Historical Snapshot</td>
                <td>SET NULL / LOOSE</td>
                <td>Dish catalog linkage. Price and name are snapshotted at purchase time.</td>
            </tr>
        </tbody>
    </table>

    <!-- ==================== PAGE 3: DATA DICTIONARY PART 1 ==================== -->
    <div class="page-break"></div>
    <h2 class="section-start">3. Comprehensive Data Dictionary &amp; Table Specifications</h2>
    <p>
        The following tables outline every column, data storage type, integrity constraint, and functional role within the SQLite database.
    </p>

    <!-- Table 1: USERS -->
    <h3>3.1 Table Name: <code>users</code></h3>
    <p>
        Stores registered user identities across all three system roles (Students, Kitchen Staff, and Cafeteria Administrators). Passwords are never stored in plain text; instead, they are hashed using salted PBKDF2 with HMAC-SHA256 (10,000 iterations).
    </p>
    <table>
        <thead>
            <tr>
                <th>Field Name</th>
                <th>Data Type</th>
                <th>Constraints</th>
                <th>Default</th>
                <th>Description &amp; Validation Rules</th>
                <th>Sample Value</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><code>id</code></td>
                <td><span class="badge badge-type">TEXT</span></td>
                <td><span class="badge badge-pk">PRIMARY KEY</span> <span class="badge badge-req">NOT NULL</span></td>
                <td><em>None</em></td>
                <td>Unique surrogate identifier for the user account.</td>
                <td><code>demo-student-1</code></td>
            </tr>
            <tr>
                <td><code>name</code></td>
                <td><span class="badge badge-type">TEXT</span></td>
                <td><span class="badge badge-req">NOT NULL</span></td>
                <td><em>None</em></td>
                <td>Full legal name of the student or cafeteria employee.</td>
                <td><code>Alex Kiprop</code></td>
            </tr>
            <tr>
                <td><code>student_id</code></td>
                <td><span class="badge badge-type">TEXT</span></td>
                <td><span class="badge badge-uq">UNIQUE</span> <span class="badge badge-req">NOT NULL</span></td>
                <td><em>None</em></td>
                <td>Official KCAU Student Registration Number or Staff ID used as login identifier. Case-insensitive lookup.</td>
                <td><code>KCA/1234/23</code></td>
            </tr>
            <tr>
                <td><code>password_hash</code></td>
                <td><span class="badge badge-type">TEXT</span></td>
                <td><span class="badge badge-req">NOT NULL</span></td>
                <td><em>None</em></td>
                <td>Cryptographically secure hash formatted as <code>salt_b64:hash_b64</code> (PBKDF2 with HMAC-SHA256, 10,000 rounds).</td>
                <td><code>GONWPrjN...:1N6Ln...</code></td>
            </tr>
            <tr>
                <td><code>role</code></td>
                <td><span class="badge badge-type">TEXT</span></td>
                <td><span class="badge badge-req">NOT NULL</span></td>
                <td><code>'student'</code></td>
                <td>Access authorization tier. Permitted values: <code>'student'</code>, <code>'staff'</code>, <code>'admin'</code>.</td>
                <td><code>'student'</code></td>
            </tr>
            <tr>
                <td><code>created_at</code></td>
                <td><span class="badge badge-type">TEXT</span></td>
                <td><span class="badge badge-req">NOT NULL</span></td>
                <td><em>None</em></td>
                <td>Account creation timestamp in standard ISO 8601 UTC string format.</td>
                <td><code>2026-11-03T11:05:15Z</code></td>
            </tr>
        </tbody>
    </table>

    <!-- Table 2: MENU_ITEMS -->
    <h3>3.2 Table Name: <code>menu_items</code></h3>
    <p>
        Maintains the master food and beverage catalog available in the cafeteria. Administrators can toggle meal availability in real time; unavailable dishes are automatically hidden from student trays.
    </p>
    <table>
        <thead>
            <tr>
                <th>Field Name</th>
                <th>Data Type</th>
                <th>Constraints</th>
                <th>Default</th>
                <th>Description &amp; Validation Rules</th>
                <th>Sample Value</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><code>id</code></td>
                <td><span class="badge badge-type">TEXT</span></td>
                <td><span class="badge badge-pk">PRIMARY KEY</span> <span class="badge badge-req">NOT NULL</span></td>
                <td><em>None</em></td>
                <td>Unique menu dish identifier code.</td>
                <td><code>food-1</code></td>
            </tr>
            <tr>
                <td><code>name</code></td>
                <td><span class="badge badge-type">TEXT</span></td>
                <td><span class="badge badge-req">NOT NULL</span></td>
                <td><em>None</em></td>
                <td>Display name of the food or drink item.</td>
                <td><code>Chicken &amp; Rice</code></td>
            </tr>
            <tr>
                <td><code>description</code></td>
                <td><span class="badge badge-type">TEXT</span></td>
                <td><span class="badge badge-opt">NULLABLE</span></td>
                <td><code>NULL</code></td>
                <td>Culinary details, preparation ingredients, and side dish notes.</td>
                <td><code>Grilled spiced chicken served with yellow rice</code></td>
            </tr>
            <tr>
                <td><code>price</code></td>
                <td><span class="badge badge-type">REAL</span></td>
                <td><span class="badge badge-req">NOT NULL</span></td>
                <td><em>None</em></td>
                <td>Current selling price per portion in Kenya Shillings (KES). Must be &ge; 0.00.</td>
                <td><code>150.00</code></td>
            </tr>
            <tr>
                <td><code>category</code></td>
                <td><span class="badge badge-type">TEXT</span></td>
                <td><span class="badge badge-req">NOT NULL</span></td>
                <td><em>None</em></td>
                <td>Cafeteria meal category: <code>'breakfast'</code>, <code>'lunch'</code>, <code>'drinks'</code>, <code>'snacks'</code>.</td>
                <td><code>'lunch'</code></td>
            </tr>
            <tr>
                <td><code>image</code></td>
                <td><span class="badge badge-type">TEXT</span></td>
                <td><span class="badge badge-opt">NULLABLE</span></td>
                <td><code>NULL</code></td>
                <td>Relative path or URI referencing the dish presentation photography asset.</td>
                <td><code>images/chicken_and_rice.png</code></td>
            </tr>
            <tr>
                <td><code>available</code></td>
                <td><span class="badge badge-type">INTEGER</span></td>
                <td><span class="badge badge-req">NOT NULL</span></td>
                <td><code>1</code></td>
                <td>Inventory stock flag: <code>1</code> = Available (In Stock); <code>0</code> = Unavailable (Sold Out). Toggled by Admin.</td>
                <td><code>1</code></td>
            </tr>
        </tbody>
    </table>

    <!-- ==================== PAGE 4: DATA DICTIONARY PART 2 ==================== -->
    <div class="page-break"></div>
    <h3 class="section-start">3.3 Table Name: <code>orders</code></h3>
    <p>
        The central transactional entity representing student food orders. Tracks order totals and drives the Kitchen Display System (KDS) progression lifecycle (<code>PENDING</code> &rarr; <code>PREPARING</code> &rarr; <code>READY</code> &rarr; <code>COLLECTED</code>).
    </p>
    <table>
        <thead>
            <tr>
                <th>Field Name</th>
                <th>Data Type</th>
                <th>Constraints</th>
                <th>Default</th>
                <th>Description &amp; Validation Rules</th>
                <th>Sample Value</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><code>id</code></td>
                <td><span class="badge badge-type">TEXT</span></td>
                <td><span class="badge badge-pk">PRIMARY KEY</span> <span class="badge badge-req">NOT NULL</span></td>
                <td><em>None</em></td>
                <td>Unique human-readable order tracking number formatted as <code>ORD-XXXXXX</code>.</td>
                <td><code>ORD-864035</code></td>
            </tr>
            <tr>
                <td><code>user_id</code></td>
                <td><span class="badge badge-type">TEXT</span></td>
                <td><span class="badge badge-fk">FOREIGN KEY</span> <span class="badge badge-req">NOT NULL</span></td>
                <td><em>None</em></td>
                <td>Identifies the student who placed the order (corresponds to <code>users.student_id</code>).</td>
                <td><code>KCA/1234/23</code></td>
            </tr>
            <tr>
                <td><code>customer_name</code></td>
                <td><span class="badge badge-type">TEXT</span></td>
                <td><span class="badge badge-req">NOT NULL</span></td>
                <td><em>None</em></td>
                <td>Name of the customer for cafeteria collection announcements.</td>
                <td><code>Alex Kiprop</code></td>
            </tr>
            <tr>
                <td><code>date</code></td>
                <td><span class="badge badge-type">TEXT</span></td>
                <td><span class="badge badge-req">NOT NULL</span></td>
                <td><em>None</em></td>
                <td>ISO 8601 UTC timestamp recording exact order submission time.</td>
                <td><code>2026-11-03T11:21:04Z</code></td>
            </tr>
            <tr>
                <td><code>total</code></td>
                <td><span class="badge badge-type">REAL</span></td>
                <td><span class="badge badge-req">NOT NULL</span></td>
                <td><em>None</em></td>
                <td>Total monetary order checkout sum in KES (sum of quantity &times; unit_price).</td>
                <td><code>230.00</code></td>
            </tr>
            <tr>
                <td><code>order_status</code></td>
                <td><span class="badge badge-type">TEXT</span></td>
                <td><span class="badge badge-req">NOT NULL</span></td>
                <td><code>'PENDING'</code></td>
                <td>Lifecycle state of kitchen queue: <code>'PENDING'</code>, <code>'PREPARING'</code>, <code>'READY'</code>, <code>'COLLECTED'</code>.</td>
                <td><code>'PREPARING'</code></td>
            </tr>
        </tbody>
    </table>

    <!-- Table 4: ORDER_ITEMS -->
    <h3>3.4 Table Name: <code>order_items</code></h3>
    <p>
        Normalized line-item detail table capturing each dish within an order. Implements the essential <em>Price Snapshot Pattern</em> to maintain permanent financial consistency.
    </p>
    <table>
        <thead>
            <tr>
                <th>Field Name</th>
                <th>Data Type</th>
                <th>Constraints</th>
                <th>Default</th>
                <th>Description &amp; Validation Rules</th>
                <th>Sample Value</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><code>id</code></td>
                <td><span class="badge badge-type">INTEGER</span></td>
                <td><span class="badge badge-pk">PRIMARY KEY</span> <code>AUTOINCREMENT</code></td>
                <td><em>Auto</em></td>
                <td>Surrogate sequential integer identifier for the line item.</td>
                <td><code>1</code></td>
            </tr>
            <tr>
                <td><code>order_id</code></td>
                <td><span class="badge badge-type">TEXT</span></td>
                <td><span class="badge badge-fk">FOREIGN KEY</span> <span class="badge badge-req">NOT NULL</span></td>
                <td><em>None</em></td>
                <td>References <code>orders(id)</code> with <span class="badge badge-req">ON DELETE CASCADE</span>.</td>
                <td><code>ORD-864035</code></td>
            </tr>
            <tr>
                <td><code>food_id</code></td>
                <td><span class="badge badge-type">TEXT</span></td>
                <td><span class="badge badge-fk">FOREIGN KEY</span> <span class="badge badge-req">NOT NULL</span></td>
                <td><em>None</em></td>
                <td>References the origin <code>menu_items(id)</code>.</td>
                <td><code>food-2</code></td>
            </tr>
            <tr>
                <td><code>food_name</code></td>
                <td><span class="badge badge-type">TEXT</span></td>
                <td><span class="badge badge-req">NOT NULL</span></td>
                <td><em>None</em></td>
                <td>Snapshot dish title at checkout time. Preserves receipt accuracy if dish is renamed.</td>
                <td><code>Fresh Mango Juice</code></td>
            </tr>
            <tr>
                <td><code>quantity</code></td>
                <td><span class="badge badge-type">INTEGER</span></td>
                <td><span class="badge badge-req">NOT NULL</span></td>
                <td><em>None</em></td>
                <td>Number of portions requested. Verified strictly &ge; 1 by Java validator.</td>
                <td><code>1</code></td>
            </tr>
            <tr>
                <td><code>unit_price</code></td>
                <td><span class="badge badge-type">REAL</span></td>
                <td><span class="badge badge-req">NOT NULL</span></td>
                <td><em>None</em></td>
                <td><strong>Price Snapshot:</strong> Historical unit price per item in KES at the exact instant of ordering.</td>
                <td><code>80.00</code></td>
            </tr>
        </tbody>
    </table>

    <div class="callout">
        <strong>Architectural Rationale: Why Snapshot Prices in <code>order_items</code>?</strong>
        In cafeteria environments, dish prices fluctuate over time. If <code>order_items</code> referenced <code>menu_items.price</code> dynamically, updating a burger's price next month would retroactively distort all past accounting sales reports and student receipts! Storing frozen <code>unit_price</code> and <code>food_name</code> guarantees immutable financial auditing.
    </div>

    <!-- ==================== PAGE 5: PAYMENTS & STORAGE METRICS ==================== -->
    <div class="page-break"></div>
    <h3 class="section-start">3.5 Table Name: <code>payments</code></h3>
    <p>
        The financial settlement audit ledger tracking electronic M-Pesa STK push confirmations, card transactions, and cash tenders.
    </p>
    <table>
        <thead>
            <tr>
                <th>Field Name</th>
                <th>Data Type</th>
                <th>Constraints</th>
                <th>Default</th>
                <th>Description &amp; Validation Rules</th>
                <th>Sample Value</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><code>id</code></td>
                <td><span class="badge badge-type">TEXT</span></td>
                <td><span class="badge badge-pk">PRIMARY KEY</span> <span class="badge badge-req">NOT NULL</span></td>
                <td><em>None</em></td>
                <td>Unique payment receipt transaction code formatted as <code>PAY-XXXXXXXX</code>.</td>
                <td><code>PAY-2DC3DDB6</code></td>
            </tr>
            <tr>
                <td><code>order_id</code></td>
                <td><span class="badge badge-type">TEXT</span></td>
                <td><span class="badge badge-fk">FOREIGN KEY</span> <span class="badge badge-req">NOT NULL</span></td>
                <td><em>None</em></td>
                <td>References the settled <code>orders(id)</code> with <span class="badge badge-req">ON DELETE CASCADE</span>.</td>
                <td><code>ORD-864035</code></td>
            </tr>
            <tr>
                <td><code>method</code></td>
                <td><span class="badge badge-type">TEXT</span></td>
                <td><span class="badge badge-req">NOT NULL</span></td>
                <td><code>'MPESA'</code></td>
                <td>Payment channel utilized: <code>'MPESA'</code> (Safaricom STK Push), <code>'CASH'</code>, or <code>'CARD'</code>.</td>
                <td><code>'MPESA'</code></td>
            </tr>
            <tr>
                <td><code>amount</code></td>
                <td><span class="badge badge-type">REAL</span></td>
                <td><span class="badge badge-req">NOT NULL</span></td>
                <td><em>None</em></td>
                <td>Monetary settlement sum in KES matching the order total.</td>
                <td><code>230.00</code></td>
            </tr>
            <tr>
                <td><code>status</code></td>
                <td><span class="badge badge-type">TEXT</span></td>
                <td><span class="badge badge-req">NOT NULL</span></td>
                <td><code>'COMPLETED'</code></td>
                <td>Settlement verification status: <code>'COMPLETED'</code>, <code>'PENDING'</code>, or <code>'FAILED'</code>.</td>
                <td><code>'COMPLETED'</code></td>
            </tr>
            <tr>
                <td><code>reference</code></td>
                <td><span class="badge badge-type">TEXT</span></td>
                <td><span class="badge badge-req">NOT NULL</span></td>
                <td><em>None</em></td>
                <td>Simulated M-Pesa confirmation code or cashier reference number.</td>
                <td><code>MPESA-C3Z16V</code></td>
            </tr>
            <tr>
                <td><code>created_at</code></td>
                <td><span class="badge badge-type">TEXT</span></td>
                <td><span class="badge badge-req">NOT NULL</span></td>
                <td><em>None</em></td>
                <td>Timestamp when the payment was authenticated and finalized (ISO 8601 UTC).</td>
                <td><code>2026-11-03T11:21:04Z</code></td>
            </tr>
        </tbody>
    </table>

    <h3>3.6 Relational Table Storage &amp; Volume Metrics</h3>
    <p>
        The following matrix details the operational characteristics, storage affinities, and data lifecycle retention policies for all five persistent entities in <code>data/dining.db</code>:
    </p>
    <table>
        <thead>
            <tr>
                <th>Table Name</th>
                <th>Primary Key</th>
                <th>Foreign Keys</th>
                <th>Initial Rows</th>
                <th>Storage Affinity</th>
                <th>Row Growth Pattern</th>
                <th>Audit Retention Policy</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><code>users</code></td>
                <td><code>id (TEXT)</code></td>
                <td>None</td>
                <td>3 seeded</td>
                <td>Variable TEXT</td>
                <td>Low (~1,000/yr)</td>
                <td>Permanent (Academic profile records)</td>
            </tr>
            <tr>
                <td><code>menu_items</code></td>
                <td><code>id (TEXT)</code></td>
                <td>None</td>
                <td>8 dishes</td>
                <td>TEXT, REAL, INT</td>
                <td>Low (Seasonal menu updates)</td>
                <td>Permanent active catalog</td>
            </tr>
            <tr>
                <td><code>orders</code></td>
                <td><code>id (TEXT)</code></td>
                <td><code>user_id</code></td>
                <td>Active queue</td>
                <td>TEXT, REAL</td>
                <td>High (~2,500/day)</td>
                <td>7-year legal financial archive</td>
            </tr>
            <tr>
                <td><code>order_items</code></td>
                <td><code>id (INT AUTO)</code></td>
                <td><code>order_id, food_id</code></td>
                <td>Order line items</td>
                <td>INT, TEXT, REAL</td>
                <td>High (~3.2 items/order)</td>
                <td>Cascade deleted with parent order</td>
            </tr>
            <tr>
                <td><code>payments</code></td>
                <td><code>id (TEXT)</code></td>
                <td><code>order_id</code></td>
                <td>Settled receipts</td>
                <td>TEXT, REAL</td>
                <td>Moderate (1:1 with orders)</td>
                <td>Immutable accounting ledger</td>
            </tr>
        </tbody>
    </table>

    <h3>3.7 Database Normalization &amp; 3NF Evaluation</h3>
    <p>
        The relational schema conforms to <strong>Third Normal Form (3NF)</strong> with deliberate design optimizations:
    </p>
    <ul>
        <li><strong>First Normal Form (1NF):</strong> All attributes contain atomic, indivisible values. Repeating groups (such as multiple items in a single cart) are strictly normalized into child entity <code>order_items</code>.</li>
        <li><strong>Second Normal Form (2NF):</strong> All non-key attributes are fully functionally dependent on their table's primary key, eliminating partial dependencies.</li>
        <li><strong>Third Normal Form (3NF) &amp; Temporal Integrity:</strong> No transitive dependencies exist across non-key attributes. While storing <code>food_name</code> and <code>unit_price</code> inside <code>order_items</code> might superficially resemble redundancy, it represents an intentional <em>Temporal Snapshot Pattern</em>: historical transaction receipts must capture prices at the time of purchase rather than fluctuating with current menu pricing.</li>
    </ul>

    <!-- ==================== PAGE 5: SQL DDL SCRIPTS ==================== -->
    <div class="page-break"></div>
    <h2 class="section-start">4. SQL Data Definition Language (DDL) Schema Scripts</h2>
    <p>
        Below are the exact SQL DDL statements executed programmatically by <code>DatabaseInitializer.java</code> upon application launch. All schemas enforce column constraints, primary keys, uniqueness constraints, and foreign key cascades.
    </p>

    <pre><code><span class="sql-comment">-- ====================================================================</span>
<span class="sql-comment">-- KCAU SMART DINING SYSTEM - RELATIONAL SCHEMA DEFINITION (SQLite 3)</span>
<span class="sql-comment">-- Enforces Foreign Key Constraints, Cascading Rules, and Constraints</span>
<span class="sql-comment">-- ====================================================================</span>

<span class="sql-kw">PRAGMA</span> foreign_keys = <span class="sql-kw">ON</span>;

<span class="sql-comment">-- 1. Users Table (Authentication &amp; Role-Based Authorization)</span>
<span class="sql-kw">CREATE TABLE IF NOT EXISTS</span> users (
    id            <span class="sql-kw">TEXT PRIMARY KEY</span>,
    name          <span class="sql-kw">TEXT NOT NULL</span>,
    student_id    <span class="sql-kw">TEXT UNIQUE NOT NULL</span>,
    password_hash <span class="sql-kw">TEXT NOT NULL</span>,
    role          <span class="sql-kw">TEXT NOT NULL DEFAULT</span> <span class="sql-str">'student'</span>,
    created_at    <span class="sql-kw">TEXT NOT NULL</span>
);

<span class="sql-comment">-- 2. Menu Items Table (Cafeteria Food &amp; Beverage Catalog)</span>
<span class="sql-kw">CREATE TABLE IF NOT EXISTS</span> menu_items (
    id          <span class="sql-kw">TEXT PRIMARY KEY</span>,
    name        <span class="sql-kw">TEXT NOT NULL</span>,
    description <span class="sql-kw">TEXT</span>,
    price       <span class="sql-kw">REAL NOT NULL</span>,
    category    <span class="sql-kw">TEXT NOT NULL</span>,
    image       <span class="sql-kw">TEXT</span>,
    available   <span class="sql-kw">INTEGER NOT NULL DEFAULT</span> 1
);

<span class="sql-comment">-- 3. Orders Table (Transactional Headers &amp; Status Lifecycle)</span>
<span class="sql-kw">CREATE TABLE IF NOT EXISTS</span> orders (
    id            <span class="sql-kw">TEXT PRIMARY KEY</span>,
    user_id       <span class="sql-kw">TEXT NOT NULL</span>,
    customer_name <span class="sql-kw">TEXT NOT NULL</span>,
    date          <span class="sql-kw">TEXT NOT NULL</span>,
    total         <span class="sql-kw">REAL NOT NULL</span>,
    order_status  <span class="sql-kw">TEXT NOT NULL DEFAULT</span> <span class="sql-str">'PENDING'</span>
);

<span class="sql-comment">-- 4. Order Items Table (Detailed Order Breakdown with Price Snapshots)</span>
<span class="sql-kw">CREATE TABLE IF NOT EXISTS</span> order_items (
    id         <span class="sql-kw">INTEGER PRIMARY KEY AUTOINCREMENT</span>,
    order_id   <span class="sql-kw">TEXT NOT NULL</span>,
    food_id    <span class="sql-kw">TEXT NOT NULL</span>,
    food_name  <span class="sql-kw">TEXT NOT NULL</span>,
    quantity   <span class="sql-kw">INTEGER NOT NULL</span>,
    unit_price <span class="sql-kw">REAL NOT NULL</span>,
    <span class="sql-kw">FOREIGN KEY</span>(order_id) <span class="sql-kw">REFERENCES</span> orders(id) <span class="sql-kw">ON DELETE CASCADE</span>
);

<span class="sql-comment">-- 5. Payments Table (M-Pesa &amp; Financial Settlement Ledger)</span>
<span class="sql-kw">CREATE TABLE IF NOT EXISTS</span> payments (
    id         <span class="sql-kw">TEXT PRIMARY KEY</span>,
    order_id   <span class="sql-kw">TEXT NOT NULL</span>,
    method     <span class="sql-kw">TEXT NOT NULL</span>,
    amount     <span class="sql-kw">REAL NOT NULL</span>,
    status     <span class="sql-kw">TEXT NOT NULL</span>,
    reference  <span class="sql-kw">TEXT NOT NULL</span>,
    created_at <span class="sql-kw">TEXT NOT NULL</span>,
    <span class="sql-kw">FOREIGN KEY</span>(order_id) <span class="sql-kw">REFERENCES</span> orders(id) <span class="sql-kw">ON DELETE CASCADE</span>
);</code></pre>

    <div class="callout callout-emerald">
        <strong>SQLite Type Affinity Specification</strong>
        SQLite utilizes dynamic type affinities. The schema strictly enforces <code>TEXT</code> for primary keys, student IDs, hashes, and ISO timestamps; <code>REAL</code> for monetary sums (prices, subtotals, tender amounts); and <code>INTEGER</code> for auto-incrementing line item surrogate keys and binary availability flags.
    </div>

    <!-- ==================== PAGE 6: JDBC & ACID TRANSACTIONS ==================== -->
    <div class="page-break"></div>
    <h2 class="section-start">5. Java Database Connectivity (JDBC) &amp; Transaction Architecture</h2>
    <p>
        Data persistence is integrated through standard <strong>JDBC (Java Database Connectivity)</strong> via the official SQLite JDBC driver (<code>org.sqlite.JDBC</code>).
    </p>

    <h3>5.1 Connection Management (<code>DatabaseConnection.java</code>)</h3>
    <pre><code><span class="sql-kw">public class</span> DatabaseConnection {
    <span class="sql-kw">private static final</span> String DB_PATH = <span class="sql-str">"data/dining.db"</span>;
    <span class="sql-kw">private static final</span> String JDBC_URL = <span class="sql-str">"jdbc:sqlite:"</span> + DB_PATH;

    <span class="sql-kw">public static</span> Connection getConnection() <span class="sql-kw">throws</span> SQLException {
        File dbFile = <span class="sql-kw">new</span> File(DB_PATH);
        File parentDir = dbFile.getParentFile();
        <span class="sql-kw">if</span> (parentDir != <span class="sql-kw">null</span> &amp;&amp; !parentDir.exists()) {
            parentDir.mkdirs(); <span class="sql-comment">// Ensure data/ directory exists</span>
        }
        <span class="sql-kw">return</span> DriverManager.getConnection(JDBC_URL);
    }
}</code></pre>

    <h3>5.2 ACID Multi-Table Atomic Transaction Pattern (<code>OrderService.java</code>)</h3>
    <p>
        When placing an order, the system must write to both <code>orders</code> (parent) and multiple rows in <code>order_items</code> (children). To guarantee Atomicity, auto-commit is disabled (<code>conn.setAutoCommit(false)</code>), batch execution is leveraged, and explicit commits/rollbacks are enforced:
    </p>

    <pre><code><span class="sql-comment">// Order creation inside OrderService.java demonstrating atomic ACID transaction boundary</span>
<span class="sql-kw">try</span> (Connection conn = DatabaseConnection.getConnection()) {
    conn.setAutoCommit(<span class="sql-kw">false</span>); <span class="sql-comment">// 1. Begin Atomic Transaction</span>
    <span class="sql-kw">try</span> {
        <span class="sql-comment">// 2. Insert Parent Order Header</span>
        <span class="sql-kw">try</span> (PreparedStatement pstmt = conn.prepareStatement(insertOrderSql)) {
            pstmt.setString(1, orderId);
            pstmt.setString(2, userId);
            pstmt.setString(3, customerName);
            pstmt.setString(4, now.toString());
            pstmt.setDouble(5, total);
            pstmt.setString(6, <span class="sql-str">"PENDING"</span>);
            pstmt.executeUpdate();
        }

        <span class="sql-comment">// 3. Batch Insert Child Order Items</span>
        <span class="sql-kw">try</span> (PreparedStatement pstmt = conn.prepareStatement(insertItemSql)) {
            <span class="sql-kw">for</span> (OrderItem item : items) {
                pstmt.setString(1, orderId);
                pstmt.setString(2, item.getFoodId());
                pstmt.setString(3, item.getFoodName());
                pstmt.setInt(4, item.getQuantity());
                pstmt.setDouble(5, item.getUnitPrice()); <span class="sql-comment">// Snapshot price</span>
                pstmt.addBatch();
            }
            pstmt.executeBatch();
        }

        conn.commit(); <span class="sql-comment">// 4. Commit atomic transaction on complete success</span>
    } <span class="sql-kw">catch</span> (Exception e) {
        conn.rollback(); <span class="sql-comment">// 5. Rollback on ANY failure, guaranteeing zero orphan rows</span>
        <span class="sql-kw">throw</span> e;
    } <span class="sql-kw">finally</span> {
        conn.setAutoCommit(<span class="sql-kw">true</span>);
    }
}</code></pre>

    <!-- ==================== PAGE 7: OPERATIONAL & ANALYTICAL QUERIES ==================== -->
    <div class="page-break"></div>
    <h2 class="section-start">6. Key Operational &amp; Analytical SQL Queries</h2>
    <p>
        The following queries represent the core operational workloads executed across the three system portals:
    </p>

    <h3>6.1 User Authentication &amp; Credential Verification (<code>UserService.java</code>)</h3>
    <pre><code><span class="sql-comment">-- Retrieves user credentials and hashed secret by Student ID / Username</span>
<span class="sql-kw">SELECT</span> id, name, student_id, password_hash, role, created_at
<span class="sql-kw">FROM</span> users
<span class="sql-kw">WHERE UPPER</span>(student_id) = <span class="sql-kw">UPPER</span>(?);</code></pre>

    <h3>6.2 Active Student Cafeteria Menu Retrieval (<code>MenuService.java</code>)</h3>
    <pre><code><span class="sql-comment">-- Fetches dishes actively in stock (available = 1) filtered by category</span>
<span class="sql-kw">SELECT</span> id, name, description, price, category, image, available
<span class="sql-kw">FROM</span> menu_items
<span class="sql-kw">WHERE</span> available = 1 <span class="sql-kw">AND</span> category = ?
<span class="sql-kw">ORDER BY</span> name <span class="sql-kw">ASC</span>;</code></pre>

    <h3>6.3 Kitchen Display System (KDS) Active Queue (<code>OrderService.java</code>)</h3>
    <pre><code><span class="sql-comment">-- Fetches orders currently in the kitchen queue (excluding collected orders)</span>
<span class="sql-kw">SELECT</span> id, user_id, customer_name, date, total, order_status
<span class="sql-kw">FROM</span> orders
<span class="sql-kw">WHERE</span> order_status <span class="sql-kw">IN</span> (<span class="sql-str">'PENDING'</span>, <span class="sql-str">'PREPARING'</span>, <span class="sql-str">'READY'</span>)
<span class="sql-kw">ORDER BY</span> date <span class="sql-kw">ASC</span>;</code></pre>

    <h3>6.4 Executive Sales &amp; Financial KPI Aggregation (<code>ReportService.java</code>)</h3>
    <pre><code><span class="sql-comment">-- Real-time Cafeteria Sales Summary &amp; Status Distribution</span>
<span class="sql-kw">SELECT</span>
    <span class="sql-fn">COUNT</span>(*) <span class="sql-kw">AS</span> total_orders,
    <span class="sql-fn">COALESCE</span>(<span class="sql-fn">SUM</span>(total), 0.0) <span class="sql-kw">AS</span> total_revenue,
    <span class="sql-fn">COALESCE</span>(<span class="sql-fn">AVG</span>(total), 0.0) <span class="sql-kw">AS</span> avg_order_value,
    <span class="sql-fn">SUM</span>(<span class="sql-kw">CASE WHEN</span> order_status = <span class="sql-str">'PENDING'</span> <span class="sql-kw">THEN</span> 1 <span class="sql-kw">ELSE</span> 0 <span class="sql-kw">END</span>) <span class="sql-kw">AS</span> pending_count,
    <span class="sql-fn">SUM</span>(<span class="sql-kw">CASE WHEN</span> order_status = <span class="sql-str">'PREPARING'</span> <span class="sql-kw">THEN</span> 1 <span class="sql-kw">ELSE</span> 0 <span class="sql-kw">END</span>) <span class="sql-kw">AS</span> preparing_count,
    <span class="sql-fn">SUM</span>(<span class="sql-kw">CASE WHEN</span> order_status = <span class="sql-str">'READY'</span> <span class="sql-kw">THEN</span> 1 <span class="sql-kw">ELSE</span> 0 <span class="sql-kw">END</span>) <span class="sql-kw">AS</span> ready_count,
    <span class="sql-fn">SUM</span>(<span class="sql-kw">CASE WHEN</span> order_status = <span class="sql-str">'COLLECTED'</span> <span class="sql-kw">THEN</span> 1 <span class="sql-kw">ELSE</span> 0 <span class="sql-kw">END</span>) <span class="sql-kw">AS</span> collected_count
<span class="sql-kw">FROM</span> orders;</code></pre>

    <h3>6.5 Dish Popularity Ranking &amp; Volume Analytics (<code>ReportService.java</code>)</h3>
    <pre><code><span class="sql-comment">-- Identifies the top 10 bestselling dishes by portion sales and gross revenue</span>
<span class="sql-kw">SELECT</span> food_name, <span class="sql-fn">SUM</span>(quantity) <span class="sql-kw">AS</span> total_qty, <span class="sql-fn">SUM</span>(quantity * unit_price) <span class="sql-kw">AS</span> total_sales
<span class="sql-kw">FROM</span> order_items
<span class="sql-kw">GROUP BY</span> food_name
<span class="sql-kw">ORDER BY</span> total_qty <span class="sql-kw">DESC</span>
<span class="sql-kw">LIMIT</span> 10;</code></pre>

    <!-- ==================== PAGE 8: SEED DATA & MIGRATION ==================== -->
    <div class="page-break"></div>
    <h2 class="section-start">7. Database Seeding &amp; Default Catalog Catalog</h2>
    <p>
        To ensure an effortless out-of-the-box demonstration, <code>DatabaseInitializer.java</code> automatically populates the database with three role-based user accounts and an authentic Kenyan university cafeteria menu upon first boot.
    </p>

    <h3>7.1 Default Role-Based User Accounts</h3>
    <table>
        <thead>
            <tr>
                <th>Account Role</th>
                <th>Full Name</th>
                <th>Student / Staff ID</th>
                <th>Default Password</th>
                <th>Assigned Permissions &amp; Access Tier</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><span class="badge badge-pk">STUDENT</span></td>
                <td>Alex Kiprop</td>
                <td><code>KCA/1234/23</code></td>
                <td><code>password123</code></td>
                <td>Browse menu, filter meals, add items to cart, simulated M-Pesa STK checkout, live tracking.</td>
            </tr>
            <tr>
                <td><span class="badge badge-fk">KITCHEN STAFF</span></td>
                <td>Chef Beatrice</td>
                <td><code>STAFF/001</code></td>
                <td><code>password123</code></td>
                <td>Kitchen Display System (KDS), view pending orders, advance status to PREPARING, READY, COLLECTED.</td>
            </tr>
            <tr>
                <td><span class="badge badge-req">ADMINISTRATOR</span></td>
                <td>Solomon (Admin)</td>
                <td><code>ADMIN/001</code></td>
                <td><code>password123</code></td>
                <td>Executive dashboard, real-time revenue analytics, toggle dish availability, add new dishes.</td>
            </tr>
        </tbody>
    </table>

    <h3>7.2 Seeded Cafeteria Menu Catalog (8 Baseline Dishes)</h3>
    <table>
        <thead>
            <tr>
                <th>Item ID</th>
                <th>Dish Name</th>
                <th>Category</th>
                <th>Unit Price (KES)</th>
                <th>Initial Availability</th>
                <th>Menu Description</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><code>food-1</code></td>
                <td><strong>Chicken &amp; Rice</strong></td>
                <td>Lunch</td>
                <td>KES 150.00</td>
                <td><span class="badge badge-success">AVAILABLE (1)</span></td>
                <td>Grilled spiced chicken served with fragrant yellow rice and gravy.</td>
            </tr>
            <tr>
                <td><code>food-2</code></td>
                <td><strong>Fresh Mango Juice</strong></td>
                <td>Drinks</td>
                <td>KES 80.00</td>
                <td><span class="badge badge-success">AVAILABLE (1)</span></td>
                <td>Chilled, naturally squeezed local mango juice without preservatives.</td>
            </tr>
            <tr>
                <td><code>food-3</code></td>
                <td><strong>Beef Burger &amp; Greens</strong></td>
                <td>Lunch</td>
                <td>KES 220.00</td>
                <td><span class="badge badge-success">AVAILABLE (1)</span></td>
                <td>Quarter pound seasoned beef patty in a toasted sesame bun with lettuce.</td>
            </tr>
            <tr>
                <td><code>food-4</code></td>
                <td><strong>Eggs &amp; Brown Toast</strong></td>
                <td>Breakfast</td>
                <td>KES 120.00</td>
                <td><span class="badge badge-success">AVAILABLE (1)</span></td>
                <td>Two farm-fresh sunny side up eggs served with buttered toasted bread.</td>
            </tr>
            <tr>
                <td><code>food-5</code></td>
                <td><strong>Crisp Golden Fries</strong></td>
                <td>Snacks</td>
                <td>KES 100.00</td>
                <td><span class="badge badge-success">AVAILABLE (1)</span></td>
                <td>Hand-cut seasoned potato fries deep-fried till golden crisp.</td>
            </tr>
            <tr>
                <td><code>food-6</code></td>
                <td><strong>Fluffy Honey Pancakes</strong></td>
                <td>Breakfast</td>
                <td>KES 140.00</td>
                <td><span class="badge badge-success">AVAILABLE (1)</span></td>
                <td>Stack of two buttermilk pancakes drizzled with pure golden honey.</td>
            </tr>
            <tr>
                <td><code>food-7</code></td>
                <td><strong>Hot Brewed Coffee</strong></td>
                <td>Drinks</td>
                <td>KES 70.00</td>
                <td><span class="badge badge-success">AVAILABLE (1)</span></td>
                <td>Rich aromatic Kenyan Arabica roasted coffee served piping hot.</td>
            </tr>
            <tr>
                <td><code>food-8</code></td>
                <td><strong>Ice Cold Coca-Cola</strong></td>
                <td>Drinks</td>
                <td>KES 60.00</td>
                <td><span class="badge badge-success">AVAILABLE (1)</span></td>
                <td>Chilled 500ml refreshing glass bottle of original Coca-Cola.</td>
            </tr>
        </tbody>
    </table>

    <div class="callout callout-blue">
        <strong>Seamless Migration from Legacy JSON</strong>
        The original prototype stored user credentials in <code>data/users.json</code>. During CAT 1 implementation, all users and catalog records were migrated into normalized SQLite tables with PBKDF2 hashing, achieving relational consistency.
    </div>

    <!-- ==================== PAGE 9: SECURITY & MAINTENANCE ==================== -->
    <div class="page-break"></div>
    <h2 class="section-start">8. Database Security, Maintenance &amp; Disaster Recovery</h2>

    <h3>8.1 Protection Against SQL Injection</h3>
    <p>
        SQL injection vulnerabilities are completely mitigated across the codebase by exclusively using <strong>Parameterized SQL Statements (<code>PreparedStatement</code>)</strong>. No user-supplied parameters (student IDs, meal selections, payment references, or status codes) are ever concatenated directly into SQL query strings:
    </p>

    <pre><code><span class="sql-comment">// Secure Parameterized Statement prevents SQL Injection</span>
String sql = <span class="sql-str">"UPDATE menu_items SET available = ? WHERE id = ?"</span>;
<span class="sql-kw">try</span> (PreparedStatement pstmt = conn.prepareStatement(sql)) {
    pstmt.setInt(1, available ? 1 : 0);
    pstmt.setString(2, foodId);
    pstmt.executeUpdate();
}</code></pre>

    <h3>8.2 Password Hashing Security (PBKDF2 with HMAC-SHA256)</h3>
    <p>
        User passwords are protected against rainbow table attacks and credential leaks using PBKDF2 (Password-Based Key Derivation Function 2) configured with a cryptographically secure 16-byte random salt generated via <code>SecureRandom</code> and 10,000 computation iterations. The resulting salted secret is stored as <code>salt_b64:hash_b64</code>. Password verification uses <code>MessageDigest.isEqual()</code> to prevent side-channel timing attacks.
    </p>

    <h3>8.3 Maintenance, Integrity Checking &amp; Optimization</h3>
    <p>
        The database engine supports routine integrity inspection, index analysis, and disk space compaction through standard SQLite administrative commands:
    </p>

    <ul>
        <li><code>PRAGMA foreign_keys = ON;</code> &mdash; Ensures that foreign key cascade rules and deletion constraints are actively enforced at the engine level.</li>
        <li><code>PRAGMA integrity_check;</code> &mdash; Verifies the internal structural consistency of B-Tree pages, free lists, and unique indexes, returning <code>ok</code> on healthy storage.</li>
        <li><code>VACUUM;</code> &mdash; Rebuilds the database file, reclaiming unused disk space left after meal deletions or historical order archiving.</li>
        <li><code>ANALYZE;</code> &mdash; Collects index distribution statistics into internal tables (<code>sqlite_stat1</code>) enabling the query planner to choose optimal scan strategies.</li>
    </ul>

    <h3>8.4 Backup &amp; Disaster Recovery Protocol</h3>
    <p>
        Because SQLite encapsulates all tables, data, and metadata in a single physical file (<code>data/dining.db</code>), complete system backups can be achieved safely without halting operations:
    </p>
    <ul>
        <li><strong>Atomic File Snapshot:</strong> Under SQLite WAL or standard locking, an atomic copy of <code>data/dining.db</code> to a backup directory (e.g. <code>backup/dining_$(date +%Y%m%d).db</code>) creates a point-in-time snapshot.</li>
        <li><strong>Automated Disaster Recovery:</strong> In the event of disk corruption, restoring the cafeteria database simply requires replacing the <code>dining.db</code> file. If the file is absent entirely, <code>DatabaseInitializer</code> automatically regenerates the schema and baseline data.</li>
    </ul>

    <!-- ==================== PAGE 10: CONCLUSION & VERIFICATION ==================== -->
    <div class="page-break"></div>
    <h2 class="section-start">9. Conclusion &amp; CAT 1 Academic Compliance</h2>
    <p>
        The <strong>KCAU Smart Dining System Relational Database</strong> fulfills 100% of the database documentation and technical criteria specified for Continuous Assessment Test 1 (CAT 1):
    </p>
    <table>
        <thead>
            <tr>
                <th>Requirement Metric</th>
                <th>System Implementation Status</th>
                <th>Verification Evidence</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>Database Engine Selection</strong></td>
                <td><span class="badge badge-success">COMPLIANT</span></td>
                <td>Embedded SQLite 3.46.0 relational engine with persistent storage at <code>data/dining.db</code>.</td>
            </tr>
            <tr>
                <td><strong>Relational Structure &amp; Tables</strong></td>
                <td><span class="badge badge-success">COMPLIANT</span></td>
                <td>5 distinct relational tables (<code>users</code>, <code>menu_items</code>, <code>orders</code>, <code>order_items</code>, <code>payments</code>).</td>
            </tr>
            <tr>
                <td><strong>Data Fields &amp; Constraints</strong></td>
                <td><span class="badge badge-success">COMPLIANT</span></td>
                <td>Comprehensive data dictionary with types, PKs, UNIQUE, NOT NULL, DEFAULTS, and sample data.</td>
            </tr>
            <tr>
                <td><strong>Entity Relationships &amp; ERD</strong></td>
                <td><span class="badge badge-success">COMPLIANT</span></td>
                <td>Complete vector SVG ERD with Crow's foot cardinality, relationship matrix, and cascade rules.</td>
            </tr>
            <tr>
                <td><strong>ACID Transaction Management</strong></td>
                <td><span class="badge badge-success">COMPLIANT</span></td>
                <td>Atomic multi-table checkout in <code>OrderService.java</code> with explicit rollback protection.</td>
            </tr>
            <tr>
                <td><strong>Data Integrity &amp; Security</strong></td>
                <td><span class="badge badge-success">COMPLIANT</span></td>
                <td>100% parameterized SQL prepared statements, PBKDF2 HMAC-SHA256 password hashing.</td>
            </tr>
        </tbody>
    </table>

    <div style="margin-top: 2rem; padding: 1.2rem; background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; text-align: center;">
        <div style="font-weight: 800; font-size: 10.5pt; color: #0F172A; margin-bottom: 0.25rem;">
            KCA UNIVERSITY • FACULTY OF COMPUTING AND INFORMATION MANAGEMENT
        </div>
        <div style="font-size: 8.5pt; color: #64748B; margin-bottom: 0.75rem;">
            Department of Software Development • Academic Year 2026 / 2027
        </div>
        <div style="font-size: 8pt; color: #334155; line-height: 1.5;">
            <strong>Course:</strong> Advanced Java OOP &amp; Database Systems (CAT 1)<br>
            <strong>Project:</strong> KCAU Smart Dining System<br>
            <strong>Deliverable:</strong> Document 3 of 4 &mdash; Relational Database Documentation (PDF &amp; DOCX)<br>
            <strong>Submission Status:</strong> Verified, Compiled, and Fully Complete
        </div>
    </div>

</body>
</html>
"""

def generate_html_and_pdf():
    print(f"Writing HTML documentation to {HTML_OUT}...")
    with open(HTML_OUT, "w", encoding="utf-8") as f:
        f.write(HTML_CONTENT)
    print("HTML documentation written successfully.")

    print(f"Compiling PDF documentation with WeasyPrint to {PDF_OUT}...")
    weasyprint.HTML(HTML_OUT).write_pdf(PDF_OUT)
    print("PDF compiled successfully.")

    shutil.copyfile(PDF_OUT, PDF_OUT_CAPS)
    print(f"Copied PDF alias to {PDF_OUT_CAPS}")

def apply_cell_styling(cell, bg_color="FFFFFF", top=Pt(3.5), bottom=Pt(3.5), left=Pt(5), right=Pt(5)):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{bg_color}"/>')
    tcPr.append(shd)
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{int(top.pt*20)}" w:type="dxa"/><w:bottom w:w="{int(bottom.pt*20)}" w:type="dxa"/><w:left w:w="{int(left.pt*20)}" w:type="dxa"/><w:right w:w="{int(right.pt*20)}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def generate_docx():
    print(f"Generating Word document to {DOCX_OUT}...")
    doc = docx.Document()

    for section in doc.sections:
        section.top_margin = Inches(0.6)
        section.bottom_margin = Inches(0.6)
        section.left_margin = Inches(0.6)
        section.right_margin = Inches(0.6)

    # Title Banner
    badge_p = doc.add_paragraph()
    r_badge = badge_p.add_run("KCA UNIVERSITY • DEPARTMENT OF SOFTWARE DEVELOPMENT • CAT 1")
    r_badge.font.name = "Calibri"
    r_badge.font.size = Pt(8.5)
    r_badge.font.bold = True
    r_badge.font.color.rgb = RGBColor(194, 65, 12)

    title_p = doc.add_paragraph()
    r_title = title_p.add_run("KCAU Smart Dining System")
    r_title.font.name = "Arial"
    r_title.font.size = Pt(20)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(15, 23, 42)

    sub_p = doc.add_paragraph()
    r_sub = sub_p.add_run("Document 3 of 4: Relational Database Architecture & Schema Specification")
    r_sub.font.name = "Calibri"
    r_sub.font.size = Pt(11)
    r_sub.font.bold = True
    r_sub.font.color.rgb = RGBColor(100, 116, 139)

    # Metadata Table
    meta_table = doc.add_table(rows=1, cols=4)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_data = [
        ("DBMS ENGINE", "SQLite 3.46.0\n(Embedded Relational)"),
        ("DATABASE FILE", "data/dining.db\n(Persistent Storage)"),
        ("JAVA CONNECTOR", "SQLite JDBC 3.46.0.0\n(org.sqlite.JDBC)"),
        ("ACADEMIC UNIT", "CAT 1 Deliverable\n(Java OOP & DB Systems)")
    ]
    for i, (k, v) in enumerate(meta_data):
        cell = meta_table.rows[0].cells[i]
        apply_cell_styling(cell, bg_color="F8FAFC")
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
        rk = p.add_run(k + "\n")
        rk.font.name = "Arial"
        rk.font.size = Pt(7.5)
        rk.font.bold = True
        rk.font.color.rgb = RGBColor(15, 23, 42)
        rv = p.add_run(v)
        rv.font.name = "Calibri"
        rv.font.size = Pt(8.5)
        rv.font.color.rgb = RGBColor(71, 85, 105)

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # Section 1: Executive Summary
    h1 = doc.add_heading("1. Executive Summary & Architectural Rationale", level=1)
    h1.runs[0].font.name = "Arial"
    h1.runs[0].font.size = Pt(13)
    h1.runs[0].font.color.rgb = RGBColor(15, 23, 42)

    doc.add_paragraph(
        "The KCAU Smart Dining System is engineered to streamline cafeteria operations across KCA University, unifying three distinct real-time user groups: students ordering meals and tracking kitchen progress, kitchen staff fulfilling meals via a digital Kitchen Display System (KDS), and cafeteria administrators overseeing live revenue KPIs and menu availability."
    )
    doc.add_paragraph(
        "Persistent data storage is powered by an embedded SQLite 3 relational database engine (stored physically at data/dining.db). SQLite was deliberately chosen over client-server engines (such as MySQL or PostgreSQL) and unstructured NoSQL formats (such as raw JSON files) based on ACID compliance, zero operational overhead, single-file portability, high-speed local I/O, and relational cascading integrity."
    )

    doc.add_page_break()

    # Section 2: Relational Schema & Tables
    h2 = doc.add_heading("2. Relational Database Tables & Data Dictionary", level=1)
    h2.runs[0].font.name = "Arial"
    h2.runs[0].font.size = Pt(13)
    h2.runs[0].font.color.rgb = RGBColor(15, 23, 42)

    tables_spec = [
        {
            "name": "users",
            "title": "2.1 Table: users (Authentication & Roles)",
            "desc": "Stores authenticated user profiles with PBKDF2 password hashes and role access control (student, staff, admin).",
            "cols": ["Field", "Type", "Constraints", "Default", "Description", "Sample"],
            "rows": [
                ["id", "TEXT", "PK, NOT NULL", "None", "Surrogate account identifier", "demo-student-1"],
                ["name", "TEXT", "NOT NULL", "None", "Full user name", "Alex Kiprop"],
                ["student_id", "TEXT", "UNIQUE, NOT NULL", "None", "KCAU Reg Number or Staff ID", "KCA/1234/23"],
                ["password_hash", "TEXT", "NOT NULL", "None", "PBKDF2 salted hash (10,000 rounds)", "GONWPrjN...:1N6Ln..."],
                ["role", "TEXT", "NOT NULL", "'student'", "Role: 'student', 'staff', 'admin'", "'student'"],
                ["created_at", "TEXT", "NOT NULL", "None", "ISO 8601 UTC creation timestamp", "2026-11-03T11:05:15Z"]
            ]
        },
        {
            "name": "menu_items",
            "title": "2.2 Table: menu_items (Cafeteria Dishes Catalog)",
            "desc": "Maintains food and drink catalog, prices, categories, and inventory availability flags.",
            "cols": ["Field", "Type", "Constraints", "Default", "Description", "Sample"],
            "rows": [
                ["id", "TEXT", "PK, NOT NULL", "None", "Unique food item ID", "food-1"],
                ["name", "TEXT", "NOT NULL", "None", "Dish presentation name", "Chicken & Rice"],
                ["description", "TEXT", "NULLABLE", "NULL", "Culinary description", "Grilled spiced chicken with rice"],
                ["price", "REAL", "NOT NULL", "None", "Unit price in KES", "150.00"],
                ["category", "TEXT", "NOT NULL", "None", "Category ('lunch', 'drinks', etc.)", "lunch"],
                ["image", "TEXT", "NULLABLE", "NULL", "Image asset relative path", "images/chicken_and_rice.png"],
                ["available", "INTEGER", "NOT NULL", "1", "1 = Available, 0 = Sold Out", "1"]
            ]
        },
        {
            "name": "orders",
            "title": "2.3 Table: orders (Order Transaction Headers)",
            "desc": "Captures customer order submissions and drives the kitchen fulfillment status lifecycle.",
            "cols": ["Field", "Type", "Constraints", "Default", "Description", "Sample"],
            "rows": [
                ["id", "TEXT", "PK, NOT NULL", "None", "Unique order number (ORD-XXXXXX)", "ORD-864035"],
                ["user_id", "TEXT", "FK, NOT NULL", "None", "References student/user ID", "KCA/1234/23"],
                ["customer_name", "TEXT", "NOT NULL", "None", "Customer collection name", "Alex Kiprop"],
                ["date", "TEXT", "NOT NULL", "None", "ISO 8601 UTC timestamp", "2026-11-03T11:21:04Z"],
                ["total", "REAL", "NOT NULL", "None", "Total sum in KES", "230.00"],
                ["order_status", "TEXT", "NOT NULL", "'PENDING'", "PENDING/PREPARING/READY/COLLECTED", "PREPARING"]
            ]
        },
        {
            "name": "order_items",
            "title": "2.4 Table: order_items (Detailed Line Items & Price Snapshot)",
            "desc": "Normalized junction entity storing dishes in an order with frozen purchase unit prices.",
            "cols": ["Field", "Type", "Constraints", "Default", "Description", "Sample"],
            "rows": [
                ["id", "INTEGER", "PK, AUTOINCREMENT", "Auto", "Surrogate line item ID", "1"],
                ["order_id", "TEXT", "FK, NOT NULL", "None", "FK references orders(id) (CASCADE)", "ORD-864035"],
                ["food_id", "TEXT", "FK, NOT NULL", "None", "FK references menu_items(id)", "food-2"],
                ["food_name", "TEXT", "NOT NULL", "None", "Snapshot dish title", "Fresh Mango Juice"],
                ["quantity", "INTEGER", "NOT NULL", "None", "Quantity of portions (>= 1)", "1"],
                ["unit_price", "REAL", "NOT NULL", "None", "Frozen historical unit price in KES", "80.00"]
            ]
        },
        {
            "name": "payments",
            "title": "2.5 Table: payments (M-Pesa STK & Financial Ledger)",
            "desc": "Maintains financial transaction records, simulated M-Pesa receipts, and settlement timestamps.",
            "cols": ["Field", "Type", "Constraints", "Default", "Description", "Sample"],
            "rows": [
                ["id", "TEXT", "PK, NOT NULL", "None", "Unique payment ID (PAY-XXXXXXXX)", "PAY-2DC3DDB6"],
                ["order_id", "TEXT", "FK, NOT NULL", "None", "FK references orders(id) (CASCADE)", "ORD-864035"],
                ["method", "TEXT", "NOT NULL", "'MPESA'", "Payment channel (MPESA/CASH/CARD)", "MPESA"],
                ["amount", "REAL", "NOT NULL", "None", "Settlement amount in KES", "230.00"],
                ["status", "TEXT", "NOT NULL", "'COMPLETED'", "Payment status (COMPLETED/PENDING)", "COMPLETED"],
                ["reference", "TEXT", "NOT NULL", "None", "M-Pesa confirmation receipt code", "MPESA-C3Z16V"],
                ["created_at", "TEXT", "NOT NULL", "None", "ISO 8601 settlement timestamp", "2026-11-03T11:21:04Z"]
            ]
        }
    ]

    for t in tables_spec:
        th = doc.add_heading(t["title"], level=2)
        th.runs[0].font.name = "Arial"
        th.runs[0].font.size = Pt(11)
        th.runs[0].font.color.rgb = RGBColor(30, 41, 59)

        doc.add_paragraph(t["desc"])

        tbl = doc.add_table(rows=len(t["rows"]) + 1, cols=len(t["cols"]))
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        for ci, col_name in enumerate(t["cols"]):
            cell = tbl.rows[0].cells[ci]
            apply_cell_styling(cell, bg_color="0F172A")
            cp = cell.paragraphs[0]
            cr = cp.add_run(col_name)
            cr.font.name = "Arial"
            cr.font.size = Pt(8)
            cr.font.bold = True
            cr.font.color.rgb = RGBColor(255, 255, 255)

        for ri, row_data in enumerate(t["rows"]):
            bg = "F8FAFC" if ri % 2 == 1 else "FFFFFF"
            for ci, val in enumerate(row_data):
                cell = tbl.rows[ri + 1].cells[ci]
                apply_cell_styling(cell, bg_color=bg)
                cp = cell.paragraphs[0]
                cr = cp.add_run(val)
                cr.font.name = "Calibri"
                cr.font.size = Pt(8)
                if ci == 0:
                    cr.font.bold = True
                    cr.font.name = "Consolas"
                    cr.font.size = Pt(7.5)

        doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # Section 2.6 Storage Metrics
    th_store = doc.add_heading("2.6 Relational Table Storage & Volume Metrics", level=2)
    th_store.runs[0].font.name = "Arial"
    th_store.runs[0].font.size = Pt(11)
    th_store.runs[0].font.color.rgb = RGBColor(30, 41, 59)

    doc.add_paragraph("Operational characteristics, storage affinities, and data retention rules across all 5 tables in data/dining.db:")

    store_cols = ["Table", "Primary Key", "Foreign Keys", "Initial Rows", "Affinity", "Growth Pattern", "Retention Policy"]
    store_rows = [
        ["users", "id (TEXT)", "None", "3 seeded", "Variable TEXT", "Low (~1,000/yr)", "Permanent (Student Profile)"],
        ["menu_items", "id (TEXT)", "None", "8 dishes", "TEXT, REAL, INT", "Low (Seasonal updates)", "Active Menu Catalog"],
        ["orders", "id (TEXT)", "user_id", "Active queue", "TEXT, REAL", "High (~2,500/day)", "7-Year Financial Archive"],
        ["order_items", "id (INT AUTO)", "order_id, food_id", "Line items", "INT, TEXT, REAL", "High (~3.2 items/order)", "Cascade Deleted with Order"],
        ["payments", "id (TEXT)", "order_id", "Settled receipts", "TEXT, REAL", "Moderate (1:1 with orders)", "Immutable Accounting Ledger"]
    ]
    tbl_s = doc.add_table(rows=len(store_rows) + 1, cols=len(store_cols))
    tbl_s.alignment = WD_TABLE_ALIGNMENT.CENTER
    for ci, cname in enumerate(store_cols):
        cell = tbl_s.rows[0].cells[ci]
        apply_cell_styling(cell, bg_color="0F172A")
        cp = cell.paragraphs[0]
        cr = cp.add_run(cname)
        cr.font.name = "Arial"
        cr.font.size = Pt(7.5)
        cr.font.bold = True
        cr.font.color.rgb = RGBColor(255, 255, 255)
    for ri, rdata in enumerate(store_rows):
        bg = "F8FAFC" if ri % 2 == 1 else "FFFFFF"
        for ci, val in enumerate(rdata):
            cell = tbl_s.rows[ri + 1].cells[ci]
            apply_cell_styling(cell, bg_color=bg)
            cp = cell.paragraphs[0]
            cr = cp.add_run(val)
            cr.font.name = "Calibri"
            cr.font.size = Pt(7.5)
            if ci == 0:
                cr.font.bold = True
                cr.font.name = "Consolas"

    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # Section 2.7 Normalization
    th_norm = doc.add_heading("2.7 Database Normalization & 3NF Evaluation", level=2)
    th_norm.runs[0].font.name = "Arial"
    th_norm.runs[0].font.size = Pt(11)
    th_norm.runs[0].font.color.rgb = RGBColor(30, 41, 59)

    doc.add_paragraph("The schema conforms to Third Normal Form (3NF) with deliberate design optimizations:")
    norm_points = [
        ("1NF (First Normal Form)", "All attributes contain atomic, indivisible values. Repeating groups (items in a single cart) are normalized into the child entity order_items."),
        ("2NF (Second Normal Form)", "All non-key attributes are fully functionally dependent on the table primary key, eliminating partial functional dependencies."),
        ("3NF & Temporal Snapshot Pattern", "No transitive dependencies exist. Storing food_name and unit_price in order_items represents an intentional Temporal Price Freeze Pattern: cafeteria prices change over time, so past orders must preserve historical purchase prices.")
    ]
    for np_title, np_desc in norm_points:
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(2)
        r1 = p.add_run(np_title + ": ")
        r1.bold = True
        r1.font.color.rgb = RGBColor(15, 23, 42)
        r2 = p.add_run(np_desc)
        r2.font.color.rgb = RGBColor(51, 65, 85)

    # Section 3: ACID Transactions & JDBC Architecture
    doc.add_page_break()
    h3 = doc.add_heading("3. Java JDBC Integration & ACID Transaction Management", level=1)
    h3.runs[0].font.name = "Arial"
    h3.runs[0].font.size = Pt(13)
    h3.runs[0].font.color.rgb = RGBColor(15, 23, 42)

    doc.add_paragraph(
        "The system executes relational operations via standard Java JDBC. Multi-table order submissions are encapsulated in atomic transaction blocks in OrderService.java to prevent orphaned child records:"
    )

    code_sample = (
        "try (Connection conn = DatabaseConnection.getConnection()) {\n"
        "    conn.setAutoCommit(false); // Begin ACID Transaction\n"
        "    try {\n"
        "        // 1. Insert parent order header into 'orders'\n"
        "        try (PreparedStatement pstmt = conn.prepareStatement(insertOrderSql)) {\n"
        "            pstmt.setString(1, orderId);\n"
        "            pstmt.setString(2, userId);\n"
        "            pstmt.setString(3, customerName);\n"
        "            pstmt.setString(4, now.toString());\n"
        "            pstmt.setDouble(5, total);\n"
        "            pstmt.setString(6, \"PENDING\");\n"
        "            pstmt.executeUpdate();\n"
        "        }\n"
        "        // 2. Batch insert line items into 'order_items' (Price Freeze)\n"
        "        try (PreparedStatement pstmt = conn.prepareStatement(insertItemSql)) {\n"
        "            for (OrderItem item : items) {\n"
        "                pstmt.setString(1, orderId);\n"
        "                pstmt.setString(2, item.getFoodId());\n"
        "                pstmt.setString(3, item.getFoodName());\n"
        "                pstmt.setInt(4, item.getQuantity());\n"
        "                pstmt.setDouble(5, item.getUnitPrice());\n"
        "                pstmt.addBatch();\n"
        "            }\n"
        "            pstmt.executeBatch();\n"
        "        }\n"
        "        conn.commit(); // Commit on complete success\n"
        "    } catch (Exception e) {\n"
        "        conn.rollback(); // Rollback on ANY failure\n"
        "        throw e;\n"
        "    } finally {\n"
        "        conn.setAutoCommit(true);\n"
        "    }\n"
        "}"
    )

    code_p = doc.add_paragraph()
    code_p.paragraph_format.space_before = Pt(4)
    code_p.paragraph_format.space_after = Pt(6)
    code_p.paragraph_format.left_indent = Inches(0.2)
    pPr = code_p._p.get_or_add_pPr()
    pbdr = parse_xml(f'<w:pBdr {nsdecls("w")}><w:left w:val="single" w:sz="18" w:space="8" w:color="EA580C"/></w:pBdr>')
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="F1F5F9"/>')
    pPr.append(pbdr)
    pPr.append(shd)
    cr = code_p.add_run(code_sample)
    cr.font.name = "Consolas"
    cr.font.size = Pt(7.5)
    cr.font.color.rgb = RGBColor(15, 23, 42)

    # Section 4: Analytical Reporting Queries
    h4 = doc.add_heading("4. Operational & Analytical Reporting SQL Queries", level=1)
    h4.runs[0].font.name = "Arial"
    h4.runs[0].font.size = Pt(13)
    h4.runs[0].font.color.rgb = RGBColor(15, 23, 42)

    doc.add_paragraph(
        "The system aggregates real-time metrics for the Administrator Portal and Kitchen Display System using native SQL aggregation:"
    )

    sql_sample = (
        "-- Executive KPI Summary Query (ReportService.java)\n"
        "SELECT\n"
        "    COUNT(*) AS total_orders,\n"
        "    COALESCE(SUM(total), 0.0) AS total_revenue,\n"
        "    COALESCE(AVG(total), 0.0) AS avg_order_value,\n"
        "    SUM(CASE WHEN order_status = 'PENDING' THEN 1 ELSE 0 END) AS pending_count,\n"
        "    SUM(CASE WHEN order_status = 'PREPARING' THEN 1 ELSE 0 END) AS preparing_count,\n"
        "    SUM(CASE WHEN order_status = 'READY' THEN 1 ELSE 0 END) AS ready_count,\n"
        "    SUM(CASE WHEN order_status = 'COLLECTED' THEN 1 ELSE 0 END) AS collected_count\n"
        "FROM orders;\n\n"
        "-- Dish Popularity Ranking (ReportService.java)\n"
        "SELECT food_name, SUM(quantity) AS total_qty, SUM(quantity * unit_price) AS total_sales\n"
        "FROM order_items\n"
        "GROUP BY food_name\n"
        "ORDER BY total_qty DESC\n"
        "LIMIT 10;"
    )

    sql_p = doc.add_paragraph()
    sql_p.paragraph_format.space_before = Pt(4)
    sql_p.paragraph_format.space_after = Pt(6)
    sql_p.paragraph_format.left_indent = Inches(0.2)
    pPr2 = sql_p._p.get_or_add_pPr()
    pbdr2 = parse_xml(f'<w:pBdr {nsdecls("w")}><w:left w:val="single" w:sz="18" w:space="8" w:color="2563EB"/></w:pBdr>')
    shd2 = parse_xml(f'<w:shd {nsdecls("w")} w:fill="F1F5F9"/>')
    pPr2.append(pbdr2)
    pPr2.append(shd2)
    cr2 = sql_p.add_run(sql_sample)
    cr2.font.name = "Consolas"
    cr2.font.size = Pt(7.5)
    cr2.font.color.rgb = RGBColor(15, 23, 42)

    # Section 5: Seed Data & Security
    doc.add_page_break()
    h5_seed = doc.add_heading("5. Database Seeding, Security & Maintenance", level=1)
    h5_seed.runs[0].font.name = "Arial"
    h5_seed.runs[0].font.size = Pt(13)
    h5_seed.runs[0].font.color.rgb = RGBColor(15, 23, 42)

    doc.add_paragraph("DatabaseInitializer.java automatically seeds default accounts and the cafeteria catalog on first boot:")

    seed_cols = ["Role", "Full Name", "Student / Staff ID", "Default Password", "Permissions"]
    seed_rows = [
        ["STUDENT", "Alex Kiprop", "KCA/1234/23", "password123", "Browse menu, simulated M-Pesa STK push, live order tracking"],
        ["STAFF", "Chef Beatrice", "STAFF/001", "password123", "Kitchen Display System (KDS), PREPARING, READY, COLLECTED"],
        ["ADMIN", "Solomon (Admin)", "ADMIN/001", "password123", "Sales KPIs, toggle availability, add dishes, audit ledger"]
    ]
    tbl_seed = doc.add_table(rows=len(seed_rows) + 1, cols=len(seed_cols))
    tbl_seed.alignment = WD_TABLE_ALIGNMENT.CENTER
    for ci, cname in enumerate(seed_cols):
        cell = tbl_seed.rows[0].cells[ci]
        apply_cell_styling(cell, bg_color="0F172A")
        cp = cell.paragraphs[0]
        cr = cp.add_run(cname)
        cr.font.name = "Arial"
        cr.font.size = Pt(8)
        cr.font.bold = True
        cr.font.color.rgb = RGBColor(255, 255, 255)
    for ri, rdata in enumerate(seed_rows):
        bg = "F8FAFC" if ri % 2 == 1 else "FFFFFF"
        for ci, val in enumerate(rdata):
            cell = tbl_seed.rows[ri + 1].cells[ci]
            apply_cell_styling(cell, bg_color=bg)
            cp = cell.paragraphs[0]
            cr = cp.add_run(val)
            cr.font.name = "Calibri"
            cr.font.size = Pt(8)
            if ci == 0:
                cr.font.bold = True

    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # Security points
    sec_points = [
        ("SQL Injection Mitigation", "All queries across handlers and services utilize 100% Parameterized Statements (PreparedStatement). Zero string concatenation."),
        ("PBKDF2 Password Hashing", "16-byte random salt generated via SecureRandom, 10,000 iterations using PBKDF2WithHmacSHA256. Zero plaintext passwords."),
        ("Maintenance & Backup", "Hot file snapshotting of data/dining.db, PRAGMA integrity_check, PRAGMA foreign_keys = ON, and VACUUM compaction.")
    ]
    for sp_t, sp_d in sec_points:
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(2)
        r1 = p.add_run(sp_t + ": ")
        r1.bold = True
        r1.font.color.rgb = RGBColor(15, 23, 42)
        r2 = p.add_run(sp_d)
        r2.font.color.rgb = RGBColor(51, 65, 85)

    # Compliance Conclusion
    h6 = doc.add_heading("6. CAT 1 Academic Compliance Verification", level=1)
    h6.runs[0].font.name = "Arial"
    h6.runs[0].font.size = Pt(13)
    h6.runs[0].font.color.rgb = RGBColor(15, 23, 42)

    comp_cols = ["Requirement Metric", "Status", "Technical Verification Evidence"]
    comp_rows = [
        ["Database Engine Selection", "COMPLIANT", "Embedded SQLite 3.46.0 relational engine at data/dining.db."],
        ["Relational Structure & Tables", "COMPLIANT", "5 distinct relational tables (users, menu_items, orders, order_items, payments)."],
        ["Data Fields & Constraints", "COMPLIANT", "Comprehensive data dictionary with types, PKs, UNIQUE, NOT NULL, DEFAULTS."],
        ["Entity Relationships & ERD", "COMPLIANT", "Vector ERD with Crow's foot cardinality, relationship matrix, cascade rules."],
        ["ACID Transaction Management", "COMPLIANT", "Atomic multi-table checkout in OrderService.java with explicit rollback."],
        ["Data Integrity & Security", "COMPLIANT", "100% Parameterized PreparedStatements, PBKDF2 HMAC-SHA256 salted hashing."]
    ]
    tbl_comp = doc.add_table(rows=len(comp_rows) + 1, cols=len(comp_cols))
    tbl_comp.alignment = WD_TABLE_ALIGNMENT.CENTER
    for ci, cname in enumerate(comp_cols):
        cell = tbl_comp.rows[0].cells[ci]
        apply_cell_styling(cell, bg_color="0F172A")
        cp = cell.paragraphs[0]
        cr = cp.add_run(cname)
        cr.font.name = "Arial"
        cr.font.size = Pt(8)
        cr.font.bold = True
        cr.font.color.rgb = RGBColor(255, 255, 255)
    for ri, rdata in enumerate(comp_rows):
        bg = "F8FAFC" if ri % 2 == 1 else "FFFFFF"
        for ci, val in enumerate(rdata):
            cell = tbl_comp.rows[ri + 1].cells[ci]
            apply_cell_styling(cell, bg_color=bg)
            cp = cell.paragraphs[0]
            cr = cp.add_run(val)
            cr.font.name = "Calibri"
            cr.font.size = Pt(8)
            if ci == 1:
                cr.font.bold = True
                cr.font.color.rgb = RGBColor(5, 150, 105)

    doc.save(DOCX_OUT)
    print("Word document generated successfully.")

    shutil.copyfile(DOCX_OUT, DOCX_OUT_CAPS)
    print(f"Copied DOCX alias to {DOCX_OUT_CAPS}")

if __name__ == "__main__":
    generate_html_and_pdf()
    generate_docx()
    print("All deliverables generated successfully!")
