# 🏥 Astra Patient User Journey - End-to-End Architecture

This document tracks the complete flow of a user interacting with the **AyurEze Patient App**, detailing how every backend feature of Astra works together in real-time.

---

## 1. 🔐 User Login (The Gateway)

**User Action:** Opens App -> Enters Phone Number -> Verify OTP.
**Backend Flow:**
1.  **Auth0 / Firebase:** Verifies OTP and returns a JWT Application Token.
2.  **Astra Login Hook:** App calls `/astra/health` to wake up the system.
3.  **Sync:** App fetches active `profile_id` (e.g., "Main User" or "Grandma").

---

## 2. 🏠 Home Screen (Proactive Intelligence)

**User Action:** Lands on Home Dashboard.
**Astra Autopilot (Background):**
1.  **Status Check:** App calls `/autopilot/status/{patient_id}`.
2.  **Logic:** Astra checks: "Does this user have pending medicines? Is a follow-up due?"
3.  **Action:**
    -   If pending meds -> Shows "Time for your Ashwagandha!" widget using **Medicine Reminder Service**.
    -   If follow-up due -> Shows "Book Follow-up" card.

---

## 3. 💬 The AI Chat (Core Companion)

**User Action:** Taps "Ask Astra" -> Says *"I have a severe back pain since yesterday."*
**Astra Pipeline Flow:**
1.  **Receiver (`/astra/chat`):** Receives text/voice + `profile_id`.
2.  **Safety Layer:** Checks for emergencies (Suicide/Heart Attack). *Safe.*
3.  **RAG Memory:** Retrieves context: *User has history of desk job & lower back issues.*
4.  **AI Brain:**
    -   Detects Symptom: "Back Pain".
    -   Consults Knowledge Base: Suggests Ayurvedic remedies (Mahanarayan Oil).
    -   **Decision:** "Pain is severe -> Recommend Doctor."
5.  **Response:** "I understand. Since it's severe, I recommend seeing an Ayurvedic Ortho specialist. I found Dr. Sharma near you. Shall I book?"
6.  **Tool Call:** `doctor_search(specialization='Ortho')`.

---

## 4. 🩺 Booking a Doctor (Search & Consult)

**User Action:** Taps *"Yes, show me doctors."*
**Doctor Service Flow:**
1.  **Tool Execution:** Astra runs `doctor_search` tool.
2.  **Database:** Queries **Laravel MySQL** for active doctors with 'Ortho' tag.
3.  **Result:** Returns list: *Dr. Anjali (5km), Dr. Raj (12km).*
4.  **UI:** App renders "Doctor Cards" in the chat.
5.  **Booking:** User taps "Book Dr. Anjali @ 5 PM".
    -   Astra API: `/api/appointments/book`.
    -   **WhatsApp:** Sends confirmation to Dr. Anjali's WhatsApp automatically.

---

## 5. 🛒 Smart Pharmacy (Buying Medicines)

**User Action:** Astra says *"Meanwhile, for relief, you can try Mahanarayan Oil."* -> User says *"Okay, add it to cart."*
**Shopify Integration Flow:**
1.  **AI Parsing:** Recognizes intent `SHOPPING_ADD`.
2.  **Search:** Calls **Shopify API** to find "Mahanarayan Oil" product ID.
3.  **Cart Action:** Calls `shopify_cart` tool -> Creates a **Shopify Draft Order**.
4.  **UI:** Shows "Cart Updated (1 item)" bubble in chat.
5.  **Checkout:** User taps "Checkout" -> Redirects to Shopify Webview/Native Checkout.

---

## 6. 📂 Medical Records (The Vault)

**User Action:** Consultation done. Doctor uploaded prescription.
**Storj EHR Flow:**
1.  **Upload:** Doctor app sends PDF to `/storj/upload`.
2.  **Encryption:** API hashes Patient ID -> Encrypts file -> Splits to **Storj Network**.
3.  **Patient View:**
    -   User opens "Records" tab.
    -   App calls `/storj/list`.
    -   **Retrieval:** Backend generates a **temporary secure link (24h)**.
    -   **Display:** PDF opens securely in-app.

---

## 7. ⏰ Ongoing Care (Reminders)

**User Action:** Closes app and goes about day.
**Medicine Reminder Flow:**
1.  **Schedule:** Backend knows prescription: "1 Tablet at 8 PM".
2.  **Trigger:** At 8 PM, **Cron Job** fires.
3.  **Notification:**
    -   **Push:** "Time for your medicine!"
    -   **WhatsApp:** Astra Bot sends: *"Hi! Did you take your 8 PM dose?"*
4.  **Feedback:** User replies "Yes" on WhatsApp.
5.  **Compliance:** Adherence recorded in Database.

---

## 🧩 Architecture Diagram (Conceptual)

```
[Patient App]  <-- (HTTPS/JSON) -->  [Astra API Gateway (Vultr)]
      |                                       |
      |                                  +----v-----+
(User Input)                             | Pipeline |  <-- (Context) --> [Supabase Memory]
      |                                  +----+-----+
      v                                       |
[Auth0 Login]                            (Decision?)
                                              |
      +----------------------+----------------+------------------+
      |                      |                |                  |
[Doctor Service]      [Shopify Tool]     [Storj Tool]     [Autopilot]
      |                      |                |                  |
(Laravel DB)           (Store API)      (Decentralized)   (State Engine)
      |                      |                |                  |
  [Find Doc]           [Add-to-Cart]      [Save PDF]      [Send Reminder]
```
