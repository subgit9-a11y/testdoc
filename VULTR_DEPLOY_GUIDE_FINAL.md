# 🚀 Final Vultr Deployment Guide - Astra AI Healthcare

This guide provides step-by-step instructions to deploy the Astra AI Healthcare backend (v2.1.0) on your Vultr instance.

---

## 🏗️ 1. Server Prerequisites
Recommended OS: **Ubuntu 22.04 LTS** or **Debian 12**.

### **Install Docker & Docker Compose**
Run these commands on your Vultr terminal:
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install -y docker-compose-v2

# Add user to docker group (optional, requires logout/login)
sudo usermod -aG docker $USER
```

---

## 📂 2. Upload and Prepare Files
1.  **Transfer the folder:** Upload the `vultr_astra/` directory to your server (via SCP, SFTP, or Git).
2.  **Navigate to the directory:**
    ```bash
    cd vultr_astra
    ```

---

## 🔑 3. Configure Credentials (.env)
Create or edit the `.env` file in the root directory. **This is the most important step.**

```bash
nano .env
```

**Fill in these mandatory values:**
```env
# Server Config
ENV=production
API_PORT=5000

# Laravel MySQL Database (For Patient/Doctor App data)
DATABASE_URL=mysql+pymysql://user:password@host:3306/dbname

# Supabase Credentials (For Astra AI Features)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key

# Firebase (For Notifications and Auth)
FIREBASE_ENABLED=true
FIREBASE_SERVICE_ACCOUNT=/app/aiastra/firebase-service-account.json

# Security
DATA_ENCRYPTION_KEY=your-32-character-secret-key

# Model (CPU Optimization)
DEVICE=cpu
HF_TOKEN=your-huggingface-token
```

---

## 🚀 4. Launch Application
Build and start the containers in "detached" (background) mode:

```bash
docker compose up -d --build
```

---

## 🛡️ 5. SSL & Nginx Setup (Optional but Recommended)
Your `docker-compose.yml` includes an Nginx proxy. If you have a domain:
1.  Point your domain to the Vultr IP.
2.  The `nginx.conf` is pre-configured to look for SSL certs in `/etc/letsencrypt`.
3.  To generate certs, run:
    ```bash
    sudo apt install certbot
    sudo certbot certonly --standalone -d yourdomain.com
    ```

---

## ✅ 6. Verification
Once the command finishes, check the status:

### **Check Running Containers**
```bash
docker ps
```
You should see `aibackend` and `aibackend_proxy` running.

### **Check Real-time Logs**
```bash
docker logs -f aibackend
```
**Look for these success messages:**
*   ✅ `[DB] Database Schema Verified`
*   ✅ `[AI] Astra Engine Online`
*   ✅ `Supabase client initialized successfully`

### **Test Endpoints**
*   **Root Health:** `http://your-ip/health`
*   **Interactive Docs:** `http://your-ip/api/docs`
*   **Full Capability List:** `http://your-ip/api/v1/astra/capabilities`

---

## 🛠️ Troubleshooting
*   **AI Model Loading:** The first startup takes 3–5 minutes while the model weights are loaded into RAM. Wait for the `Astra Engine Online` log message.
*   **Database Refusal:** If you see "Mock Mode", double-check that `SUPABASE_URL` in `.env` doesn't have a trailing slash or extra spaces.
*   **Memory Issues:** If the container crashes, ensure your Vultr plan has at least **4GB to 8GB of RAM**, as AI models are memory-intensive.

---
**Guide Version:** 2.1.0-FINAL  
**Verified by:** Antigravity AI Assistant
