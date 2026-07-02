
import asyncio
import os
import json
import time
import httpx
import re
from datetime import datetime
from typing import Dict, Any, List
from dataclasses import asdict

# Import the actual client used by the app
try:
    # Manual load of .env.txt if not in environment
    if os.path.exists(".env.txt"):
        with open(".env.txt", "r") as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    key, val = line.strip().split("=", 1)
                    os.environ[key] = val
    
    from app.astra_brain_client import AstraBrainClient, Intent
    from app.database import db_manager
except ImportError:
    print("Error: Could not import app modules. Ensure you are running from the project root.")
    exit(1)

class ComprehensiveAudit:
    def __init__(self):
        self.brain = AstraBrainClient()
        # Increase timeout for complex reasoning tasks
        self.brain.client.timeout = httpx.Timeout(300.0, read=300.0, connect=10.0)
        self.db = db_manager
        self.results = []
        self.report_path = "COMPREHENSIVE_AUDIT_REPORT.md"

    async def run_test(self, name: str, category: str, func, *args, **kwargs):
        print(f"Testing {category}: {name}...", end="", flush=True)
        start_time = time.time()
        try:
            # Check if it's a coroutine function or a coroutine object
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
                if asyncio.iscoroutine(result):
                    result = await result
            
            duration = time.time() - start_time
            
            # Normalize result for reporting
            success = True
            if hasattr(result, 'success'):
                success = result.success
            elif isinstance(result, dict) and 'success' in result:
                success = result['success']
            elif result is None:
                success = False
                
            self.results.append({
                "name": name,
                "category": category,
                "success": success,
                "duration": f"{duration:.2f}s",
                "result": result,
                "timestamp": datetime.now().isoformat()
            })
            print(f" {'PASS' if success else 'FAIL'} ({duration:.2f}s)")
            return result
        except Exception as e:
            duration = time.time() - start_time
            self.results.append({
                "name": name,
                "category": category,
                "success": False,
                "duration": f"{duration:.2f}s",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            print(f" FAIL ERROR: {e}")
            return None

    async def run_all(self):
        print("Starting Comprehensive Astra AI Audit")
        print(f"Gateway: {self.brain.base_url}")
        print("-" * 50)

        # 1. System Health
        await self.run_test("Cloudflare Tunnel Health", "System", self.brain.check_health)
        await self.run_test("Supabase EHR Connectivity", "Database", self.db.is_connected)

        # 2. Conversational AI
        await self.run_test("Basic Chat", "Brain Chat", self.brain.chat, "Hello, tell me a quick health tip.")
        await self.run_test("Ayurvedic Query", "Brain Chat", self.brain.chat, "What are the benefits of Ashwagandha for sleep?")

        # 3. AstraFill (Information Extraction)
        fill_text = "Patient Rahul, age 28, reports mild dry cough and slight fever since last night."
        fill_schema = '{"patient_name": "string", "age": "number", "symptoms": "list", "duration": "string"}'
        await self.run_test("Entity Extraction", "AstraFill", self.brain.fill, fill_text, fill_schema)

        # 4. Astra Autopilot (Intent Routing)
        await self.run_test("Booking Intent", "Autopilot", self.brain.autopilot, "I want to book an appointment with Dr. Sharma tomorrow.")
        await self.run_test("Chat Intent", "Autopilot", self.brain.autopilot, "How do I reduce stress naturally?")

        # 5. Smart Prescription (Schedule Extraction)
        rx_text = "Tab. Amoxicillin 500mg - 1-0-1 after food for 5 days. SYP. Grilinctus 10ml TDS."
        await self.run_test("Schedule Parsing", "Smart Prescription", self.brain.extract_schedule, rx_text)

        # 6. Wellness Companion (Content Generation)
        await self.run_test("Meditation Gen", "Wellness", self.brain.generate_wellness, "5-minute anxiety relief meditation", "5 mins")
        await self.run_test("Yoga Plan Gen", "Wellness", self.brain.generate_wellness, "Yoga for lower back pain", "15 mins")

        # 7. Shopify AutoCart (Shop Assist)
        await self.run_test("Product Mapping", "AutoCart", self.brain.shop_assist, "I need something for joint pain and inflammation.")

        # 8. Clinical Intelligence
        patient_notes = "Patient: 45F. BP: 140/95. History of Type 2 Diabetes. Current complaints: Fatigue and blurred vision."
        await self.run_test("Doctor Summary", "Clinical", self.brain.doctor_summary, patient_notes)

        # 9. Analysis Tools
        await self.run_test("Safety Check", "Safety", self.brain.analyze_safety, "I am feeling very depressed and think about hurting myself.")
        await self.run_test("Emotion Detection", "Emotion", self.brain.detect_emotion, "I am so excited to start my new health journey!")

        # 10. Social Intelligence
        p_a = '{"interests": ["Yoga", "Veganism"], "goals": ["Weight loss"]}'
        p_b = '{"interests": ["Yoga", "Meditation"], "goals": ["Fitness"]}'
        await self.run_test("Buddy Matching", "Social", self.brain.profile_analysis, p_a, "buddy_match", p_b)

        print("-" * 50)
        await self.generate_markdown_report()

    async def generate_markdown_report(self):
        success_count = sum(1 for r in self.results if r["success"])
        total_count = len(self.results)
        
        report = []
        report.append("# Astra AI Comprehensive Audit Report")
        report.append(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**Target Gateway:** `{self.brain.base_url}`")
        report.append(f"**EHR Database:** `{'Connected' if self.db.is_connected() else 'Disconnected'}`")
        report.append("\n## Summary")
        report.append(f"- **Total Tests:** {total_count}")
        report.append(f"- **Pass Rate:** {(success_count/total_count)*100:.1f}% ({success_count}/{total_count})")
        
        report.append("\n## Detailed Results")
        report.append("| Category | Test Name | Status | Latency | Response/Output |")
        report.append("|----------|-----------|--------|---------|-----------------|")
        
        for r in self.results:
            status = "PASS" if r["success"] else "FAIL"
            
            # Format output
            output = ""
            res_obj = r.get("result")
            if hasattr(res_obj, '__dict__'):
                try: output = json.dumps(asdict(res_obj))
                except: output = str(res_obj)
            elif isinstance(res_obj, dict):
                output = json.dumps(res_obj)
            else:
                output = str(res_obj or r.get("error", "Unknown"))
                
            # Truncate for table
            if len(output) > 200:
                output = output[:197] + "..."
            
            # Clean for markdown and encoding
            output = output.replace("|", "\\|").replace("\n", " ").replace("`", "'")
            output = output.encode('utf-8', 'ignore').decode('utf-8')
            
            report.append(f"| {r['category']} | {r['name']} | {status} | {r['duration']} | `{output}` |")
            
        report.append("\n\n---")
        report.append("*Verified by Astra AI Integration Suite*")
        
        full_report = "\n".join(report)
        # Deep clean for any remaining surrogates
        full_report = "".join(c for c in full_report if ord(c) < 0x10000)
        
        with open(self.report_path, "w", encoding="utf-8") as f:
            f.write(full_report)
        
        print(f"\nAudit Complete. Detailed report generated in: {self.report_path}")

async def main():
    audit = ComprehensiveAudit()
    try:
        await audit.run_all()
    finally:
        await audit.brain.close()

if __name__ == "__main__":
    asyncio.run(main())
