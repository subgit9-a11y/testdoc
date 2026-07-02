import os
import sys
from a2wsgi import ASGIMiddleware

# Add your app to the system path
sys.path.insert(0, os.path.dirname(__file__))

# Import your FastAPI app from main.py
try:
    from main import app as fastapi_app
except ImportError as e:
    raise ImportError(f"Could not import main FastAPI app. Make sure this file is in the same directory as main.py. Error: {e}")

# Convert the ASGI FastAPI app into a WSGI app so cPanel can run it
application = ASGIMiddleware(fastapi_app)
