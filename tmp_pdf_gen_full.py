from fpdf import FPDF
import os

class PDF(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 16)
        self.cell(0, 15, 'AyurEze AI Wellness Companion - COMPLETE UI/UX FLOW', 0, 1, 'C')
        self.line(10, 25, 200, 25)
        self.ln(5)
        
    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def add_step(pdf, title, desc, img_path):
    pdf.add_page()
    pdf.set_font('helvetica', 'B', 14)
    pdf.cell(0, 8, title, 0, 1)
    pdf.set_font('helvetica', '', 11)
    pdf.multi_cell(0, 6, desc)
    pdf.ln(5)
    if os.path.exists(img_path):
        pdf.image(img_path, x=45, w=120)
    else:
        pdf.cell(0, 10, 'Image not found', 0, 1)

pdf = PDF()

# Step 1: Splash
add_step(pdf, 'Step 1: App Splash Screen', 
         'The user opens the app and is greeted by the premium AyurEze AI Wellness Companion splash screen, establishing a trustworthy and aesthetic healthcare vibe.', 
         r'C:\Users\SUBHASH\.gemini\antigravity\brain\cdb5c957-aedd-4788-8c78-707bae641a2a\ayureze_ui_splash_1779161031748.png')

# Step 2: Home
add_step(pdf, 'Step 2: Home Dashboard', 
         'The user lands on their personalized dashboard. The Astra AI chat input is immediately accessible for them to report any health issues, alongside upcoming goals.', 
         r'C:\Users\SUBHASH\.gemini\antigravity\brain\cdb5c957-aedd-4788-8c78-707bae641a2a\ayureze_ui_home_1779161046778.png')

# Step 3: Intake
add_step(pdf, 'Step 3: Astra Fill (Patient Intake)', 
         'The user types their symptoms into the chat. The AI extracts the clinical context using NLP, summarizes it in a beautiful card, and prompts for a doctor connection.', 
         r'C:\Users\SUBHASH\.gemini\antigravity\brain\cdb5c957-aedd-4788-8c78-707bae641a2a\ayureze_ui_intake_1779160078105.png')

# Step 4: Teleconsultation
add_step(pdf, 'Step 4: Doctor Teleconsultation', 
         'The patient is seamlessly routed to a teleconsultation video call with an Ayurvedic Doctor. The doctor reviews the AI-extracted symptoms on their end.', 
         r'C:\Users\SUBHASH\.gemini\antigravity\brain\cdb5c957-aedd-4788-8c78-707bae641a2a\ayureze_ui_teleconsult_1779160097334.png')

# Step 5: Prescription & Cart
add_step(pdf, 'Step 5: Prescription & Shopify Auto Cart', 
         'After the consultation, the doctor generates a prescription. The AI automatically maps this to Shopify inventory and sends a Smart Cart for 1-click checkout directly in the chat.', 
         r'C:\Users\SUBHASH\.gemini\antigravity\brain\cdb5c957-aedd-4788-8c78-707bae641a2a\ayureze_ai_wellness_companion_ui_1779159673658.png')

# Step 6: Dispatch
add_step(pdf, 'Step 6: Order Dispatch Tracking', 
         'Once purchased, the app displays a Smart Dispatch tracker. The patient can track their herbal medicines in real-time until they arrive at their doorstep.', 
         r'C:\Users\SUBHASH\.gemini\antigravity\brain\cdb5c957-aedd-4788-8c78-707bae641a2a\ayureze_ui_tracking_1779161062888.png')

# Step 7: Companion
add_step(pdf, 'Step 7: AI Wellness Companion & Reminders', 
         'With the medicine received, the AI acts as a daily companion. It tracks medication adherence (check-offs) and asks daily follow-up questions to monitor recovery.', 
         r'C:\Users\SUBHASH\.gemini\antigravity\brain\cdb5c957-aedd-4788-8c78-707bae641a2a\ayureze_ui_companion_1779160117563.png')

# Step 8: Resolved
add_step(pdf, 'Step 8: Case Resolved & App Close', 
         'Once the patient reports feeling better, the Astra Autopilot marks the case as resolved. The journey concludes with a beautiful wellness confirmation screen before closing.', 
         r'C:\Users\SUBHASH\.gemini\antigravity\brain\cdb5c957-aedd-4788-8c78-707bae641a2a\ayureze_ui_resolved_1779161082097.png')


pdf_output_path = r'C:\Users\SUBHASH\Desktop\astrafinalneed\AyurEze_COMPLETE_End_to_End_Flow.pdf'
pdf.output(pdf_output_path)
print(f"Created {pdf_output_path}")
