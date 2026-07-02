# Automation & Escalation Flow Protocol

## 1. The Strategy
Astra uses a **Tagging Protocol** to allow the Brain (api.ayureze.in) to control the Body (Astra Backend).

The Brain is just a text generator. To make it "do" things, it must output specific **Command Tags** in its text response. Astra parses these tags and executes the Python code.

## 2. Supported Tags

### A. Escalation Tag: `[ESCALATE]`
If the AI cannot answer or detects high risk, it outputs this tag.

*   **Brain Output:** `I am not sure about this specific medical condition. [ESCALATE] Please wait while I connect you to a human expert.`
*   **Astra Action:**
    1.  Detects `[ESCALATE]`.
    2.  Strips the tag so the user doesn't see it.
    3.  Triggers `CapabilityAgent` to send an alert to your support team (e.g., via WhatsApp Admin API).

### B. Action Tag: `[ACTION:JSON]`
If the AI wants to perform a task (book appointment, check status), it outputs a JSON object inside this tag.

*   **Brain Output:** `I will book that for you. [ACTION:{"tool": "book_appointment", "data": {"date": "Monday"}}]`
*   **Astra Action:** 
    1.  Parses the JSON inside the tag.
    2.  Executes the python function `tool_book_appointment`.
    3.  Appends the result (e.g., "✅ Success") to the chat.

## 3. How to Prompt the Brain
For this to work, the **System Prompt** on `api.ayureze.in` must include these instructions:

> "You are Astra. If you cannot answer, output [ESCALATE]. If the user asks to book an appointment, output [ACTION:{\"tool\": \"book_appointment\", \"data\": {...}}]."

## 4. Current Implementation status
Your `CapabilityAgent` is now **Live** and listening for these tags.

- **File**: `app/astra/capabilities.py`
- **Logic**: 
    - `process_response_actions()` method scans every incoming AI message.
    - If it finds tags, it executes the corresponding python method in the `CapabilityAgent` class.
