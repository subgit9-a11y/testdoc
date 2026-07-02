import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.units import inch

def generate_pdf():
    pdf = r"c:\Users\SUBHASH\Desktop\astrafinalneed\astra\Astra_AI_Complete_Feature_List.pdf"
    doc = SimpleDocTemplate(pdf, pagesize=letter, rightMargin=45, leftMargin=45, topMargin=45, bottomMargin=45)
    styles = getSampleStyleSheet()

    # Styles
    cover_t = ParagraphStyle('CT', parent=styles['Heading1'], fontSize=28, spaceAfter=10, alignment=TA_CENTER, textColor=HexColor("#0d4f4f"))
    cover_s = ParagraphStyle('CS', parent=styles['Heading2'], fontSize=14, spaceAfter=8, alignment=TA_CENTER, textColor=HexColor("#555"))
    section_t = ParagraphStyle('ST', parent=styles['Heading1'], fontSize=20, spaceBefore=15, spaceAfter=10, textColor=HexColor("#0d4f4f"))
    feat_name = ParagraphStyle('FN', parent=styles['Normal'], fontSize=12, spaceAfter=3, fontName="Helvetica-Bold", textColor=HexColor("#1e3a8a"))
    feat_desc = ParagraphStyle('FD', parent=styles['Normal'], fontSize=10, spaceAfter=10, leftIndent=15, textColor=HexColor("#374151"))
    stat_label = ParagraphStyle('SL', parent=styles['Normal'], fontSize=11, alignment=TA_CENTER, textColor=HexColor("#047857"), fontName="Helvetica-Bold")

    story = []

    # ==================== COVER PAGE ====================
    story.append(Spacer(1, 80))
    story.append(Paragraph("Astra AI Wellness Companion", cover_t))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Complete Feature Documentation", cover_s))
    story.append(Spacer(1, 30))
    story.append(Paragraph("Version 2.0 - Security Hardened Architecture", ParagraphStyle('V', parent=styles['Normal'], fontSize=11, alignment=TA_CENTER, textColor=HexColor("#047857"))))
    story.append(Spacer(1, 15))
    story.append(Paragraph("May 2026", ParagraphStyle('D', parent=styles['Normal'], fontSize=10, alignment=TA_CENTER, textColor=HexColor("#9ca3af"))))
    story.append(Spacer(1, 50))

    # Stats boxes
    stats = [["11", "64", "11"],
             ["Major Modules", "Production Features", "Security Layers"]]
    st = Table(stats, colWidths=[2.2*inch, 2.2*inch, 2.2*inch])
    st.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTSIZE', (0,0), (-1,0), 28),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0,0), (-1,0), HexColor("#0d4f4f")),
        ('FONTSIZE', (0,1), (-1,1), 10),
        ('TEXTCOLOR', (0,1), (-1,1), HexColor("#6b7280")),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(st)
    story.append(PageBreak())

    # ==================== TABLE OF CONTENTS ====================
    story.append(Paragraph("Table of Contents", section_t))
    story.append(Spacer(1, 10))
    toc = [
        "Section A: Astra Companion - Core AI Chat (11 Features)",
        "Section B: Astra Fill - Health Intake (4 Features)",
        "Section C: Astra Autopilot - Proactive Care (5 Features)",
        "Section D: Meditation &amp; Yoga (5 Features)",
        "Section E: Smart Cart &amp; Shopify Integration (5 Features)",
        "Section F: Prescription &amp; PDF (5 Features)",
        "Section G: Payments (3 Features)",
        "Section H: Notifications &amp; Reminders (3 Features)",
        "Section I: WhatsApp Omnichannel (3 Features)",
        "Section J: Doctor Ecosystem (4 Features)",
        "Section K: EHR Management - Electronic Health Records (6 Features)",
        "Section L: Security &amp; Infrastructure (11 Features)",
        "Appendix: Complete Feature Matrix",
    ]
    for i, item in enumerate(toc, 1):
        story.append(Paragraph(f"<b>{i}.</b> {item}", ParagraphStyle('TOC', parent=styles['Normal'], fontSize=11, spaceAfter=6, leftIndent=15)))
    story.append(PageBreak())

    # ==================== HELPER ====================
    def add_feature(num, name, description):
        story.append(Paragraph(f"Feature #{num}: {name}", feat_name))
        story.append(Paragraph(description, feat_desc))

    # ==================== SECTION A ====================
    story.append(Paragraph("Section A: Astra Companion - Core AI Chat", section_t))
    story.append(Paragraph("The primary AI-powered conversational interface that serves as the patient's personal wellness assistant.", feat_desc))
    story.append(Spacer(1, 8))

    add_feature(1, "AI Wellness Chat",
        "Text-based conversational AI that analyzes patient symptoms, provides Ayurvedic wellness guidance, and routes to human doctors when necessary. Powered by OpenAI/Anthropic with strict medical guardrails.")
    add_feature(2, "Voice-to-Text Chat",
        "Patients can speak their symptoms using the microphone. Audio is processed via Speech-to-Text on-device, then passed through the Voice Confirmation Gate before reaching the AI.")
    add_feature(3, "Multilingual Support (IndicTrans2)",
        "Full support for 12+ Indian languages including Hindi, Tamil, Telugu, Kannada, Bengali, Marathi, Gujarati, Malayalam, Punjabi, Odia, Assamese, and Urdu. Powered by IndicTrans2 translation service.")
    add_feature(4, "Rolling Context Summarizer",
        "As conversations grow beyond 20 messages, the system automatically compresses older messages into concise summaries while preserving critical medical context. Prevents token overflow without losing patient history.")
    add_feature(5, "Conversation Pruner",
        "Actively manages the AI context window by intelligently removing low-priority messages while permanently retaining safety guardrails. Ensures the AI never forgets its core medical protocols.")
    add_feature(6, "Cultural Clarification Protocol",
        "When a patient uses regional idioms or slang (e.g., 'chest burning' meaning acid reflux), the AI asks one explicit clarifying question before assigning clinical severity, preventing false emergency escalations.")
    add_feature(7, "Safety Middleware (Deterministic)",
        "An offline-safe, regex-based scanner that runs before the AI. Detects chest pain, breathing issues, severe bleeding, seizures, and suicidal ideation. Operates even if the AI API is down.")
    add_feature(8, "SOS Emergency Lock &amp; Doctor Routing",
        "When a critical medical emergency is detected, the chat is permanently locked, an SOS button appears (calling 112), and the assigned doctor is instantly notified via Firebase push notification.")
    add_feature(9, "Voice Synthesis / Text-to-Speech",
        "The AI can speak its responses back to the patient using natural-sounding voice synthesis. Supports multiple voice profiles and languages for accessibility.")
    add_feature(10, "Ayurveda Model Service",
        "A specialized AI layer that provides dosha-specific (Vata/Pitta/Kapha) wellness guidance, integrating traditional Ayurvedic principles with modern symptom analysis.")
    add_feature(11, "Native App Home Dashboard",
        "A central Flutter hub where the patient lands upon login. Features a prominent 'Start My Journey' button to enter Companion mode, alongside quick-access cards for the EHR Vault and Meditation Player, allowing direct use without chatting.")
    story.append(PageBreak())

    # ==================== SECTION B ====================
    story.append(Paragraph("Section B: Astra Fill - Health Intake", section_t))
    story.append(Paragraph("An intelligent health data collection module that extracts structured medical information from natural voice or text input.", feat_desc))
    story.append(Spacer(1, 8))

    add_feature(11, "Voice Transcript Health Intake",
        "Patients speak their medical history naturally (e.g., 'I've been taking paracetamol for two days and I'm allergic to penicillin'). The system transcribes and processes this into structured health data.")
    add_feature(12, "Two-Phase Voice Confirmation Gate",
        "Phase 1: Speech-to-Text runs, returns raw transcript with a pending_id. Flutter shows: 'I heard: [text]. Is this correct? [Yes / Edit]'. Phase 2: Only after patient confirms does AI extraction run. Prevents dangerous medical data errors.")
    add_feature(13, "AI-Powered Data Extraction",
        "Uses natural language processing to extract structured fields from free-form text: symptoms, allergies, current medications, dosages, duration, and severity scores.")
    add_feature(14, "Health Profile Builder",
        "Compiles extracted data into a comprehensive patient health profile stored in Supabase, including symptom tags, allergies, blood type, medication history, and lifestyle factors.")
    story.append(PageBreak())

    # ==================== SECTION C ====================
    story.append(Paragraph("Section C: Astra Autopilot - Proactive Care", section_t))
    story.append(Paragraph("An autonomous care management engine that proactively monitors patient health journeys and suggests actions without requiring patient initiation.", feat_desc))
    story.append(Spacer(1, 8))

    add_feature(15, "Autopilot Consent Management",
        "Patients must explicitly opt-in to Autopilot via a toggle switch. Consent is stored in Supabase and can be revoked at any time. The system never acts without patient permission.")
    add_feature(16, "Daily Autonomous Scheduler",
        "Runs automatically at 9:00 AM every day via background workers. The system autonomously scans all enabled patients' care journeys without them needing to open the app or send a message.")
    add_feature(17, "Follow-Up Orchestration",
        "Automatically calculates a follow-up window (15 days after the last consultation). When the window opens, the daily scheduler prepares a suggestion card: 'Time for a follow-up with Dr. Sharma. Book now?'")
    add_feature(18, "Medicine Refill Intelligence",
        "Tracks the medicine_end_date from the last prescription. When only 5 days of medicine remain, the daily scheduler proactively alerts the patient: 'Your Ashwagandha is running low. Reorder?'")
    add_feature(19, "Morning Wellness Check-Ins",
        "Acts as a daily companion by sending proactive morning check-ins asking about side effects or general wellness. Powered by the O-D-P Decision Loop: Observe (read Supabase events), Decide (evaluate rules), Prepare (write draft actions).")
    story.append(PageBreak())

    # ==================== SECTION D ====================
    story.append(Paragraph("Section D: Meditation &amp; Yoga", section_t))
    story.append(Paragraph("AI-generated and locally-cached wellness content for guided meditation, breathing exercises, and personalized yoga plans.", feat_desc))
    story.append(Spacer(1, 8))

    add_feature(20, "Guided Meditation Scripts",
        "Generates personalized meditation sessions for five focus areas: Stress Relief, Sleep, Anxiety, Energy, and Concentration. Each script includes an Opening, Body Scan, Main Practice, optional Mantras, and Closing.")
    add_feature(21, "Dosha-Specific Meditation",
        "Adapts meditation guidance based on the patient's Ayurvedic body type: Vata (grounding), Pitta (cooling), or Kapha (energizing). Provides dosha-appropriate language and breathing patterns.")
    add_feature(22, "Breathing Exercises (Pranayama)",
        "Four guided breathing techniques: 4-7-8 Relaxing Breath, Box Breathing (Sama Vritti), Alternate Nostril Breathing (Nadi Shodhana), and Bee Breath (Bhramari Pranayama). Each with timed guided scripts.")
    add_feature(23, "Mantra Integration",
        "Optional sacred sound integration including Om, Om Shanti, Om Tryambakam (healing), and Om Gam Ganapataye (energy). Mantras are mapped to meditation focus areas.")
    add_feature(24, "AI-Generated Yoga Plans",
        "Personalized yoga routines for specific conditions (Back Pain, Stress Relief, Flexibility). Includes pose-by-pose instructions, duration per pose, and safety warnings for chronic conditions.")
    story.append(PageBreak())

    # ==================== SECTION E ====================
    story.append(Paragraph("Section E: Smart Cart &amp; Shopify Integration", section_t))
    story.append(Paragraph("End-to-end e-commerce integration connecting AI-analyzed symptoms to Shopify product fulfillment.", feat_desc))
    story.append(Spacer(1, 8))

    add_feature(25, "Automated Draft Order Creation",
        "When a doctor approves a prescription, the system automatically maps prescribed medicines to Shopify product variants and creates a draft order with correct quantities, prices, and patient shipping details.")
    add_feature(26, "Product Mapping Engine",
        "A comprehensive mapping system (95,000+ bytes of product data) that translates medical prescriptions into exact Shopify product variant IDs. Supports fuzzy matching for medicine name variations.")
    add_feature(27, "Real COD Order Creation",
        "Supports Cash-on-Delivery orders by creating real Shopify orders (not drafts) that are immediately queued for fulfillment without requiring online payment.")
    add_feature(28, "Shopify Auto-Sync",
        "Automatically synchronizes the complete Shopify product catalog to the local database every 6 hours, ensuring product availability, pricing, and variant data is always current.")
    add_feature(29, "Shopify Webhook Handler",
        "Processes incoming Shopify webhooks for order payment verification, fulfillment updates, and inventory changes. Protected by HMAC signature verification.")
    story.append(PageBreak())

    # ==================== SECTION F ====================
    story.append(Paragraph("Section F: Prescription &amp; PDF", section_t))
    story.append(Paragraph("Complete prescription lifecycle management from creation to cryptographically-signed PDF delivery.", feat_desc))
    story.append(Spacer(1, 8))

    add_feature(30, "Prescription PDF Generation (Celery Worker)",
        "Generates professional prescription PDFs using ReportLab. Offloaded to an isolated Celery background worker to prevent RAM spikes from crashing the main API server.")
    add_feature(31, "Cryptographic QR Code Signing",
        "Every generated PDF contains a unique QR code encoding a verification URL (ayureze.com/verify/{hash}). The hash is a cryptographic signature that allows pharmacies to mathematically prove the document was not tampered with.")
    add_feature(32, "Wasabi Cloud Storage Upload",
        "All generated PDFs are automatically uploaded to Wasabi S3-compatible cloud storage for permanent, reliable, and cost-effective archival with signed download URLs.")
    add_feature(33, "Email Prescription Delivery",
        "Prescription PDFs are automatically emailed to patients via SMTP/Firebase email service with the PDF attached, providing an instant digital copy.")
    add_feature(34, "Prescription Approval Workflow",
        "A multi-step workflow: Create (AI suggests) > Doctor Review > Approve/Reject/Modify > Process (trigger PDF + Cart). Every step requires authenticated Doctor JWT tokens.")
    story.append(PageBreak())

    # ==================== SECTION G ====================
    story.append(Paragraph("Section G: Payments", section_t))
    story.append(Paragraph("Native in-app payment processing and financial tracking.", feat_desc))
    story.append(Spacer(1, 8))

    add_feature(35, "Razorpay In-App Checkout",
        "Native Razorpay SDK integration within the Flutter app supporting UPI, Credit/Debit Cards, Net Banking, and Wallet payments. Provides a seamless checkout experience without leaving the app.")
    add_feature(36, "Payment Verification Webhooks",
        "Server-side payment verification using Razorpay signature validation. Ensures payment authenticity before marking orders as PAID in Shopify.")
    add_feature(37, "Finance Service",
        "Internal revenue tracking and payout split simulation for multi-party transactions between AyurEze, doctors, and delivery partners.")
    story.append(PageBreak())

    # ==================== SECTION H ====================
    story.append(Paragraph("Section H: Notifications &amp; Reminders", section_t))
    story.append(Paragraph("Automated patient engagement through scheduled push notifications and medicine reminders.", feat_desc))
    story.append(Spacer(1, 8))

    add_feature(38, "Morning &amp; Evening Medicine Reminders",
        "Automated push notifications sent exactly at 8:00 AM and 8:00 PM daily to remind patients to take their prescribed medicines. The companion is with them twice a day to ensure adherence.")
    add_feature(39, "Firebase Push Notifications",
        "Real-time push notifications via Firebase Cloud Messaging for doctor assignments, prescription approvals, payment confirmations, and emergency alerts.")
    add_feature(40, "Advanced Notification Scheduling",
        "A flexible scheduling engine that supports custom notification times, recurring schedules, and condition-based triggers (e.g., send reminder only if patient hasn't confirmed dose).")
    story.append(PageBreak())

    # ==================== SECTION I ====================
    story.append(Paragraph("Section I: WhatsApp Omnichannel", section_t))
    story.append(Paragraph("Extends the AI companion experience to WhatsApp, enabling patients to interact via their most familiar messaging platform.", feat_desc))
    story.append(Spacer(1, 8))

    add_feature(41, "WhatsApp Companion Chat",
        "The same Astra AI brain that powers the Flutter app also processes WhatsApp messages. Patients can describe symptoms, receive guidance, and get doctor referrals directly through WhatsApp.")
    add_feature(42, "WhatsApp Autopilot Follow-Ups",
        "The Autopilot engine sends proactive morning check-in messages via WhatsApp: 'Good morning! How are you feeling after your Ashwagandha? Any side effects?' Patients reply naturally.")
    add_feature(43, "WhatsApp Webhook Handler",
        "Processes incoming WhatsApp messages via webhook, maps phone numbers to patient profiles in Supabase, and routes responses back through the WhatsApp Business API.")
    story.append(PageBreak())

    # ==================== SECTION J ====================
    story.append(Paragraph("Section J: Doctor Ecosystem", section_t))
    story.append(Paragraph("Backend infrastructure supporting the Doctor App and Admin Panel for clinical workflow management.", feat_desc))
    story.append(Spacer(1, 8))

    add_feature(44, "Doctor Authentication (Firebase JWT)",
        "Doctors authenticate via Firebase with cryptographic JWT tokens. Every clinical endpoint (prescriptions, orders, approvals) requires a valid doctor token, preventing unauthorized access.")
    add_feature(45, "Doctor Prescription Submission",
        "Doctors can review AI-generated symptom analyses, modify diagnoses, and submit final prescriptions that automatically trigger the Smart Cart and PDF generation pipeline.")
    add_feature(46, "Patient Management Dashboard",
        "API endpoints for doctors to view their assigned patients, consultation history, active prescriptions, and treatment progress.")
    add_feature(47, "Buddy Matching Service",
        "An intelligent patient-doctor pairing system that matches patients with appropriate doctors based on specialization, availability, and patient preferences.")
    story.append(PageBreak())

    # ==================== SECTION K: EHR ====================
    story.append(Paragraph("Section K: EHR Management - Electronic Health Records", section_t))
    story.append(Paragraph("A complete cloud-based medical document vault powered by Wasabi S3 storage and Supabase metadata tracking, enabling secure upload, retrieval, sharing, and audit of all patient medical records.", feat_desc))
    story.append(Spacer(1, 8))

    add_feature(48, "Document Upload to Cloud EHR Vault",
        "Patients and doctors can upload medical documents (prescriptions, lab reports, X-rays, MRIs, CT scans) directly to the encrypted Wasabi S3 cloud storage with automatic metadata indexing in Supabase.")
    add_feature(49, "Per-Patient Document Listing",
        "API endpoint to retrieve all EHR documents belonging to a specific patient, filterable by document type (prescription, lab_report, xray, mri, ct_scan). Returns file size, upload date, and download counts.")
    add_feature(50, "Secure Document Download",
        "Stream-based document download from Wasabi with automatic download count tracking. Documents are streamed through temporary files to minimize server memory usage.")
    add_feature(51, "Time-Limited Shareable Links",
        "Generates cryptographically pre-signed download URLs with configurable expiration (default: 24 hours). Links become invalid after expiry, ensuring documents cannot be accessed indefinitely.")
    add_feature(52, "WhatsApp Document Sharing",
        "Doctors can share medical documents directly to a patient's WhatsApp number via the custom WhatsApp Business API integration. Includes document type emoji, filename, and auto-expiring secure link.")
    add_feature(53, "Document Metadata &amp; Audit Trail",
        "Complete metadata tracking per document: file size, content type, upload timestamp, uploader ID, download count, share count, sharing history (link vs WhatsApp), and related prescription cross-references.")
    story.append(PageBreak())

    # ==================== SECTION L ====================
    story.append(Paragraph("Section L: Security &amp; Infrastructure", section_t))
    story.append(Paragraph("Production-grade security layers and infrastructure hardening implemented to protect the platform against hacking, data breaches, and system crashes.", feat_desc))
    story.append(Spacer(1, 8))

    add_feature(54, "PgBouncer Connection Multiplexer",
        "Routes all database connections through Supabase PgBouncer (port 6543) instead of direct PostgreSQL (port 5432). Safely funnels 10,000 concurrent connections into 50 stable database connections.")
    add_feature(55, "Immutable Audit Ledger",
        "A write-only Supabase table (immutable_audit_logs) that permanently records every AI response, doctor action, and cart payload. Enforced by Row-Level Security policies that physically block UPDATE and DELETE.")
    add_feature(56, "XSS Output Sanitizer",
        "Scrubs all AI-generated text through a regex-based HTML/JavaScript stripper before returning to users or saving to the database, preventing AI-driven Cross-Site Scripting attacks.")
    add_feature(57, "Token Budget Monitor (Denial of Wallet)",
        "Redis-based per-user token tracking. If any patient_id exceeds 2,000 tokens in a single hour, the account is instantly frozen and flagged for human review, preventing API credit drainage attacks.")
    add_feature(58, "SSL Doomsday Monitor",
        "A nightly cron job (1:00 AM) that physically connects to all critical platform domains, downloads the live SSL certificate, and triggers a CRITICAL alert if any certificate expires within 14 days.")
    add_feature(59, "Webhook Payload Middleware",
        "Custom Nginx and FastAPI middleware that increases the payload limit to 50MB specifically for /api/v1/payments and /shopify routes while enforcing a strict 2MB limit on all other endpoints.")
    add_feature(60, "Celery PDF Worker",
        "An isolated background worker process (worker_concurrency=2, max_tasks_per_child=50) that handles RAM-intensive PDF generation, preventing the Linux OOM-Killer from assassinating the main API server.")
    add_feature(61, "Redis Cache Layer",
        "High-speed in-memory caching for journey states, token budgets, abuse flags, and session data. Provides sub-millisecond data retrieval for real-time chat performance.")
    add_feature(62, "Rate Limiter",
        "Configurable per-endpoint rate limiting to prevent brute-force attacks, API abuse, and automated scraping.")
    add_feature(63, "Prompt Injection Protection (Zero-Trust)",
        "The AI companion has zero programmatic access to Shopify, prescription, or financial endpoints. All transactional routes require authenticated Doctor JWT tokens, making prompt injection attacks structurally impossible.")

    # ==================== APPENDIX ====================
    story.append(PageBreak())
    story.append(Paragraph("Appendix: Complete Feature Matrix", section_t))
    story.append(Spacer(1, 10))

    data = [["#", "Module", "Feature Count", "Key Technologies"]]
    rows = [
        ("A", "Astra Companion Chat", "11", "OpenAI, IndicTrans2, Redis"),
        ("B", "Astra Fill", "4", "Speech-to-Text, NLP Extraction"),
        ("C", "Astra Autopilot", "5", "Supabase, Cron Scheduler"),
        ("D", "Meditation &amp; Yoga", "5", "ReportLab, AI Generation"),
        ("E", "Smart Cart &amp; Shopify", "5", "Shopify API, Product Mapper"),
        ("F", "Prescription &amp; PDF", "5", "Celery, Wasabi, QR Crypto"),
        ("G", "Payments", "3", "Razorpay SDK"),
        ("H", "Notifications", "3", "Firebase Cloud Messaging"),
        ("I", "WhatsApp", "3", "WhatsApp Business API"),
        ("J", "Doctor Ecosystem", "4", "Firebase Auth, JWT"),
        ("K", "EHR Management", "6", "Wasabi S3, Supabase, WhatsApp"),
        ("L", "Security", "10", "Redis, PgBouncer, Nginx"),
    ]
    for r in rows:
        data.append(list(r))
    data.append(["", "TOTAL", "64", ""])

    t = Table(data, colWidths=[0.4*inch, 2.5*inch, 1.2*inch, 2.7*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), HexColor("#0d4f4f")),
        ('TEXTCOLOR', (0,0), (-1,0), white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, HexColor("#d1d5db")),
        ('ROWBACKGROUNDS', (0,1), (-1,-2), [white, HexColor("#f3f4f6")]),
        ('BACKGROUND', (0,-1), (-1,-1), HexColor("#e5e7eb")),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
    ]))
    story.append(t)

    doc.build(story)
    print("Feature List PDF Generated Successfully!")

if __name__ == "__main__":
    generate_pdf()
