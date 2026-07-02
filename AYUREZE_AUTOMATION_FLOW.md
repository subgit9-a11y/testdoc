# 🩺 AyurEze Automation Architecture & User Flow

This document outlines the complete automated workflow for the AyurEze ecosystem, mapping your business requirements to the Astra 2.0 backend architecture.

---

## 🔁 The "Knee Pain" User Journey (Automated Flow)

### Phase 1: Onboarding & Discovery
1.  **Login**: User logs in with Firebase Auth (Verified OTP).
2.  **Home Page**: User sees the static Homepage (Carousel, Panels).
    -   *User Action:* Clicks the **"Talk to Astra"** Floating Action Button (FAB).
3.  **Astra Trigger**:
    -   **Backend:** `/astra/health` confirms connectivity.
    -   **AI:** "Namaste! I am Astra. I see this is your first time. I've created your wellness profile. How can I help you today?"
    -   **Pipeline:** Creates `UserSession` and initiates `RAGMemory`.

### Phase 2: Consultation & Intake (Astra Fill)
4.  **Symptom Expression**:
    -   *User:* "I have bad knee pain."
    -   **AI Analysis:** Detects `SYMPTOM_CHECK` intent.
    -   **Response:** Explains causation (Vata aggravation), suggests consultation.
5.  **Astra Fill Trigger (Intake)**:
    -   *User:* "Okay, let's book."
    -   **Action:** App opens "Astra Fill" Voice Mode.
    -   *User:* Describes details by voice.
    -   **Backend (`/astra-fill/process-voice`):**
        -   Transcribes audio (Whisper/Google).
        -   Extracts structured keys: `{symptom: "Knee Pain", duration: "2 days", severity: "High"}`.
        -   **Result Generation:** Generates a **"Pre-Consultation Summary" PDF** (JSON -> PDF on App/Backend).
        -   **Storage:** Uploads Summary to **Storj**.

### Phase 3: Doctor Matching & Booking
6.  **Panel Recommendation**:
    -   **AI:** "Based on your knee pain, here are top Ortho (Vata) specialists."
    -   **Tool:** `doctor_search(specialization="Ortho")`.
    -   **UI:** User selects Dr. Ramesh.
7.  **Data Sharing**:
    -   **Backend:** Grants Dr. Ramesh access to the **Astra Fill Summary PDF** (via Storj Link).
    -   **Notification:** Dr. Ramesh gets a WhatsApp: "New Appointment with [User]. View Summary: [link]".

### Phase 4: The Consultation & Prescription
8.  **Consultation**: Video/Audio call happens.
9.  **Prescription Generation**:
    -   *Doctor Action:* Uses **Doctor App** to prescribe "Mahanarayan Oil" & "Panchakarma".
    -   **Backend:**
        -   Generates **Prescription PDF**.
        -   Uploads to **Storj** (Patient Folder).
        -   **Action:** Triggers `PostPrescriptionWorkflow`.

### Phase 5: Post-Consultation Automation (The Magic)
10. **Astra Extraction & Piping**:
    -   **Parser:** Reads prescription items.
    -   **Shopify:** Auto-adds "Mahanarayan Oil" to User's **Smart Cart**.
    -   **Booking:** Detects "Janu Basti" (Treatment) -> Opens "Book Treatment" slot for user.
11. **Communication**:
    -   **WhatsApp:** User gets message:
        > "Dr. Ramesh's prescription is ready! 📄
        > 1. Medicine added to your cart 🛒 [Checkout Link]
        > 2. Treatment 'Janu Basti' recommended. Book slot? 🗓️"
12. **Care Companion (Autopilot)**:
    -   **Backend:** `Astra Autopilot` activates `Journey: TREATMENT_STARTED`.
    -   **Daily:** Checks in: "Did you apply the oil today?"
    -   **Reminders:** Sets 8 PM Reminder for meds.

---

## ✅ Feature Checklist for App Developers

### 📱 Patient App Features
1.  **Authentication**: Firebase Phone Auth Integration.
2.  **Home Dashboard**:
    -   Fetch Banners/Doctors from Admin API.
    -   **"Ask Astra" FAB**: Global floating button to launch AI chat.
3.  **Astra Chat Interface**:
    -   Typing indicators, Voice Recorder (for Astra Fill).
    -   **Components**: Render "Doctor Cards", "Product Cards", and "Booking Slots" inside chat.
4.  **Astra Fill UI**:
    -   Dedicated screen for "Intake Mode" (Voice/Text).
    -   "Review & Confirm" screen for extracted data.
    -   PDF Viewer (for Pre-consultation reports).
5.  **Smart Cart**:
    -   Sync with Shopify Draft Orders.
    -   "One-Click Checkout" for prescribed meds.
6.  **EHR Vault**:
    -   List Storj Documents.
    -   Secure PDF Viewer.
7.  **Autopilot Widgets**:
    -   Home screen widget: "Next Medicine: 8 PM".

### 👨‍⚕️ Doctor App Features
1.  **Dashboard**:
    -   "Upcoming Appointments".
    -   "Patient Queue" (with access to Astra Fill Summary PDFs).
2.  **Voice RX (Prescriber)**:
    -   "Dictate Prescription" button (uses Astra Fill).
    -   Auto-convert speech to Medicine List.
3.  **E-Prescription Pad**:
    -   Digital signature support.
    -   **"Send to Patient"**: Triggers the Astra Automation Pipeline (Upload + WhatsApp + Cart).
4.  **Patient History**:
    -   View Patient's Storj records (with consent).

---

## 📂 Data Flow Summary

| Step | Component | Data Action |
| :--- | :--- | :--- |
| **Intake** | Astra Fill | Voice -> Text -> **Summary PDF** |
| **Storage** | Storj | Encrypts & Stores PDFs |
| **Logic** | Astra Brain | Matches Doctor, Explains Symptoms |
| **Sales** | Shopify | Prescription -> **Draft Order** |
| **Comms** | WhatsApp | Notifications, PDF Links, Reminders |
| **Care** | Autopilot | Daily check-ins, Adherence tracking |
