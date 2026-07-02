from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib import colors

def create_pdf(filename):
    doc = SimpleDocTemplate(filename, pagesize=letter,
                            rightMargin=50, leftMargin=50,
                            topMargin=50, bottomMargin=50)
    
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='CustomTitle', parent=styles['Heading1'], fontSize=18, spaceAfter=20, textColor=colors.darkblue))
    styles.add(ParagraphStyle(name='CustomHeading', parent=styles['Heading2'], fontSize=14, spaceAfter=10, textColor=colors.black))
    styles.add(ParagraphStyle(name='CustomBody', parent=styles['Normal'], fontSize=11, spaceAfter=8, leading=14))
    
    Story = []
    
    Story.append(Paragraph("Astra AI Wellness Companion", styles['CustomTitle']))
    Story.append(Paragraph("Patient App Integration Guide & Feature Specifications", styles['CustomHeading']))
    Story.append(Spacer(1, 12))
    
    Story.append(Paragraph("1. System Architecture Overview", styles['CustomHeading']))
    Story.append(Paragraph("The Super App approach integrates the new Astra AI directly into the existing AyurEze app via a bottom/top TabBar. Patients can seamlessly switch between the Traditional Menu (Food/Instamart style) and the Astra AI Companion.", styles['CustomBody']))
    Story.append(Spacer(1, 12))
    
    Story.append(Paragraph("2. Key Features to Implement", styles['CustomHeading']))
    Story.append(Paragraph("<b>A. Conversational Intake:</b> Replace manual symptom selection forms with a natural language chat interface powered by the Astra LLM.", styles['CustomBody']))
    Story.append(Paragraph("<b>B. Interlinked Identity & Wallet:</b> Ensure the Patient App sends the existing user_id (e.g., 35) to the Astra backend. Astra automatically syncs with the legacy MySQL database for seamless continuity of medical and financial records.", styles['CustomBody']))
    Story.append(Paragraph("<b>C. Field-Level Encryption (DISHA Compliance):</b> The Astra backend handles all PII encryption automatically. The Patient App just needs to send raw data over HTTPS; Astra stores it symmetrically encrypted.", styles['CustomBody']))
    Story.append(Paragraph("<b>D. Automated Cart & Shopify Sync:</b> When Astra AI prescribes medications, the backend triggers Shopify Draft Orders. The Patient App fetches these drafts via the standard Razorpay checkout flow.", styles['CustomBody']))
    Story.append(Spacer(1, 12))
    
    Story.append(Paragraph("3. Integration Flow (Step-by-Step)", styles['CustomHeading']))
    Story.append(Paragraph("<b>Phase 1 (UI Integration):</b> Create a Flutter TabBar holding two views: the existing 'Home' view and the new 'Astra Chat' view.", styles['CustomBody']))
    Story.append(Paragraph("<b>Phase 2 (Identity Handoff):</b> In the Astra Chat view, inject a secure JWT or the legacy user_id so Astra recognizes the logged-in patient.", styles['CustomBody']))
    Story.append(Paragraph("<b>Phase 3 (Chat Loop):</b> Implement a WebSocket or HTTP Polling loop to send user messages to '/api/chat' and render Astra's streaming text responses.", styles['CustomBody']))
    Story.append(Paragraph("<b>Phase 4 (Action Cards):</b> Teach the Patient App UI to parse 'Action Tokens' from Astra. E.g., if Astra outputs [CHECKOUT:CART], the Flutter UI pops up the native Razorpay payment sheet.", styles['CustomBody']))
    
    doc.build(Story)

create_pdf("Astra_Patient_App_Integration.pdf")
print("PDF Generated Successfully!")
