#!/bin/bash
API_URL="https://api.ayureze.in/v1"

echo "🚀 Starting Astra Brain v7.5 Validation..."
echo "--------------------------------------------"

# 1. Chat
echo -n "1. Chat: "
curl -s -X POST "$API_URL/chat" -H "Content-Type: application/json" \
-d '{"q":"What is Triphala?"}' | grep -v "404" | grep -q "\"answer\"\|\"response\"\|\"success\"" && echo "✅ PASSED" || echo "❌ FAILED"

# 2. Autopilot
echo -n "2. Autopilot: "
curl -s -X POST "$API_URL/autopilot" -H "Content-Type: application/json" \
-d '{"q":"I want to book a doctor"}' | grep -q "intent" && echo "✅ PASSED" || echo "❌ FAILED"

# 3. Safety Analysis
echo -n "3. Safety Sentinel: "
curl -s -X POST "$API_URL/analyze_safety" -H "Content-Type: application/json" \
-d '"High fever and chest pain"' | grep -q "is_safe" && echo "✅ PASSED" || echo "❌ FAILED"

# 4. Emotion Detection
echo -n "4. Emotion Detection: "
curl -s -X POST "$API_URL/detect_emotion" -H "Content-Type: application/json" \
-d '"I am very frustrated with my back pain"' | grep -q "emotion" && echo "✅ PASSED" || echo "❌ FAILED"

# 5. Wellness Generation
echo -n "5. Wellness Gen: "
curl -s -X POST "$API_URL/generate_wellness" -H "Content-Type: application/json" \
-d '{"topic":"Vata Balancing", "duration":"10 mins"}' | grep -q "content\|success" && echo "✅ PASSED" || echo "❌ FAILED"

# 6. Fill (Extraction)
echo -n "6. Fill/Extract: "
curl -s -X POST "$API_URL/fill" -H "Content-Type: application/json" \
-d '{"text":"I have had a headache for 3 days", "schema_def":"{\"duration\": \"string\"}"}' | grep -q "extracted_data" && echo "✅ PASSED" || echo "❌ FAILED"

echo "--------------------------------------------"
echo "Done."
