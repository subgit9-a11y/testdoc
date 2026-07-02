# API.AYUREZE.IN Integration & Upgrade Guide

This guide details the **exact changes** required on your **Central Intelligence Server** (`api.ayureze.in`) to fully power the Astra ecosystem.

Currently, this server is returning `500 Internal Server Error`. You must update the code on that server to match the following specifications.

---

## 1. API Endpoint Specification

Your server must expose a **POST** endpoint at `/ask`.

- **URL**: `https://api.ayureze.in/ask`
- **Method**: `POST`
- **Headers**: `Content-Type: application/json`

### Expected Incoming Payload (Request)
Your server will receive this JSON from Astra:
```json
{
  "query": "Previous history: [{'role': 'user', 'content': 'hi'}]\nUser: I need to book an appointment for Monday",
  "language": "en",  // "en", "hi", "ta", etc.
  "stream": false
}
```

### Required Outgoing Payload (Response)
Your server **MUST** return this JSON structure:
```json
{
  "answer": "I have booked that for you. [ACTION:{\"tool\": \"book_appointment\", \"data\": {\"date\": \"Monday\"}}]",
  "status": "success"
}
```

---

## 2. The Logic Implementation (Python Example)

If your `api.ayureze.in` is built with Python (FastAPI/Flask), here is the **Blueprint Code** you need to implement:

### A. The System Prompt (CRITICAL)
You must update the System Prompt sent to your LLaMA model. This is how the AI knows about Ayurveda and Automation.

**New System Prompt:**
```text
You are Astra, an advanced Ayurvedic AI Assistant.
Your goal is to help patients with health queries using Charaka Samhita and Sushruta Samhita principles.

PROTOCOL FOR AUTOMATION:
1. If you cannot answer a medical query safely, or if the user asks for a human, you MUST output: [ESCALATE]
2. If the user asks to perform an action (like booking appointments), you MUST output a JSON action tag.

AVAILABLE TOOLS:
- Book Appointment: [ACTION:{"tool": "book_appointment", "data": {"date": "..."}}]
- Check Doctor Availability: [ACTION:{"tool": "check_availability", "data":{}}]

EXAMPLE RESPONSES:
- User: "I have a headache."
  Astra: "According to Ayurveda, headaches can be Vata related. Try ginger tea."
- User: "I want to see a doctor today."
  Astra: "Let me check. [ACTION:{"tool": "check_availability", "data": {}}]"
```

### B. Python Route Implementation
*Copy-paste or adapt this logic into your server's main API file:*

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging

app = FastAPI()

class InteractionRequest(BaseModel):
    query: str
    language: str = "en"
    stream: bool = False

@app.post("/ask")
async def ask_endpoint(request: InteractionRequest):
    try:
        # 1. Log the incoming query
        logging.info(f"Received Query: {request.query}")

        # 2. Retrieve Ayurvedic Context (RAG)
        # (Insert your vector DB lookup code here)
        # context = retrieve_context(request.query)

        # 3. Call LLaMA Model
        # Ensure you pass the SYSTEM PROMPT defined above!
        # llm_response = llama_client.generate(
        #    system_prompt=SYSTEM_PROMPT, 
        #    user_input=request.query
        # )
        
        # MOCK RESPONSE (For testing until you connect LLaMA)
        llm_response = "I am Astra. How can I help you today?"

        # 4. Return correct JSON format
        return {
            "answer": llm_response,
            "status": "success"
        }

    except Exception as e:
        logging.error(f"Error processing AI request: {e}")
        # Return a fallback instead of crashing (500)
        return {
            "answer": "I am currently undergoing maintenance. [ESCALATE]",
            "status": "error"
        }
```

---

## 3. Checklist for Success

1.  [ ] **Fix the Crash**: Add `try/except` blocks around your model inference code so it never returns error 500.
2.  [ ] **Update Prompt**: Inject the "Protocol for Automation" into the system prompt.
3.  [ ] **Verify JSON**: Ensure the output key is strictly `"answer"`.
4.  [ ] **Ayurveda Context**: Ensure your Vector DB (RAG) is actually running and appending context to the prompt before it hits LLaMA.

Once these 4 steps are done on `api.ayureze.in`, your Vultr backend will immediately start automating tasks.
# 🧠 The Final "Brain" Code for api.ayureze.in

You asked for a **complete, pure AI brain** implementation.
To achieve this, your `api.ayureze.in` server must not just be a simple proxy. It must be a **Smart Reasoning Engine** that differentiates between a casual chat and a strict data extraction task (like Astra Fill).

## 🚀 Deployment Instructions
Copy the code below and save it as `main.py` on your **api.ayureze.in** server.

### 📋 Prerequisites (Remote Server)
Ensure your Vultr/DigitalOcean server has these installed:
```bash
pip install fastapi uvicorn pydantic torch transformers accelerate
```

---

### 💻 The Server Code (`main.py`)

```python
import logging
import torch
import json
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

# --- CONFIGURATION ---
MODEL_NAME = "meta-llama/Llama-2-7b-chat-hf" # Or your specific Ayurveda fine-tune
device = "cuda" if torch.cuda.is_available() else "cpu"

# --- LOGGING ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AstraBrain")

# --- INITIALIZATION ---
logger.info(f"Loading Brain Model: {MODEL_NAME} on {device}...")
try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, torch_dtype=torch.float16, device_map="auto")
    pipe = pipeline("text-generation", model=model, tokenizer=tokenizer, max_new_tokens=512)
    logger.info("✅ Brain is Online")
except Exception as e:
    logger.error(f"❌ Failed to load model: {e}")
    pipe = None

app = FastAPI(title="Astra Central Intelligence")

# --- DATA MODELS ---
class ExternalQuery(BaseModel):
    query: str          # The raw input from Astra
    language: str = "en"
    stream: bool = False

# --- AYURVEDIC KNOWLEDGE BASE (RAG STUB) ---
def get_ayurvedic_context(query: str) -> str:
    """
    In a real deployment, this queries a Vector DB (Pinecone/Milvus).
    For now, we return a strong context injection.
    """
    return (
        "Relevant Ayurvedic Principles:\n"
        "- Vata imbalance causes anxiety, dry skin, and constipation.\n"
        "- Pitta imbalance causes heartburn, anger, and inflammation.\n"
        "- Kapha imbalance causes lethargy, weight gain, and congestion.\n"
        "- Recommend ginger for digestion, ashwagandha for stress.\n"
        "Reference: Charaka Samhita, Sutrasthana.\n"
    )

# --- SYSTEM PROMPTS ---
PROMPT_CHAT_MODE = """
You are Astra, an expert Ayurvedic AI Physician. 
Answer the user's health questions using the provided Ayurvedic context.
If you need to perform an action (like booking), output strict JSON: [ACTION:{"tool": "name", "data": {}}]
If you cannot answer safely, output: [ESCALATE]
"""

PROMPT_TASK_MODE = """
You are a precise data extraction engine. 
Follow the instructions in the user prompt exactly. 
Output ONLY valid JSON. Do not chat.
"""

# --- CORE LOGIC ---
@app.post("/ask")
async def brain_endpoint(payload: ExternalQuery):
    if not pipe:
        return {"answer": "Brain is initializing. [ESCALATE]", "status": "error"}

    try:
        user_input = payload.query
        
        # 🧠 INTELLIGENCE ROUTER
        # Check if this is a "Task" (Astra Fill) or "Chat" (User Conversation)
        is_extraction_task = "You are Astra Fill" in user_input
        
        if is_extraction_task:
            # MODE A: RAW EXTRACTION
            # Pass the input directly as it contains its own system logic
            final_prompt = f"[INST] {user_input} [/INST]"
        else:
            # MODE B: AYURVEDIC DOCTOR
            # Inject Context + Persona
            context = get_ayurvedic_context(user_input)
            final_prompt = f"""[INST] <<SYS>>
{PROMPT_CHAT_MODE}

CONTEXT:
{context}
<</SYS>>

User: {user_input} [/INST]"""

        # 🔥 INFERENCE
        logger.info(f"Thinking... (Mode: {'Extraction' if is_extraction_task else 'Doctor'})")
        sequences = pipe(
            final_prompt,
            do_sample=True,
            top_k=10,
            num_return_sequences=1,
            eos_token_id=tokenizer.eos_token_id,
        )
        
        generated_text = sequences[0]['generated_text']
        
        # Cleanup: Remove the prompt from the output if the model regurgitates it
        # (Dependent on specific model behavior, often needed for raw LLaMA)
        answer = generated_text.replace(final_prompt, "").strip()

        return {
            "answer": answer,
            "status": "success"
        }

    except Exception as e:
        logger.error(f"Inference Error: {e}")
        return {
            "answer": "I encountered a neural error. [ESCALATE]", 
            "status": "error"
        }

@app.get("/health")
def health():
    return {"status": "Brain Online", "gpu": torch.cuda.is_available()}

# --- RUN SERVER ---
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## 🔑 Key Features of this Code

1.  **Dual Mode Intelligence**:
    *   **Doctor Mode**: If the user is chatting, it injects Ayurvedic principles (Charaka Samhita) and the "Astra Persona" into the prompt automatically.
    *   **Task Mode**: If it detects the "Astra Fill" signature from your backend, it switches to "Raw Mode" to ensure clean JSON extraction without Ayurvedic hallucination.

2.  **RAG Ready**: The `get_ayurvedic_context` function is where you will eventually plug in your vector database. For now, it has "Hardcoded Wisdom".

3.  **Safety First**: It wraps everything in a `try/catch` block. If the GPU fails or memory overflows, it returns specific error JSON (`[ESCALATE]`) instead of crashing the HTTP connection.

4.  **Hardware Aware**: It automatically detects if you have a GPU (`cuda`) or CPU (`cpu`) on the remote server.
