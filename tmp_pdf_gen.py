from fpdf import FPDF
import os

class PDF(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 16)
        self.cell(0, 15, 'AyurEze AI Wellness Companion - UI/UX Flow', 0, 1, 'C')
        self.line(10, 25, 200, 25)
        self.ln(10)
        
    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

pdf = PDF()

# Step 1
pdf.add_page()
pdf.set_font('helvetica', 'B', 14)
pdf.cell(0, 10, 'Step 1: Astra Fill (Patient Intake)', 0, 1)
pdf.set_font('helvetica', '', 11)
pdf.multi_cell(0, 8, 'The user opens the app and enters their symptoms. The AI extracts the clinical context using NLP and prompts for a doctor connection.')
pdf.ln(5)
pdf.image(r'C:\Users\SUBHASH\.gemini\antigravity\brain\cdb5c957-aedd-4788-8c78-707bae641a2a\ayureze_ui_intake_1779160078105.png', x=45, w=120)

# Step 2
pdf.add_page()
pdf.set_font('helvetica', 'B', 14)
pdf.cell(0, 10, 'Step 2: Doctor Teleconsultation', 0, 1)
pdf.set_font('helvetica', '', 11)
pdf.multi_cell(0, 8, 'The patient is seamlessly routed to a teleconsultation video call with an Ayurvedic Doctor. The doctor reviews the AI-extracted symptoms on their end.')
pdf.ln(5)
pdf.image(r'C:\Users\SUBHASH\.gemini\antigravity\brain\cdb5c957-aedd-4788-8c78-707bae641a2a\ayureze_ui_teleconsult_1779160097334.png', x=45, w=120)

# Step 3
pdf.add_page()
pdf.set_font('helvetica', 'B', 14)
pdf.cell(0, 10, 'Step 3: Prescription & Shopify Auto Cart', 0, 1)
pdf.set_font('helvetica', '', 11)
pdf.multi_cell(0, 8, 'After the consultation, the doctor generates a prescription. The AI automatically maps this to Shopify inventory and sends a Smart Cart for 1-click checkout in the chat.')
pdf.ln(5)
pdf.image(r'C:\Users\SUBHASH\.gemini\antigravity\brain\cdb5c957-aedd-4788-8c78-707bae641a2a\ayureze_ai_wellness_companion_ui_1779159673658.png', x=45, w=120)

# Step 4
pdf.add_page()
pdf.set_font('helvetica', 'B', 14)
pdf.cell(0, 10, 'Step 4: AI Wellness Companion & Follow-up', 0, 1)
pdf.set_font('helvetica', '', 11)
pdf.multi_cell(0, 8, 'Once medicine is dispatched, the AI acts as a daily companion, tracking medication adherence and checking on the patient until the case is resolved.')
pdf.ln(5)
pdf.image(r'C:\Users\SUBHASH\.gemini\antigravity\brain\cdb5c957-aedd-4788-8c78-707bae641a2a\ayureze_ui_companion_1779160117563.png', x=45, w=120)

pdf_output_path = r'C:\Users\SUBHASH\Desktop\astrafinalneed\AyurEze_Patient_App_UI_Flow.pdf'
pdf.output(pdf_output_path)
print(f"Created {pdf_output_path}")
