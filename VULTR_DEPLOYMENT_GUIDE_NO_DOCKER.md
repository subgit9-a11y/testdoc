# 🚀 Vultr Deployment Guide - Astra 2.0 (No-Docker Environment)

This guide details how to deploy Astra 2.0 on a raw Vultr VPS (Ubuntu 22.04 LTS or newer) without using Docker. This ensures direct hardware access, easier debugging, and avoids container-networking issues.

---

## 🏗️ 1. STT/TTS Configuration Check

**Status:**
- **Speech-to-Text (STT):** Configured to use **OpenAI Whisper (Local)** or **Google Cloud Speech**.
  - Default: **Google Cloud Speech** (higher accuracy for Indian accents).
  - Fallback: **OpenAI Whisper** (runs locally on the server).
- **Text-to-Speech (TTS):** Configured to use **ElevenLabs** (Premium) or **Google Cloud TTS**.
  - Default: **ElevenLabs** (for human-like emotional voice).

**Verification:**
The file `app/astra/voice_service.py` handles this.
- If `GOOGLE_SPEECH_AVAILABLE` is true, it uses Google.
- If `WHISPER_AVAILABLE` is true, it can use Whisper.

**To switch purely to Whisper:**
Call `VoiceService(stt_provider="whisper")` in your code (already supported).

---

## 🛠️ 2. Server Prerequisites

Provision a **Vultr Cloud Compute** instance:
- **OS:** Ubuntu 24.04 LTS x64 (recommended) or 22.04.
- **CPU:** 2 vCPU minimum (for Whisper AI inference).
- **RAM:** 4GB minimum (8GB recommended for smooth AI operations).
- **Storage:** 80GB+ SSD.

---

## ⚙️ 3. Installation Steps

### Step 1: System Update & Dependencies
SSH into your Vultr server and run:

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11+, pip, ffmpeg (required for audio/Whisper), and git
sudo apt install -y python3-pip python3-venv git ffmpeg portaudio19-dev libsndfile1

# Verify Python version
python3 --version  # Should be 3.10+
ffmpeg -version    # Should verify ffmpeg is installed
```

### Step 2: Clone & Setup Codebase
```bash
# Clone your repository (use your actual repo URL)
git clone https://github.com/your-repo/vultr_astra_1.0.git
cd vultr_astra_1.0

# Create virtual environment (isolates dependencies)
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 3: Install OpenAI Whisper (If using local STT)
```bash
pip install openai-whisper
```

### Step 4: Environment Configuration
Create the `.env` file with your production credentials:

```bash
nano .env
```

**Paste your .env content from your local machine:**
(Ensure `STORJ_ENABLED=true` and `DATABASE_URL` matches your local config, but update `DB_HOST` if needed).

```env
# ... [PASTE YOUR .ENV CONTENT HERE] ...
GOOGLE_APPLICATION_CREDENTIALS="firebase-service-account.json"
```

**Important:** Upload your `firebase-service-account.json` to the server root directory using Secure Copy (SCP) or FileZilla.

### Step 5: Process Manager Setup (Supervisor)
Use Supervisor to keep Astra running 24/7 and auto-restart on crashes.

```bash
sudo apt install -y supervisor

# Create config file
sudo nano /etc/supervisor/conf.d/astra.conf
```

**Paste the following:**
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

**Start the application:**
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start astra
```

### Step 6: Nginx Reverse Proxy (Optional but Recommended)
To serve on port 80 (HTTP) or 443 (HTTPS) instead of 8000.

```bash
sudo apt install -y nginx
sudo nano /etc/nginx/sites-available/astra
```

**Config:**
```nginx
server {
    listen 80;
    server_name your_domain_or_IP;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/astra /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 🔒 4. Post-Deployment Checks

1.  **Check Status:** `sudo supervisorctl status astra` (Should show RUNNING).
2.  **View Logs:** `tail -f /var/log/astra.out.log`.
3.  **Firewall:** Ensure port 80/443 (or 8000) is open in Vultr Firewall settings.
4.  **Database Whitelist:** **CRITICAL!** Add your Vultr Server IP to your MySQL Host's "Remote MySQL" whitelist (Hostinger/cPanel) to allow the doctor service to connect.

## 🎤 STT Provider Summary

| Feature | OpenAI Whisper (Local) | Google Cloud Speech |
| :--- | :--- | :--- |
| **Connection** | Local (Python Lib) | Remote API |
| **Accuracy** | Excellent | Excellent |
| **Speed** | Variable (CPU Dependent) | Fast |
| **Setup** | `pip install openai-whisper` | Service Account JSON |
| **Current Config** | **Supported** (Fallback) | **Default** |

Your code in `app/astra/voice_service.py` is currently configured to prioritize **Google Cloud Speech** but has full support for **Whisper** as a valid provider or fallback.

---

**Deployment is ready.** 🚀
