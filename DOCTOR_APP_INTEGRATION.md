# 🩺 Doctor App Integration Guide (Flutter/React Native)

This guide explains how to connect your **Doctor App** to the Astra AI backend.

---

## 🔗 Connection Details

- **Base URL:** `https://your-vultr-ip-or-domain` (e.g., `https://api.ayureze.in`)
- **Authentication:** Bearer Token (Secure API Key or JWT)

---

## 🛠️ Required Endpoints

### 1. **Doctor Operations (Prescription & Vitals)**

**POST** `/astra-fill/process-voice`
*Use this for voice-based prescription dictation.*

- **Headers:** `Content-Type: multipart/form-data`
- **Body:**
    - `audio`: `[File]` (wav/mp3)
    - `user_id`: `"doctor_123"`
    - `language_code`: `"en-IN"` (or "hi-IN")
- **Response:**
    ```json
    {
      "response": "Prescription generated for Paracetamol 500mg...",
      "capability": "prescription_generation",
      ...
    }
    ```

**POST** `/api/pharmacy/prescription/submit`
*Use this to submit the final confirmed prescription.*

- **Body:**
    ```json
    {
       "doctor_id": "doc_001",
       "patient_id": "pat_123",
       "medicines": [ ... ],
       "diagnosis": "Viral Fever"
    }
    ```

### 2. **AI Assistant (Chat/Query)**

**POST** `/astra/chat`
*General AI helper for the doctor (e.g., "What are interactions for Ashwagandha?").*

- **Body:**
    ```json
    {
      "message": "Is Ashwagandha safe with Paracetamol?",
      "user_id": "doc_001",
      "profile_id": "doc_profile",
      "user_metadata": { "role": "doctor" }
    }
    ```

---

## 📱 Doctor App UI Components (Recommendations)

1.  **Voice Dictation FAB (Floating Action Button):**
    -   Place a prominent microphone button on the "Patient Consultation" screen.
    -   **Action:** Record audio -> Send to `/astra-fill/process-voice`.
    -   **Result:** Auto-fill the prescription form fields.

2.  **Smart Assistant Widget:**
    -   A small chat icon in the top/bottom corner.
    -   Opens a chat overlay to ask Astra medical questions or operational queries (e.g., "Show me patient history").

3.  **Prescription Review Screen:**
    -   Display the AI-extracted prescription.
    -   **Edit/Confirm Buttons**: Allow the doctor to verify before final submission.

---

## 🔐 Security Best Practices

1.  **Secure Storage**: Store the API Key securely in `EncryptedSharedPreferences` (Android) or `Keychain` (iOS).
2.  **HTTPS**: Always use `https://` requests.
3.  **Role Header**: Pass `X-Role: doctor` in headers if your API requires specific permission checks.
