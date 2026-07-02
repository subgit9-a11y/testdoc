# 🏥 Doctor App Full Implementation Guide

This comprehensive guide details how to implement the newly enabled **Doctor App Features** in your Flutter application. These features turn your app into a powerful clinical tool connected to the **Astra AI Backend**.

---

## 🚀 1. Base Configuration

Ensure your Flutter app is pointing to your hosted Astra URL.

*   **Base URL:** `https://your-api-domain.com` (or your Vultr IP)
*   **Authentication:** Pass the Firebase Auth Token in the header.

```dart
// Example Header in typical Flutter request
headers: {
  'Authorization': 'Bearer <firebase_id_token>',
  'Content-Type': 'application/json',
}
```

---

## 👤 2. Doctor Identity & Onboarding

**Goal:** Register a doctor or fetch their profile to show on the dashboard.

### **A. Register Doctor**
*   **Endpoint:** `POST /api/doctors/register`
*   **When to call:** First time user login (after Firebase Auth).
*   **Payload:**
    ```json
    {
      "name": "Dr. Aditi Sharma",
      "specialization": "Ayurveda",
      "qualifications": ["BAMS", "MD"],
      "experience_years": 8,
      "consultation_fee": 500,
      "available_days": ["Mon", "Wed", "Fri"],
      "location": {
        "latitude": 12.97,
        "longitude": 77.59,
        "city": "Bangalore"
      }
    }
    ```

### **B. Get Doctor Profile**
*   **Endpoint:** `GET /api/doctors/{doctor_id}`
*   **Use Case:** Show profile in the "Account" tab.

---

## 📄 3. Patient comprehensive View (The "Clinical Dashboard")

**Goal:** Before prescribing, see everything about the patient in ONE request.

*   **Endpoint:** `GET /api/doctors/patient-view/{patient_id}`
*   **What you get:**
    1.  **Demographics:** Name, Age, Allergies.
    2.  **AI Intake Summary:** The latest symptoms/complaints extracted by Astra AI from the patient's chat.
    3.  **History:** Last 5 prescriptions and consultations.

*   **Flutter Implementation Tip:** Use a `FutureBuilder` to load this page.

```json
// Response Structure
{
  "patient_profile": { "name": "Rohan", "allergies": "Peanuts" ... },
  "latest_astra_fill": { "extracted_symptoms": ["Headache", "Fever"] },
  "recent_consultations": [ ... ],
  "prescription_history": [ ... ]
}
```

---

## 💊 4. Smart Prescription Writing (With Product Search)

**Goal:** Write prescriptions that map to REAL inventory (Shopify) so 1-click buying works.

### **A. Search Medicines**
*   **Endpoint:** `GET /api/doctors/products/search?query=ashwagandha`
*   **Use Case:** As the doctor types in the prescription form, show a dropdown of available medicines.
*   **Response:**
    ```json
    [
      {
        "medicine_name": "Organic India Ashwagandha",
        "shopify_variant_id": "837492...",
        "price": "450.00",
        "is_available": true
      }
    ]
    ```

### **B. Suggest from Symptoms**
*   **Endpoint:** `GET /api/doctors/products/suggest-from-intake?symptoms=cough,cold`
*   **Use Case:** "One-tap add" suggested medicines based on the patient's symptoms.

---

## ✅ 5. Final Submission & Automation (The "Magic Button")

**Goal:** One button that does EVERYTHING (Save DB, PDF, WhatsApp, Cart, Reminders).

*   **Endpoint:** `POST /api/prescriptions/submit-and-automate`
*   **Query Params:** `?doctor_id=...&patient_id=...`
*   **Payload:**

```json
{
  "diagnosis": "Viral Upper Respiratory Infection",
  "medicines": [
    {
      "medicine_name": "Sitopaladi Churna",
      "shopify_variant_id": "123456789", 
      "dose": "1 tsp",
      "schedule": "1-0-1",
      "timing": "After Food",
      "duration": "5 days",
      "instructions": "Mix with honey"
    }
  ],
  "lifestyle_advice": "Steam inhalation twice daily",
  "follow_up_date": "2024-02-10",
  "auto_process": true
}
```

### **What Happens Automatically?**
1.  **Prescription Record** created in SQL Database.
2.  **PDF Generated** (Official letterhead format) & uploaded to Cloud (Storj).
3.  **Shopify Cart** created for the patient with "Sitopaladi Churna".
4.  **WhatsApp Message** sent to Patient: 
    *   *"Dr. Aditi has sent your prescription. [Download PDF]"*
    *   *"Buy Medicines Now: [Link]"*
5.  **Reminders** scheduled (Patient gets WhatsApp reminders to take medicine).

---

## 📱 Flutter Implementation Plan

1.  **PrescriptionScreen Widget:**
    *   **Text Field** for Diagnosis.
    *   **ListView** of `MedicineRow` widgets.
    *   **Add Medicine Button**: Opens a `SearchMedicineSheet` (hits `/products/search`).
    *   **Submit Button**: Calls `/submit-and-automate`.

2.  **State Management:**
    *   Maintain a list of `MedicineItem` objects.
    *   When a user selects from Search, populate the `shopify_variant_id` (Crucial for the "Buy Now" link to work).

3.  **Success Handling:**
    *   After `200 OK` from submit, show a "Success Animation".
    *   Show a toast: "Prescription sent to Patient via WhatsApp!".
    *   Navigate back to Dashboard.
