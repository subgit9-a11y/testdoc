# 🏥 Patient App Integration Guide (Flutter/React Native)

This guide explains how to connect your **Patient App** to the Astra AI backend.

---

## 🔗 Connection Details

- **Base URL:** `https://your-vultr-ip-or-domain` (e.g., `https://api.ayureze.in`)
- **Authentication:** Bearer Token (JWT from Auth0/Firebase)

---

## 🛠️ Required Endpoints

### 1. **AI Health Companion (Chat)**

**POST** `/astra/chat`
*The core chat interface for patients.*

- **Body:**
    ```json
    {
      "message": "I have a headache",
      "user_id": "patient_123",
      "profile_id": "profile_001",
      "is_voice": false
    }
    ```
- **Response:**
    ```json
    {
      "response": "I'm sorry to hear that. How long have you had it?",
      "emotion": "empathy",
      "tool_call": "symptom_checker" (optional)
    }
    ```

### 2. **Medicine Reminders**

**GET** `/api/reminders/{patient_id}`
*Fetch active medicine schedules.*

- **Response:**
    ```json
    [
      { "medicine": "Dolo 650", "time": "09:00 AM", "taken": false }
    ]
    ```

### 3. **Doctor Search**

**POST** `/astra/chat` (via Intent)
*Patients find doctors by simply asking.*

- **User**: "Find me an Ayurveda doctor for back pain."
- **AI**: Calls `doctor_search` tool backend.
- **Response**: Returns a list of doctor cards in the chat JSON (parse `tool_result` if available, or text).

---

## 📱 Patient App UI Components (Recommendations)

1.  **AI Chat Screen (Clean Interface):**
    -   Similar to WhatsApp/ChatGPT UI.
    -   **Typing Indicators**: Show when Astra is "thinking".
    -   **Quick Replies**: Chips for common actions (e.g., "Book Doctor", "My Medicines").

2.  **Voice Mode:**
    -   Microphone button in the chat bar.
    -   **Action**: Record -> Send to `/astra/chat` with `is_voice: true` (or process STT on device and send text).

3.  **Rich Message Bubbles:**
    -   **Doctor Card Bubble**: If AI suggests a doctor, render a clickable card (Name, Photo, "Book Now" button).
    -   **Product Card Bubble**: If AI suggests medicines (Shopify), render a product card ("Add to Cart").

4.  **EHR Vault:**
    -   A dedicated tab for "Medical Records".
    -   **Fetch**: List secure Storj links.
    -   **View**: In-app PDF viewer for downloaded prescriptions.

---

## 🎨 UI Design Tips (Aesthetics)
-   **Color Palette**: Calming greens/blues (Ayurveda theme) + Clean White/Dark mode.
-   **Typography**: Clean sans-serif (Inter/Roboto).
-   **Micro-interactions**: Smooth fade-ins for AI messages.
