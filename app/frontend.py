"""
Simple frontend routes for Firebase login testing
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
import os

frontend_router = APIRouter(tags=["frontend"])

@frontend_router.get("/login-page", response_class=HTMLResponse)
async def login_page():
    """Simple login page for testing Firebase integration"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Astra - Ayurvedic Wellness Assistant</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .container {
                background: white;
                padding: 2rem;
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                text-align: center;
                max-width: 400px;
                width: 90%;
            }
            h1 {
                color: #333;
                margin-bottom: 0.5rem;
                font-size: 2rem;
            }
            .subtitle {
                color: #666;
                margin-bottom: 2rem;
                font-size: 1.1rem;
            }
            .info-box {
                background: #f0f7ff;
                padding: 1.5rem;
                border-radius: 10px;
                margin-top: 1rem;
                border-left: 4px solid #4285f4;
            }
            .info-box h3 {
                margin-top: 0;
                color: #333;
            }
            .info-box p {
                color: #666;
                line-height: 1.6;
            }
            .features {
                margin-top: 2rem;
                text-align: left;
            }
            .feature {
                margin: 0.5rem 0;
                color: #555;
            }
            .namaste {
                font-size: 1.2rem;
                color: #8B4513;
                margin-bottom: 1rem;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="namaste">🕉️ Namaste 🕉️</div>
            <h1>Astra</h1>
            <p class="subtitle">Your Ayurvedic Wellness Assistant</p>
            
            <div class="info-box">
                <h3>🔐 Firebase Authentication</h3>
                <p>This application now uses Firebase Authentication. Please use the mobile app or integrate Firebase Auth in your frontend application.</p>
                <p><strong>For API access:</strong> Include your Firebase ID token in the Authorization header as a Bearer token.</p>
            </div>
            
            <div class="features">
                <h3>Features:</h3>
                <div class="feature">✨ Multilingual support (20+ languages)</div>
                <div class="feature">🌿 Personalized Ayurvedic guidance</div>
                <div class="feature">💬 Persistent chat history</div>
                <div class="feature">🧘‍♀️ Holistic wellness recommendations</div>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@frontend_router.get("/callback")
async def auth_callback(request: Request):
    """Legacy callback endpoint - now redirects to Firebase info"""
    return HTMLResponse("""
    <html>
    <body style="font-family: Arial, sans-serif; padding: 2rem; text-align: center;">
        <h1>Authentication Method Changed</h1>
        <p>This application now uses Firebase Authentication instead of Auth0.</p>
        <p>Please use the mobile app or integrate Firebase Auth in your frontend.</p>
        <a href="/docs" style="color: #4285f4; text-decoration: none;">Go to API Documentation</a>
    </body>
    </html>
    """)
