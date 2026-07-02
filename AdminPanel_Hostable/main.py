from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from app.enhanced_inference import AstraModelInference
from app.astra.pipeline import AstraPipeline
from app.astra.router import router as astra_router
from app.astra.brain_routes import router as brain_router
from app.admin.routes import router as admin_api_router
from app.admin.dashboard import router as dashboard_router
from app.auth_middleware import rate_limit_check
import logging
import os

# Security: Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AstraSecurityFortress")

app = FastAPI(
    title="Astra AI Unified Engine",
    version="4.5.0",
    docs_url="/astra/docs", # Obscured docs URL
    redoc_url="/astra/redoc"
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
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'none'; object-src 'none';"
        return response

app.add_middleware(SecurityHeadersMiddleware)

# AI Model State
model = AstraModelInference()

@app.on_event("startup")
async def startup():
    await model.load_model()
    from app.astra import router
    router.pipeline = AstraPipeline(model)
    logger.info("🛡️ Astra Security Fortress Online - System LOADED")

@app.on_event("shutdown")
def shutdown():
    model.cleanup()

# 3. Routes with Global Protections
# Any request to brain_router (v1 API) is now rate-limited
app.include_router(
    brain_router, 
    prefix="", 
    dependencies=[Depends(rate_limit_check)]
)

app.include_router(astra_router)
app.include_router(admin_api_router)
app.include_router(dashboard_router)

@app.get("/")
def root():
    return {"status": "ok", "service": "Astra Secure Gateway"}

@app.get("/health")
def health():
    return {"status": "ok", "security": "bolstered"}
