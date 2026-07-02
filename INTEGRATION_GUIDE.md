# Astra AI <-> api.ayureze.in Integration Protocol

## 1. Overview
The `api.ayureze.in` serves as the **Cognitive Brain** of the Astra ecosystem. While the Astra backend on Vultr handles user connections, database storage, and whatsapp messages, it delegates all intelligence, reasoning, and Ayurvedic knowledge generation to `api.ayureze.in`.

## 2. API Contract
Your Astra backend communicates with the Brain using a strict JSON protocol without authentication headers (currently).

### Endpoint
`POST https://api.ayureze.in/ask`

### Request Format
Astra sends this JSON payload:
```json
{
  "query": "Patient complains of Pitta imbalance with heartburn. Suggest remedies.",
  "language": "en",
  "stream": false
}
```

### Response Format
The Brain returns this JSON payload:
```json
{
  "answer": "Based on Ayurvedic principles, Pitta imbalance can be managed by cooling foods...",
  "status": "success"
}
```

## 3. How the "Brain" Logic Works
The api.ayureze.in server must implement the following logic pipeline to serve Astra correctly:

1.  **Receive**: Accept the `query` string from Astra.
2.  **Contextualize**:
    *   Recognize if the query is a simple chat or a medical request.
    *   If medical, retrieve specialized **Ayurvedic Knowledge Base** vectors (Charaka Samhita, Sushruta Samhita).
3.  **Process (LLM)**:
    *   Feed the User Query + Ayurvedic Context into the LLaMA model.
    *   *System Prompt*: "You are Astra, an expert Ayurvedic AI assistant. Answer using authentic Ayurvedic principles, citing Doshas where applicable."
4.  **Guardrails**:
    *   Ensure no harmful medical advice is generated.
    *   Filter out non-relevant topics.
5.  **Return**: Send the clean text response back to Astra in the `answer` field.

## 4. Integration Checklist for Deployment
To ensure your Astra backend connects seamlessy:

- [x] **Client Implementation**: Your `app/enhanced_inference.py` is already configured to POST to the correct URL.
- [ ] **Error Handling**: Currently, the API returns 500. This must be fixed on the **Server Side** to handle empty or malformed queries gracefully.
- [ ] **Latency**: Ensure the Brain responds within <30 seconds (Astra's timeout limit).
- [ ] **Ayurveda Context**: Ensure the LLaMA model on the server is actually prompted with Ayurvedic context, otherwise it will just be a generic chatbot.

## 5. Future: Tool Calling (Actionable AI)
To enable automation (booking appointments, creating prescriptions), the API response should eventually support structured data:

```json
{
  "answer": "I have booked your appointment.",
  "action": {
    "tool": "book_appointment",
    "params": {
      "time": "10:00 AM",
      "date": "2024-02-20"
    }
  }
}
```
*Note: Your `CapabilityAgent` in Astra is ready to handle this once the API starts sending it.*
