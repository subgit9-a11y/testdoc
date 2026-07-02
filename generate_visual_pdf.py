import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.colors import HexColor, white
from reportlab.lib.units import inch

IMG_DIR = r"C:\Users\SUBHASH\.gemini\antigravity\brain\55f719cb-b688-4ee9-ae7c-5302aba210d0"

def find_img(prefix):
    for f in sorted(os.listdir(IMG_DIR)):
        if f.startswith(prefix) and f.endswith(".png"):
            return os.path.join(IMG_DIR, f)
    return None

def generate_pdf():
    pdf = r"c:\Users\SUBHASH\Desktop\astrafinalneed\astra\Astra_Complete_App_Flow.pdf"
    doc = SimpleDocTemplate(pdf, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()

    title_s = ParagraphStyle('T', parent=styles['Heading1'], fontSize=26, spaceAfter=10, alignment=TA_CENTER, textColor=HexColor("#0d4f4f"))
    screen_s = ParagraphStyle('S', parent=styles['Heading2'], fontSize=18, spaceAfter=8, alignment=TA_CENTER, textColor=HexColor("#047857"))
    desc_s = ParagraphStyle('D', parent=styles['Normal'], fontSize=11, spaceAfter=6, leftIndent=15)
    sec_s = ParagraphStyle('X', parent=styles['Normal'], fontSize=10, spaceAfter=8, leftIndent=15, textColor=HexColor("#991b1b"), fontName="Helvetica-BoldOblique")

    story = []

    # Cover
    story.append(Spacer(1, 120))
    story.append(Paragraph("Astra AI Wellness Companion", title_s))
    story.append(Paragraph("Complete App Flow - All Features &amp; Screens", ParagraphStyle('Sub', parent=styles['Heading2'], alignment=TA_CENTER)))
    story.append(Spacer(1, 40))
    story.append(Paragraph("Covers: Astra Companion Chat, Astra Fill, Astra Autopilot, Meditation &amp; Yoga, Smart Cart, Prescription PDF, WhatsApp Omnichannel, and all Security Layers.", desc_s))
    story.append(PageBreak())

    def esc(t): return t.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

    def add_page(title, subtitle, img_prefix, actions, security):
        story.append(Paragraph(title, screen_s))
        story.append(Paragraph(esc(subtitle), desc_s))
        story.append(Spacer(1, 8))
        img = find_img(img_prefix)
        if img:
            story.append(Image(img, width=260, height=390))
        else:
            story.append(Paragraph("[Design Specification - See description below]", ParagraphStyle('P', parent=styles['Normal'], fontSize=11, alignment=TA_CENTER, textColor=HexColor("#9ca3af"))))
        story.append(Spacer(1, 12))
        for a in actions:
            story.append(Paragraph("* " + esc(a), desc_s))
        story.append(Spacer(1, 6))
        for s in security:
            story.append(Paragraph("[SECURE] " + esc(s), sec_s))
        story.append(PageBreak())

    # ===== SECTION A: ONBOARDING =====
    story.append(Paragraph("SECTION A: Onboarding &amp; Authentication", title_s))
    story.append(PageBreak())

    add_page("Screen 1: Splash Screen", "AyurEze branding with golden lotus on dark teal gradient. Loading bar at bottom.", "screen_01_splash",
        ["App initializes Firebase SDK", "Pings backend health endpoint", "Auto-login if cached JWT exists"],
        ["SSL Doomsday Monitor verified certificates at 1 AM", "PgBouncer handles connection surge"])

    add_page("Screen 2: Phone Login", "Phone number input with +91 prefix and Send OTP button.", "screen_02_phone_login",
        ["Patient enters 10-digit mobile number", "Taps Send OTP", "Firebase sends SMS"],
        ["Rate limiter: max 5 OTP attempts per IP per hour"])

    add_page("Screen 3: OTP Verification", "6-digit OTP input boxes with Verify button and resend timer.", "screen_03_otp_verify",
        ["Patient enters OTP", "Firebase verifies server-side", "JWT token generated and stored"],
        ["JWT token required for all subsequent API calls"])

    add_page("Screen 4: App Home Page", "Clean native dashboard with friendly AI avatar. Large [Start My Journey] button and quick-action cards for EHR Vault and Meditation.", "screen_04_onboarding",
        ["Patient lands on native Flutter Home Page", "Taps Start My Journey to enter Companion mode", "Accesses EHR or Yoga without chatting"],
        ["Journey isolation: each patient tracked independently", "Native routing to diverse app modules"])

    # ===== SECTION B: ASTRA COMPANION CHAT =====
    story.append(Paragraph("SECTION B: Astra Companion Chat", title_s))
    story.append(PageBreak())

    add_page("Screen 5: Chat - First Message", "WhatsApp-style chat with Astra's greeting: Namaste! How are you feeling?", "screen_05_chat_empty",
        ["Patient sees AI greeting", "Text input field and microphone button at bottom", "ListView.builder renders bubbles lazily"],
        ["Memory Leak Fix: ListView.builder destroys off-screen widgets", "Token Budget initialized in Redis (2000 tokens/hr)"])

    add_page("Screen 6: Active Conversation", "Multiple chat bubbles showing symptom discussion between patient and AI.", "screen_06_chat_active",
        ["Patient: I have bad headaches for 3 days", "AI asks clarifying questions (location, severity)", "Patient: Behind my eyes, 7/10"],
        ["XSS Sanitizer scrubs AI output", "Every response logged to Immutable Audit Ledger", "Token Budget tracks usage per hour"])

    add_page("Screen 7: Voice Recording", "Pulsing microphone with sound wave animation. Listening... indicator.", "screen_07_voice_recording",
        ["Patient holds mic button and speaks symptoms", "Speech-to-Text processes audio locally on device", "Raw audio NEVER sent to backend"],
        ["Voice data stays on device until patient confirms text"])

    add_page("Screen 8: Voice Confirmation Gate", "Modal popup: I heard 50mg. Is this correct? Confirm / Edit buttons.", "screen_08_voice_confirm",
        ["Patient reads transcribed text", "Notices error (15mg heard as 50mg)", "Edits text and taps Confirm"],
        ["Prevents dangerous dosage hallucinations from background noise", "Only confirmed text enters the AI pipeline"])

    # ===== SECTION C: SAFETY & EMERGENCY =====
    story.append(Paragraph("SECTION C: Safety &amp; Emergency", title_s))
    story.append(PageBreak())

    add_page("Screen 9: Cultural Clarification", "Orange-bordered card: You said chest is burning. Do you mean indigestion or cardiac pain? Two option chips.", "screen_09_cultural",
        ["AI detects ambiguous idiom", "Presents two options: Indigestion vs Sharp Chest Pain", "Patient selects to clarify"],
        ["Prevents false emergency escalation from regional idioms", "Cultural Clarification Protocol in system prompt"])

    add_page("Screen 10: SOS Emergency Lock", "Red warning banner, chat disabled, massive SOS CALL 112 button.", "astra_ui_safety_lock",
        ["Patient confirmed Sharp Chest Pain", "Chat input disappears permanently", "SOS button calls emergency services"],
        ["Journey locked to REFERRED status in Supabase", "Exact conversation etched into Immutable Audit Ledger", "Doctor notified via Firebase push"])

    add_page("Screen 11: Account Frozen", "Red ACCOUNT FROZEN banner. Chat keyboard hidden. Contact Support button.", "astra_ui_frozen",
        ["Hacker bot spammed 500 messages", "Keyboard and input field disappear", "Red warning with Contact Support link"],
        ["Denial of Wallet: Redis detected 2000+ tokens in 1 hour", "Account frozen until admin manually reviews"])

    # ===== SECTION D: ASTRA FILL (HEALTH INTAKE) =====
    story.append(Paragraph("SECTION D: Astra Fill - Health Intake", title_s))
    story.append(PageBreak())

    add_page("Screen 12: Astra Fill Form", "Health profile form with symptom tag chips, allergies input, medications list, blood type dropdown.", "screen_12_astra_fill",
        ["Patient fills symptom tags (Headache, Fatigue)", "Adds allergies and current medications", "AI extracts structured health data from voice or text"],
        ["Two-phase voice gate: /transcribe-voice then /confirm-transcript", "Structured data validated before storage"])

    add_page("Screen 13: Astra Fill Voice Intake", "Voice recording UI with real-time transcript appearing: I have been taking paracetamol for 2 days...", "astra_fill_voice",
        ["Patient speaks their health history", "Real-time transcript appears on screen", "Confirmation gate appears before AI processes"],
        ["Phase 1: STT only, no AI processing", "Phase 2: Patient confirms, then AI extraction runs"])

    # ===== SECTION E: ASTRA AUTOPILOT =====
    story.append(Paragraph("SECTION E: Astra Autopilot", title_s))
    story.append(PageBreak())

    add_page("Screen 14: Autopilot Consent", "Toggle switch: Enable Astra Autopilot. Description of automated follow-ups and refill reminders.", "astra_autopilot_consent",
        ["Patient reads Autopilot description", "Toggles ON to enable proactive care", "Consent stored in Supabase"],
        ["Autopilot only activates with explicit patient consent", "Patient can disable anytime"])

    add_page("Screen 15: Morning Wellness Check-In", "A push notification leads to a chat card: 'Good morning! At 9:00 AM, Astra asks how you are feeling today.'", "astra_morning_checkin",
        ["9:00 AM background worker triggers daily check-in", "Patient responds directly in the chat", "AI updates health profile if side effects are reported"],
        ["Daily engagement without user initiation", "Monitors treatment adherence passively"])

    add_page("Screen 16: Autopilot Refill Alert", "Purple gradient card in chat: Medicine running low (3 days left). Reorder? Yes/Not Now buttons.", "screen_11_autopilot",
        ["Autopilot detects medicine_end_date approaching", "Sends refill suggestion card in chat", "Patient taps Yes Reorder or Not Now"],
        ["Autopilot engine runs O-D-P loop: Observe, Decide, Prepare", "Refill triggered only with patient approval"])

    add_page("Screen 17: Autopilot Follow-Up", "Card in chat: Its been 15 days since your consultation. Time for a follow-up? Book Now button.", "astra_autopilot_followup",
        ["Autopilot detects follow-up window is open", "Suggests booking with previous doctor", "Patient taps Book Now or Dismiss"],
        ["Follow-up window: 15 days after last consultation", "Care gap detection prevents patients from falling off"])

    # ===== SECTION F: MEDITATION & YOGA =====
    story.append(Paragraph("SECTION F: Meditation &amp; Yoga", title_s))
    story.append(PageBreak())

    add_page("Screen 18: Meditation Player", "Dark blue/purple gradient. Glowing breathing circle. Breathe In... 4 seconds. Timer: 3:42.", "screen_10_meditation",
        ["Patient selects focus: Stress, Sleep, Anxiety, Energy", "Guided meditation script plays with breathing timer", "Dosha-specific guidance (Vata/Pitta/Kapha)"],
        ["4-7-8, Box Breathing, Nadi Shodhana, Bhramari techniques", "AI-generated personalized scripts via Astra Brain"])

    add_page("Screen 19: Yoga Plan", "Clean card layout showing yoga poses with illustrations: Cat-Cow, Childs Pose, Downward Dog. Duration per pose.", "astra_yoga_plan",
        ["AI generates personalized yoga plan based on focus (Back Pain, Flexibility)", "Step-by-step pose instructions", "Beginner/Intermediate/Advanced levels"],
        ["Plans include safety warnings for chronic conditions", "Local fallback if AI is unavailable"])

    # ===== SECTION G: DOCTOR HANDOFF & PRESCRIPTION =====
    story.append(Paragraph("SECTION G: Doctor Handoff &amp; Prescription", title_s))
    story.append(PageBreak())

    add_page("Screen 20: Doctor Handoff", "Status card: Connecting you with Dr. Sharma. Green progress indicator. Doctor avatar.", "astra_doctor_handoff",
        ["AI completes symptom analysis", "Status card appears in chat with doctor name", "Doctor reviews full audit trail on admin panel"],
        ["Zero-Trust: AI role ends here. Only Doctor JWT can trigger orders", "Doctor modifications also logged to Audit Ledger"])

    add_page("Screen 21: Smart Cart", "Product carousel with Ashwagandha bottle, price, and Add to Cart button inside chat.", "astra_ui_smart_cart",
        ["Doctor prescribed medicine via admin panel", "Product card appears in patient chat", "Patient taps Add to Cart"],
        ["Prompt Injection proof: AI has zero access to Shopify endpoints", "50MB Nginx limit prevents webhook truncation"])

    add_page("Screen 22: Prescription PDF", "Full-screen PDF viewer with QR code, doctor signature, medicine list.", "astra_ui_prescription_scanner",
        ["PDF generated by Celery background worker (not main thread)", "QR code links to /verify endpoint", "Patient downloads or shares PDF"],
        ["OOM Prevention: Celery worker isolated from FastAPI", "QR cryptographic hash detects Photoshop tampering"])

    # ===== SECTION H: CHECKOUT & FOLLOW-UP =====
    story.append(Paragraph("SECTION H: Checkout &amp; Follow-Up", title_s))
    story.append(PageBreak())

    add_page("Screen 23: Payment Checkout", "Razorpay gateway with UPI/Card options and Pay Now button.", "astra_razorpay",
        ["Patient taps Proceed to Pay", "Razorpay SDK opens natively", "UPI / Card / Net Banking options"],
        ["Webhook payload passes Nginx 50MB limit", "PgBouncer handles payment spike connections"])

    add_page("Screen 24: Order Confirmed", "Green checkmark animation. Order Confirmed! Order details and Back to Chat button.", "astra_ui_payment_success",
        ["Green success animation plays", "Order marked PAID in Shopify", "Medicine reminders auto-created"],
        ["Celery handles post-payment PDF receipts", "Reminder schedules stored in Supabase"])

    add_page("Screen 25: Medicine Reminder", "Push notification on lock screen: Time to take your Ashwagandha! (Morning dose)", "astra_reminder",
        ["Phone buzzes at 8 AM and 8 PM", "Notification shows medicine name and dose", "Tap opens app to confirm taken"],
        ["Background scheduler fires at 8 AM and 8 PM daily", "Firebase Cloud Messaging delivers push"])

    add_page("Screen 26: WhatsApp Autopilot", "WhatsApp notification: Good morning! How are you feeling after your Ashwagandha?", "astra_ui_whatsapp",
        ["AI drafts personalized check-in message", "Sent via WhatsApp Business API at 9 AM", "Patient replies directly on WhatsApp"],
        ["Same AI brain powers both Flutter and WhatsApp", "WhatsApp responses also logged to Audit Ledger"])

    # ===== APPENDIX =====
    story.append(Paragraph("Appendix: Complete Feature &amp; Security Matrix", title_s))
    story.append(Spacer(1, 20))

    data = [["Module", "Feature", "Security Layer"]]
    rows = [
        ("Astra Companion", "AI Chat, Voice, Multilingual", "XSS Sanitizer, Audit Log, Token Budget"),
        ("Astra Fill", "Health Intake via Voice/Text", "Two-Phase Voice Gate, Confirmation Card"),
        ("Astra Autopilot", "Refill Alerts, Follow-Ups, Care Gaps", "Patient Consent Required, O-D-P Loop"),
        ("Meditation", "Guided Scripts, Breathing, Yoga", "AI + Local Fallback, Dosha-Specific"),
        ("Smart Cart", "Shopify Draft Orders in Chat", "Doctor JWT Only, Prompt Injection Proof"),
        ("Prescription PDF", "QR-Signed PDF Generation", "Celery Worker, Cryptographic Hash"),
        ("Payments", "Razorpay In-App Checkout", "50MB Nginx Limit, PgBouncer"),
        ("WhatsApp", "Omnichannel AI Chat", "Same Security Pipeline as App"),
        ("Infrastructure", "SSL, DB, Background Jobs", "Doomsday Monitor, PgBouncer, Redis"),
    ]
    for r in rows: data.append(list(r))

    t = Table(data, colWidths=[1.3*inch, 2.2*inch, 3.3*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), HexColor("#0d4f4f")),
        ('TEXTCOLOR', (0,0), (-1,0), white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, HexColor("#d1d5db")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [white, HexColor("#f3f4f6")]),
    ]))
    story.append(t)

    doc.build(story)
    print("Complete App Flow PDF Generated Successfully!")

if __name__ == "__main__":
    generate_pdf()
