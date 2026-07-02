import sys
import os
import time

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

log("Starting Full Diagnostic Run")

try:
    log("Importing logging")
    import logging
    log("Importing asyncio")
    import asyncio
    log("Importing httpx")
    import httpx
    log("Importing supabase (This might be slow)")
    from supabase import create_client, Client
    log("Supabase base imported")
    
    log("Importing app.database")
    from app.database import db_manager
    log("app.database imported")
    
    log("Importing app.astra_brain_client")
    from app.astra_brain_client import get_brain_client
    log("app.astra_brain_client imported")
    
    log("Importing app.astra.pipeline")
    from app.astra.pipeline import AstraPipeline
    log("app.astra.pipeline imported")

    async def main():
        log("Inside async main")
        pipeline = AstraPipeline()
        log("Pipeline initialized")
        
        log("Testing brain health...")
        health = await pipeline.brain.check_health()
        log(f"Brain Health: {health}")
        
        log("Testing chat...")
        res = await pipeline.brain.chat("Hi")
        log(f"Chat Response: {res.answer[:50]}...")
        
        log("Diagnostic Complete")

    if __name__ == "__main__":
        asyncio.run(main())

except Exception as e:
    log(f"CRITICAL ERROR: {e}")
    import traceback
    log(traceback.format_exc())
