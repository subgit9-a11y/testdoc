import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from app.enhanced_inference import AstraModelInference
from app.astra.pipeline import AstraPipeline
from app.astra.routes import v1_router as astra_v1_router
from app.doctors.doctor_auth_routes import doctor_auth_router
from app.astra.router import router as astra_router
from app.astra.brain_routes import router as brain_router
from app.admin.routes import router as admin_api_router
from app.admin.dashboard import router as dashboard_router
from app.auth_middleware import rate_limit_check
from app.sync_service import sync_service
from app.inventory_sync_service import inventory_sync_service
import logging
from logging.handlers import TimedRotatingFileHandler
import os
import asyncio # Added for asyncio.create_task

# Security & Centralized Logging: Set up daily rotating logs
os.makedirs("logs", exist_ok=True)
log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Daily rotating file handler (midnight) keeping 30 days of logs
file_handler = TimedRotatingFileHandler("logs/astra_backend.log", when="midnight", interval=1, backupCount=30)
file_handler.setFormatter(log_format)

# Console handler for Docker logs
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_format)

# Configure the root logger
logging.basicConfig(level=logging.INFO, handlers=[file_handler, console_handler])
logger = logging.getLogger("AstraSecurityFortress")

app = FastAPI(
    title="Astra AI Unified Engine",
    version="4.5.1",
    docs_url="/docs", 
    redoc_url="/redoc"
)

# 1. CORS Protection
origins = [
    "https://ayureze.in",
    "https://app.ayureze.in",
    "http://localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# 2. Security Headers Middleware
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        # Adjusted CSP to allow Swagger UI scripts while maintaining hardening
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; img-src 'self' data:; style-src 'self' 'unsafe-inline';"
        return response

app.add_middleware(SecurityHeadersMiddleware)

# 3. Payload Truncation Fix Middleware (Issue #42)
from app.payload_middleware import MaxBodySizeMiddleware
app.add_middleware(MaxBodySizeMiddleware)

# AI Model State
model = AstraModelInference()

@app.on_event("startup")
async def startup():
    await model.load_model()
    from app.astra import router
    router.pipeline = AstraPipeline(model)
    logger.info("🛡️ Astra Security Fortress Online - System LOADED")

    # Start Interlink Sync (MySQL -> Supabase)
    asyncio.create_task(sync_service.start_background_sync(interval_seconds=3600))
    
    # Start Inventory Sync (Shopify -> Supabase)
    asyncio.create_task(inventory_sync_service.start_background_sync(interval_seconds=3600))
    
    logger.info("✅ Ecosystem Synchronization tasks started (Interlink + Inventory)")


@app.on_event("shutdown")
def shutdown():
    model.cleanup()

# 3. Unified API v1 Gateway (Consolidated for Doctor App)
from app.auth_routes import auth_router, chat_router as auth_chat_router
from app.doctors.doctor_routes import router as doctor_router
from app.patient_management import router as patient_router
from app.brain_api import brain_router as api_brain_router
from app.prescriptions.prescription_routes import router as prescription_router
from app.catchy_prescription.routes import router as catchy_router
from app.unified_prescription_workflow import router as workflow_router
from app.smart_auto_cart import router as shopify_router
from app.astra_fill.routes import router as astra_fill_router
from app.documents.routes import router as document_router
from app.notification_routes import router as notification_router
from app.medicine_reminders.routes import router as reminder_router
from app.indictrans2_routes import router as translate_router
from app.ai_agent_api import router as ai_agent_router
from app.treatment_centers.center_routes import router as treatment_router
from app.audit_routes import router as audit_router
from app.agora_routes import router as agora_router
from app.finance_routes import finance_router
from fastapi import APIRouter # Added for APIRouter

# Main API Version 1 Router
v1_router = APIRouter(prefix="/api/v1")

# Mount Sub-Routers to v1 (Suffixes are combined, e.g., /api/v1 + /auth = /api/v1/auth)
v1_router.include_router(auth_router)
v1_router.include_router(auth_chat_router)
v1_router.include_router(doctor_auth_router)
v1_router.include_router(doctor_router)      # /api/v1/api/doctors
v1_router.include_router(patient_router)     # /api/v1/patients
v1_router.include_router(prescription_router)# /api/v1/api/prescriptions
v1_router.include_router(catchy_router)      # /api/v1/prescriptions
v1_router.include_router(workflow_router)    # /api/v1/prescription-workflow
v1_router.include_router(shopify_router)     # /api/v1/shopify
v1_router.include_router(astra_fill_router)  # /api/v1/astra-fill
v1_router.include_router(document_router)    # /api/v1/documents
v1_router.include_router(notification_router)# /api/v1/notifications
v1_router.include_router(reminder_router)    # /api/v1/medicine-reminders
v1_router.include_router(translate_router)   # /api/v1/api/translate
v1_router.include_router(ai_agent_router)    # /api/v1/api/ai-agent
v1_router.include_router(treatment_router)   # /api/v1/api/treatment-centers
v1_router.include_router(audit_router)       # /api/v1/audit
v1_router.include_router(agora_router)       # /api/v1/video
v1_router.include_router(finance_router, prefix="/finance") # /api/v1/finance

# Brain router usually has /brain or its own versioning
# brain_api.py has /api/v1/brain internally, so we strip /api/v1 when mounting to v1_router if possible
# or just include it directly in the app
app.include_router(api_brain_router) # This is already at /api/v1/brain

# Add v1_router to main app
app.include_router(v1_router)

# Legacy / Non-Versioned Routes
# The original brain_router (from app.astra.brain_routes) is replaced by api_brain_router
# The original prescription_router and catchy_router are now included via v1_router
app.include_router(astra_router) # /astra/chat
app.include_router(admin_api_router)
app.include_router(dashboard_router)

# Fix for 404 errors (frontend expects /api/doctors, not /api/v1/api/doctors)
app.include_router(doctor_router)

# Wellness Companion API Endpoints
from app.companion_api import router as companion_router
from app.companion_api_enhanced import router as companion_enhanced_router
app.include_router(companion_router)
app.include_router(companion_enhanced_router)


@app.get("/")
def root():
    return {
        "status": "online",
        "service": "Astra AI Healthcare Gateway",
        "version": "4.5.1",
        "endpoints": {
            "v1": "/api/v1",
            "admin": "/admin",
            "dashboard": "/dashboard"
        }
    }

@app.get("/api/v1/health")
def api_health():
    return {"status": "ok", "api_version": "v1", "service": "Astra Secure Gateway"}

@app.get("/health")
def health():
    return {"status": "ok", "security": "bolstered"}
