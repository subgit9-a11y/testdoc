import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.colors import HexColor

def generate_pdf():
    pdf_filename = "c:\\Users\\SUBHASH\\Desktop\\astrafinalneed\\astra\\Astra_Secure_UX_Flow.pdf"
    doc = SimpleDocTemplate(pdf_filename, pagesize=letter,
                            rightMargin=50, leftMargin=50,
                            topMargin=50, bottomMargin=50)

    styles = getSampleStyleSheet()
    
    # Custom Styles
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=HexColor("#1e3a8a")
    )
    
    screen_title_style = ParagraphStyle(
        'ScreenTitle',
        parent=styles['Heading2'],
        fontSize=18,
        spaceAfter=15,
        textColor=HexColor("#047857")
    )
    
    ux_action_style = ParagraphStyle(
        'UXAction',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=10,
        bulletIndent=10,
        leftIndent=20
    )
    
    security_style = ParagraphStyle(
        'SecurityNote',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=15,
        leftIndent=20,
        textColor=HexColor("#b91c1c"),
        fontName="Helvetica-Oblique"
    )

    story = []

    # ================= TITLE PAGE =================
    story.append(Paragraph("Astra AI Wellness Companion", title_style))
    story.append(Paragraph("End-to-End Secure UI/UX Flow Architecture", styles['Title']))
    story.append(Spacer(1, 50))
    story.append(Paragraph("This document outlines the complete patient journey from the opening screen to checkout, detailing how the newly implemented security and anti-hijacking layers integrate into the user interface.", styles['Normal']))
    story.append(PageBreak())

    # ================= SCREEN 1 =================
    story.append(Paragraph("Screen 1: Splash & Secure Authentication", screen_title_style))
    story.append(Paragraph("<b>Visuals:</b> AyurEze branding fades in. A loading spinner indicates server connection.", styles['Normal']))
    story.append(Spacer(1, 10))
    story.append(Paragraph("• <b>User Action:</b> Opens the app.", ux_action_style))
    story.append(Paragraph("• <b>System Action:</b> The app verifies the Firebase JWT token.", ux_action_style))
    story.append(Paragraph("🔒 <i>Security Layer: If the SSL certificate is within 14 days of expiration, the background Doomsday Monitor has already alerted DevOps, ensuring this screen never hangs.</i>", security_style))
    story.append(Spacer(1, 20))

    # ================= SCREEN 2 =================
    story.append(Paragraph("Screen 2: The Main Chat Interface", screen_title_style))
    story.append(Paragraph("<b>Visuals:</b> A clean, continuous chat feed. A text input box and a microphone button sit at the bottom.", styles['Normal']))
    story.append(Spacer(1, 10))
    story.append(Paragraph("• <b>User Action:</b> Types 'What herbs help with digestion?' and hits send.", ux_action_style))
    story.append(Paragraph("• <b>System Action:</b> The Flutter app uses ListView.builder to render the chat bubbles without crashing the phone's memory (Fix #29).", ux_action_style))
    story.append(Paragraph("🔒 <i>Security Layer (Token Budget): Before the AI replies, Redis checks if the user exceeded 2,000 tokens/hr. If safe, the AI generates a response.</i>", security_style))
    story.append(Paragraph("🔒 <i>Security Layer (XSS Sanitizer): The AI's response is scrubbed of malicious HTML/JS before appearing on the screen.</i>", security_style))
    story.append(Spacer(1, 20))

    # ================= SCREEN 3 =================
    story.append(Paragraph("Screen 3: Voice Confirmation Gate", screen_title_style))
    story.append(Paragraph("<b>Visuals:</b> A modal popup card temporarily blocks the chat interface.", styles['Normal']))
    story.append(Spacer(1, 10))
    story.append(Paragraph("• <b>User Action:</b> Taps the microphone and says 'I took fifty milligrams.'", ux_action_style))
    story.append(Paragraph("• <b>System Action:</b> The Flutter app pauses the flow and presents the text to the user.", ux_action_style))
    story.append(Paragraph("• <b>UI Element:</b> 'I heard: I took 50 milligrams. Is this correct? [Confirm] / [Edit]'", ux_action_style))
    story.append(Paragraph("🔒 <i>Security Layer (Voice Triage): Prevents the AI from acting on dangerous transcription errors caused by background noise (Fix #21).</i>", security_style))
    story.append(PageBreak())

    # ================= SCREEN 4 =================
    story.append(Paragraph("Screen 4: Abuse Prevention (Account Frozen)", screen_title_style))
    story.append(Paragraph("<b>Visuals:</b> The standard chat keyboard disappears. The screen flashes a red warning banner.", styles['Normal']))
    story.append(Spacer(1, 10))
    story.append(Paragraph("• <b>User Action:</b> A hacker writes a bot to spam the chat box rapidly.", ux_action_style))
    story.append(Paragraph("• <b>System Action:</b> The backend returns metadata={'account_frozen': True}.", ux_action_style))
    story.append(Paragraph("• <b>UI Element:</b> '⚠️ ACCOUNT FROZEN FOR REVIEW. Unusually high activity detected.' The chat input is permanently disabled.", ux_action_style))
    story.append(Paragraph("🔒 <i>Security Layer (Denial of Wallet): Protects company API credits from being drained (Fix #31).</i>", security_style))
    story.append(Spacer(1, 20))

    # ================= SCREEN 5 =================
    story.append(Paragraph("Screen 5: Safety Lock & SOS Escalation", screen_title_style))
    story.append(Paragraph("<b>Visuals:</b> The AI stops responding. A prominent red 'SOS Emergency' button overrides the chat box.", styles['Normal']))
    story.append(Spacer(1, 10))
    story.append(Paragraph("• <b>User Action:</b> Patient types 'My chest is crushing me.'", ux_action_style))
    story.append(Paragraph("• <b>System Action:</b> The AI checks the Cultural Protocol. If verified as a real emergency, it locks the chat.", ux_action_style))
    story.append(Paragraph("• <b>UI Element:</b> '🚨 CHAT LOCKED. Critical emergency detected. Tap SOS to call 112.'", ux_action_style))
    story.append(Paragraph("🔒 <i>Security Layer (Medical Liability): The exact prompt and AI lock response are permanently etched into the Immutable Audit Ledger in Supabase (Fix #12).</i>", security_style))
    story.append(Spacer(1, 20))

    # ================= SCREEN 6 =================
    story.append(Paragraph("Screen 6: Smart Cart & Doctor Handoff", screen_title_style))
    story.append(Paragraph("<b>Visuals:</b> An interactive product carousel appears inside the chat feed containing prescribed medicines.", styles['Normal']))
    story.append(Spacer(1, 10))
    story.append(Paragraph("• <b>System Action:</b> The Doctor clicks 'Generate Prescription' on the admin panel.", ux_action_style))
    story.append(Paragraph("• <b>System Action:</b> A massive Shopify JSON payload is sent without hitting the 1MB Nginx limit (Fix #42).", ux_action_style))
    story.append(Paragraph("• <b>UI Element:</b> Patient sees 'Dr. AyurEze has prescribed: Ashwagandha. [Add to Cart]'", ux_action_style))
    story.append(Paragraph("🔒 <i>Security Layer (Prompt Injection): The AI itself cannot generate this cart. It requires a Doctor's authorized JWT token.</i>", security_style))
    story.append(PageBreak())

    # ================= SCREEN 7 =================
    story.append(Paragraph("Screen 7: Prescription PDF & Forgery Scanner", screen_title_style))
    story.append(Paragraph("<b>Visuals:</b> A built-in PDF viewer showing the official prescription document with an embedded QR code.", styles['Normal']))
    story.append(Spacer(1, 10))
    story.append(Paragraph("• <b>System Action:</b> The background Celery Worker successfully generated the PDF without crashing the main server (Fix #39).", ux_action_style))
    story.append(Paragraph("• <b>User Action:</b> The patient downloads the PDF and takes it to a pharmacy.", ux_action_style))
    story.append(Paragraph("• <b>UI Element (Pharmacy Portal):</b> A 'Scan Prescription QR' button opens the camera.", ux_action_style))
    story.append(Paragraph("🔒 <i>Security Layer (Non-Repudiation): Scanning the QR hits the /verify endpoint to cryptographically prove the patient didn't photoshop the medicine quantity (Fix #28).</i>", security_style))
    story.append(Spacer(1, 20))
    
    # ================= SCREEN 8 =================
    story.append(Paragraph("Screen 8: Checkout & Background Autopilot", screen_title_style))
    story.append(Paragraph("<b>Visuals:</b> Standard Razorpay checkout UI, followed by a 'Success' checkmark.", styles['Normal']))
    story.append(Spacer(1, 10))
    story.append(Paragraph("• <b>User Action:</b> Patient pays for the medicine.", ux_action_style))
    story.append(Paragraph("• <b>System Action:</b> The order clears in Shopify.", ux_action_style))
    story.append(Paragraph("• <b>System Action:</b> The next morning, the background Cron job wakes up and sends a WhatsApp message: 'Don't forget to take your Ashwagandha!'", ux_action_style))
    story.append(Spacer(1, 30))
    
    story.append(Paragraph("<b>Document Generated Successfully by Astra AI Infrastructure</b>", styles['Normal']))

    doc.build(story)
    print("PDF Generated successfully.")

if __name__ == "__main__":
    generate_pdf()
