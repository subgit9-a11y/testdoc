from fastapi import APIRouter, HTTPException
from app.astra.pipeline import AstraPipeline

router = APIRouter(prefix="/astra", tags=["astra"])

pipeline: AstraPipeline | None = None

@router.post("/chat")
async def chat(payload: dict):
    if not pipeline:
        raise HTTPException(503, "Astra not ready")

    message = payload.get("message")
    language = payload.get("language", "en")

    if not message:
        raise HTTPException(400, "Message required")

    reply = await pipeline.run(message, language)
    return {"reply": reply}
