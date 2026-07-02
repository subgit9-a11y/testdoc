# 🚀 FINAL ERROR-FREE VULTR DEPLOYMENT GUIDE - ASTRA 2.0

**Target Environment:** Vultr Cloud Compute (VPS)
**OS:** Ubuntu 22.04 LTS or 24.04 LTS
**Method:** Bare Metal (No Docker) - *Most stable for Voice/AI apps.*

---

## 🚦 PRE-FLIGHT CHECKLIST
Before you start, ensure you have:
1.  **Vultr Server credentials** (IP Address, Root Password).
2.  **Your `.env` file content** ready to copy.
3.  **`firebase-service-account.json`** file ready to upload.
4.  **Database Hostname** (e.g., from Hostinger).

---

## 🛠️ PHASE 1: SERVER PREPARATION (The Foundation)

Login to your server via SSH:
`ssh root@<YOUR_VULTR_IP>`

### 1. Update & Install System Dependencies
Run these commands exactly. They install Python, Audio drivers (for Whisper), and build tools.

```bash
# Update package list and upgrade existing packages
sudo apt update && sudo apt upgrade -y

# Install Python 3, pip, VirtualEnv, Git, FFmpeg (Audio), and build basics
sudo apt install -y python3-pip python3-venv git ffmpeg portaudio19-dev libsndfile1 build-essential
```

### 2. Verify Installations
```bash
python3 --version  # Must be 3.10 or higher
ffmpeg -version    # Must show configuration
```

---

## 📦 PHASE 2: CODE & ENVIRONMENT SETUP

### 1. Clone Your Repository
```bash
cd /root
git clone <YOUR_GITHUB_REPO_URL> vultr_astra_1.0
cd vultr_astra_1.0
```

### 2. Create Virtual Environment
This isolates your app so system updates don't break it.
```bash
python3 -m venv venv
source venv/bin/activate
```
*(Your terminal prompt should now show `(venv)`)*

### 3. Install Python Libraries
```bash
# Upgrade pip first to avoid errors
pip install --upgrade pip

# Install project requirements
pip install -r requirements.txt

# Install Server Server (Uvicorn)
pip install uvicorn

# Install Whisper (AI Speech-to-Text)
pip install openai-whisper
```

### 4. Setup Configuration Files
**A. The `.env` file**
```bash
nano .env
```
*Paste your local `.env` content here. Save with Ctrl+O, Enter, Ctrl+X.*

**B. Upload Google Credentials**
From your **LOCAL** machine (not Vultr), run this command to upload your file:
```bash
scp path/to/firebase-service-account.json root@<YOUR_VULTR_IP>:/root/vultr_astra_1.0/
```

---

## 🚀 PHASE 3: RUNNING THE APP (24/7 Background Service)

We use **Supervisor** to keep Astra running forever. If it crashes, Supervisor restarts it instantly.

### 1. Install & Configure Supervisor
```bash
sudo apt install -y supervisor
sudo nano /etc/supervisor/conf.d/astra.conf
```

### 2. Paste Configuration
Copy this block exactly:
```ini
[program:astra]
directory=/root/vultr_astra_1.0
command=/root/vultr_astra_1.0/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
user=root
autostart=true
autorestart=true
stderr_logfile=/var/log/astra.err.log
stdout_logfile=/var/log/astra.out.log
environment=PYTHONUNBUFFERED=1
```
*Save with Ctrl+O, Enter, Ctrl+X.*

### 3. Start the Service
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start astra
```

### 4. Verify It's Running
```bash
sudo supervisorctl status astra
```
*You should see `RUNNING`.*

---

## 🌐 PHASE 4: PUBLIC ACCESS (Nginx Reverse Proxy)

This allows users to access your app via port 80 (HTTP) without typing `:8000`.

### 1. Install Nginx
```bash
sudo apt install -y nginx
```

### 2. Configure Site
```bash
sudo nano /etc/nginx/sites-available/astra
```
Paste this:
```nginx
server {
    listen 80;
    server_name _;  # Or your domain.com

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        # Increase timeout for AI Voice processing
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
    }
}
```

### 3. Enable & Restart
```bash
sudo ln -s /etc/nginx/sites-available/astra /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default  # Remove default welcome page
sudo nginx -t                             # Check for syntax errors
sudo systemctl restart nginx
```

---

## 🛡️ CRITICAL FINAL STEP: DATABASE WHITELISTING

Your Doctor Service connects to an external Laravel MySQL database. **This will FAIL** if you skip this step.

1.  Log in to your **Vultr Dashboard**.
2.  Copy your **Server IP Address**.
3.  Go to your **Database Provider** (cPanel / Hostinger / AWS RDS).
4.  Find **"Remote MySQL"** or **"Database Access"**.
5.  **Add your Vultr IP** to the whitelist.

---

## 🎉 DONE! How to Test

**API Base URL:** `http://<YOUR_VULTR_IP>`

1.  **Health Check:**
    Open browser: `http://<YOUR_VULTR_IP>/astra/health`
    *Should return: `{"status": "healthy", ...}`*

2.  **Autopilot Status:**
    `http://<YOUR_VULTR_IP>/autopilot/status/test_patient`

**Troubleshooting:**
- **App not starting?** Check logs: `tail -n 50 /var/log/astra.err.log`
- **Database Error?** You probably forgot the Whitelist step above.
- **Voice error?** Check if `ffmpeg` is installed.

**Your Astra AI Backend is now LIVE!** 🚀
