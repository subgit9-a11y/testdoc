import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

def generate_grid_pdf():
    buffer_path = "prescription_debug_grid.pdf"
    c = canvas.Canvas(buffer_path, pagesize=A4)
    width, height = A4
    
    # 1. Draw Background
    base_path = os.path.join(os.path.dirname(__file__), "assets", "base_prescription.png")
    if os.path.exists(base_path):
        c.drawImage(base_path, 0, 0, width=width, height=height)
    
    # 2. Draw Coordinate Grid
    c.setStrokeColorRGB(1, 0, 0) # Red
    c.setLineWidth(0.5)
    
    # Vertical lines every 50 points
    for x in range(0, int(width), 50):
        c.line(x, 0, x, height)
        c.setFont("Helvetica", 8)
        c.drawString(x + 2, 10, str(x))
        
    # Horizontal lines every 50 points
    for y in range(0, int(height), 50):
        c.line(0, y, width, y)
        c.setFont("Helvetica", 8)
        c.drawString(10, y + 2, str(y))
        
    # Mark specific areas
    c.setStrokeColorRGB(0, 0, 1) # Blue
    c.rect(30, height - 165, 250, 20) # Name area
    
    c.save()
    print(f"Grid PDF generated at {buffer_path}")

if __name__ == "__main__":
    generate_grid_pdf()
