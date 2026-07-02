# 🚀 Astra Admin Panel: cPanel Deployment Guide

This package contains the standalone Admin Control Center for governing the Astra AI Engine. It is set up to run as a **FastAPI** application on any cPanel host that supports Python (via Phusion Passenger).

## 📁 Package Contents
- `/app/admin`: The dashboard and UI routes.
- `/app/auth_middleware`: Security and Rate-Limiter logic.
- `/app/database`: Supabase connection manager.
- `requirements.txt`: Necessary library dependencies.
- `.env`: (Modify this with your actual database and API keys).

## 🛠️ cPanel Step-by-Step Installation:

1. **Upload Files**:
   - Upload the entire `AdminPanel_Hostable` directory to your cPanel's `public_html/admin` or a separate folder.

2. **Create Python App**:
   - Go to cPanel -> **Setup Python App**.
   - Click **Create Application**.
   - **Python Version**: Select 3.9 or higher.
   - **Application Root**: e.g., `admin_astra`.
   - **Application URL**: e.g., `yourdomain.com/admin`.
   - **Application Startup File**: `app/main.py`.
   - **Application Entry Point**: `app`.

3. **Install Dependencies**:
   - Scroll down to "Configuration files" and enter `requirements.txt`.
   - Click **Run Pip Install**.

4. **Environment Variables**:
   - Ensure the `.env` file is in the root and contains your `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `WASABI_ACCESS_KEY`, etc.
   - Set `ASTRA_API_KEY` for secure dashboard access if needed.

5. **Restart**:
   - Click **Restart Application** in the Python Setup.

## 🔗 Access URL:
Once started, you can visit:
**`https://yourdomain.com/admin/dashboard`**

### 🛡️ Security Note:
The dashboard is currently "Public" for your ease of first access. I recommend that you set an .htaccess password or a custom login in `app/admin/dashboard.py` once it is live.

---
**Astra AI System Governance - Powered by Ayureze**
