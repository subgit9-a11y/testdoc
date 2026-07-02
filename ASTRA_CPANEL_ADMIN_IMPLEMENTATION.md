# 🛰️ Astra AI Engine: cPanel Implementation Master Guide
**Unified Deployment of Clinical AI and Admin Governance**

This document provides a comprehensive, step-by-step roadmap for technical administrators to host the Astra AI Engine and its Laravel-based Admin Governance Panel on **cPanel-based shared or private hosting**.

---

## 🏗️ Architecture Overview
*   **Astra AI Engine (Backend)**: Python (FastAPI). Runs as a "Python Application" in cPanel. Handles LLaMA inference, patient memory, and secure storage (Wasabi/Supabase).
*   **Admin Command Center (Frontend)**: PHP (Laravel). Integrated into your existing Laravel app or hosted as a new one. Displays live stats, clinical logs, and security jails.

---

## 🛠️ Phase 1: Deploying the AI Engine (Python)

### 1. Preparing the Backend
*   **Directory**: `AdminPanel_Hostable/` (This contains the core `app/` structure).
*   **Upload**: Upload this entire folder to your cPanel's home directory (e.g., `/home/username/astra_engine`).

### 2. cPanel "Setup Python App"
1.  Login to cPanel -> **Setup Python App**.
2.  Click **Create Application**.
3.  **Python Version**: Select **3.9.x** or higher.
4.  **Application Root**: `astra_engine` (Matches your folder name).
5.  **Application URL**: `yourdomain.com/api/astra` (Or any path you prefer).
6.  **Application Startup File**: `app/main.py`.
7.  **Application Entry Point**: `app`.
8.  **Configuration Files**: In the `requirements.txt` field, click **Run Pip Install**.

### 3. Environment Environment (`.env`)
Ensure your `.env` file in `/home/username/astra_engine/` contains:
```env
SUPABASE_URL=https://your-url.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-secret-key
WASABI_ACCESS_KEY=your-key
ASTRA_API_KEY=astra-secret-2026 # THIS PROTECTS THE ENGINE
```

---

## 🛠️ Phase 2: Deploying the Admin Panel (Laravel)

### 1. Integration Steps
Follow these steps within your existing Laravel project on cPanel:

1.  **Controller**: Upload `AstraAdminController.php` to `app/Http/Controllers/`.
2.  **The View**: Upload `astra_dashboard.blade.php` to `resources/views/`.
3.  **The Routes**: Add the registration snippet from `astra_admin.php` into your `routes/web.php`.

### 2. Secure Connectivity
In your Laravel project's `.env` file (usually in the root of your Laravel site), add:
```env
# Point this to the Python URL you created in Phase 1
ASTRA_API_URL=https://yourdomain.com/api/astra

# Must match the ASTRA_API_KEY in Phase 1
ASTRA_API_KEY=astra-secret-2026
```

### 3. Permissions & Security
*   **Middleware**: Ensure your `/admin/astra/dashboard` route is wrapped in the `auth` middleware:
    ```php
    Route::middleware(['auth'])->group(function () {
        Route::get('/admin/astra/dashboard', [AstraAdminController::class, 'index']);
    });
    ```

---

## 🛡️ Phase 3: Verification & Governance

### 1. Test Connectivity
*   Visit: `https://your-laravel-domain.com/admin/astra/dashboard`.
*   If the **"Database Status"** shows **ONLINE**, your Laravel app successfully "handshaked" with the Python AI Engine.

### 2. Clinical Verification
*   Check the **"EHR Prescriptions"** count. This confirms your Laravel dashboard is reading real-world data from the **Supabase / Wasabi (astraehr)** pipeline.

### 3. Security Check
*   Attempt to access `https://yourdomain.com/api/astra/v1/extract_schedule` in a browser.
*   **Expected Result**: `401 Unauthorized`. This confirms the **Astra Security Fortress** is correctly protecting the clinical API.

---

## 🆘 Troubleshooting for cPanel

1.  **503 Service Unavailable (Python)**:
    *   Usually means the Python app is not running. Check "Setup Python App" in cPanel and look for stderr logs in the application root.
2.  **Laravel cURL Errors**:
    *   If Laravel cannot reach the Python engine, ensure there is no firewall (like CSF or ModSecurity) blocking internal loopback requests from PHP to Python on the same server.
3.  **Missing Requirements**:
    *   If `pip install` fails, ensure your cPanel server has `gcc` and `python-devel` installed (contact your host if shared).

---
**Astra AI Governance System | 🛰️ Complete Implementation Ready**
