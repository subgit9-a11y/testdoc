from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib import colors

def create_pdf(filename):
    doc = SimpleDocTemplate(filename, pagesize=letter,
                            rightMargin=40, leftMargin=40,
                            topMargin=40, bottomMargin=40)
    
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='CustomTitle', parent=styles['Heading1'], fontSize=18, spaceAfter=15, textColor=colors.darkblue))
    styles.add(ParagraphStyle(name='CustomHeading', parent=styles['Heading2'], fontSize=14, spaceAfter=10, textColor=colors.black))
    styles.add(ParagraphStyle(name='CustomBody', parent=styles['Normal'], fontSize=11, spaceAfter=8, leading=14))
    styles.add(ParagraphStyle(name='CustomSubHeading', parent=styles['Heading3'], fontSize=12, spaceAfter=6, textColor=colors.darkred))
    
    Story = []
    
    Story.append(Paragraph("AyurEze Patient App - Complete User Journey", styles['CustomTitle']))
    Story.append(Paragraph("End-to-End Flow: App Open to App Close (Astra AI Integration)", styles['CustomBody']))
    Story.append(Spacer(1, 15))
    
    # Step 1
    Story.append(Paragraph("1. App Initialization & Authentication", styles['CustomHeading']))
    Story.append(Paragraph("<b>A. Splash Screen:</b> App opens, verifies device security and internet connection.", styles['CustomBody']))
    Story.append(Paragraph("<b>B. Login / Auto-Login:</b> User logs in via OTP/Biometrics. Flutter securely stores the Auth Token.", styles['CustomBody']))
    Story.append(Paragraph("<b>C. Identity Sync:</b> The app fetches the user's Profile ID from the legacy MySQL database and quietly authenticates with the Astra Supabase ecosystem.", styles['CustomBody']))
    Story.append(Spacer(1, 10))
    
    # Step 2
    Story.append(Paragraph("2. The Super App Dashboard", styles['CustomHeading']))
    Story.append(Paragraph("<b>A. Landing Page:</b> User lands on the traditional Home Screen (showing categories like Food, Therapy, Instamart).", styles['CustomBody']))
    Story.append(Paragraph("<b>B. The UI Toggle:</b> A prominent floating button or TabBar (similar to Swiggy) allows the user to switch instantly from 'Traditional Shopping' to 'Astra AI Companion'.", styles['CustomBody']))
    Story.append(Spacer(1, 10))
    
    # Step 3
    Story.append(Paragraph("3. The Astra AI Chat Flow (The Core Journey)", styles['CustomHeading']))
    Story.append(Paragraph("<b>A. Initialization:</b> User switches to Astra AI. Astra greets the user by name, referencing past health history if available.", styles['CustomBody']))
    Story.append(Paragraph("<b>B. Symptom Capture:</b> User types or uses voice-to-text to describe their symptoms (e.g., 'I have a severe headache and fever').", styles['CustomBody']))
    Story.append(Paragraph("<b>C. AI Triage:</b> Astra securely processes the input. Under the hood, symptoms are symmetrically encrypted (DISHA compliance) and saved to the decentralized vault.", styles['CustomBody']))
    Story.append(Paragraph("<b>D. AI Resolution:</b> Astra provides a wellness plan, lifestyle advice, and recommends specific AyurEze herbal medicines.", styles['CustomBody']))
    Story.append(Spacer(1, 10))
    
    # Step 4
    Story.append(Paragraph("4. Prescription & E-Commerce Flow", styles['CustomHeading']))
    Story.append(Paragraph("<b>A. Automated Cart:</b> The Astra backend automatically communicates with the Shopify API to create a Draft Order containing the prescribed medicines.", styles['CustomBody']))
    Story.append(Paragraph("<b>B. Rich UI Card:</b> Astra sends a 'Smart Card' in the chat UI containing the cart summary and a 'Pay Now' button.", styles['CustomBody']))
    Story.append(Paragraph("<b>C. Native Checkout:</b> User taps 'Pay Now'. The Flutter app triggers the native Razorpay SDK overlay.", styles['CustomBody']))
    Story.append(Paragraph("<b>D. Payment Success:</b> Once Razorpay succeeds, Flutter notifies Astra. Astra marks the Shopify order as 'Paid' and updates the legacy MySQL wallet interlink.", styles['CustomBody']))
    Story.append(Spacer(1, 10))
    
    # Step 5
    Story.append(Paragraph("5. Post-Consultation & App Close", styles['CustomHeading']))
    Story.append(Paragraph("<b>A. Order Tracking:</b> Astra provides a tracking link for the newly purchased medicines.", styles['CustomBody']))
    Story.append(Paragraph("<b>B. Secure Audit Log:</b> The backend finalizes the immutable audit log for the session, ensuring medical liability compliance.", styles['CustomBody']))
    Story.append(Paragraph("<b>C. App Close:</b> The user closes the app. All sensitive session data is cleared from the device's volatile memory, remaining safely encrypted in the Astra ecosystem.", styles['CustomBody']))
    
    doc.build(Story)

create_pdf("AyurEze_End_To_End_App_Flow.pdf")
print("PDF Generated Successfully!")
