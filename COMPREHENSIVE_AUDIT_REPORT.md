# Astra AI Comprehensive Audit Report
**Date:** 2026-05-17 23:02:24
**Target Gateway:** `https://metal-rotary-nano-heavily.trycloudflare.com`
**EHR Database:** `Disconnected`

## Summary
- **Total Tests:** 15
- **Pass Rate:** 46.7% (7/15)

## Detailed Results
| Category | Test Name | Status | Latency | Response/Output |
|----------|-----------|--------|---------|-----------------|
| System | Cloudflare Tunnel Health | PASS | 0.41s | `{"status": "offline", "error": "[Errno 11001] getaddrinfo failed"}` |
| Database | Supabase EHR Connectivity | PASS | 0.00s | `Unknown` |
| Brain Chat | Basic Chat | FAIL | 0.06s | `{"answer": "I'm having trouble connecting to the brain.", "mode": "error", "success": false}` |
| Brain Chat | Ayurvedic Query | FAIL | 0.00s | `{"answer": "I'm having trouble connecting to the brain.", "mode": "error", "success": false}` |
| AstraFill | Entity Extraction | FAIL | 0.00s | `{"success": false, "error": "[Errno 11001] getaddrinfo failed"}` |
| Autopilot | Booking Intent | PASS | 0.00s | `AutopilotResponse(intent=<Intent.CHAT: 'chat'>, status='error', confidence=1.0)` |
| Autopilot | Chat Intent | PASS | 0.00s | `AutopilotResponse(intent=<Intent.CHAT: 'chat'>, status='error', confidence=1.0)` |
| Smart Prescription | Schedule Parsing | PASS | 0.00s | `{"reminders": [], "raw_json": "[Errno 11001] getaddrinfo failed"}` |
| Wellness | Meditation Gen | FAIL | 0.00s | `{"success": false, "error": "[Errno 11001] getaddrinfo failed"}` |
| Wellness | Yoga Plan Gen | FAIL | 0.00s | `{"success": false, "error": "[Errno 11001] getaddrinfo failed"}` |
| AutoCart | Product Mapping | FAIL | 0.00s | `{"success": false, "error": "[Errno 11001] getaddrinfo failed"}` |
| Clinical | Doctor Summary | FAIL | 0.00s | `{"success": false, "error": "[Errno 11001] getaddrinfo failed"}` |
| Safety | Safety Check | PASS | 0.00s | `{"is_safe": true, "flags": [], "risk_level": "unknown"}` |
| Emotion | Emotion Detection | PASS | 0.00s | `{"emotion": "Neutral", "intensity": "Medium", "confidence": 0.8}` |
| Social | Buddy Matching | FAIL | 0.00s | `{"success": false, "error": "[Errno 11001] getaddrinfo failed"}` |


---
*Verified by Astra AI Integration Suite*