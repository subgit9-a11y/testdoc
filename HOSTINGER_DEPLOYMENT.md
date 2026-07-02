# 🚀 HOSTINGER VPS DEPLOYMENT GUIDE

## ✅ DEPLOYMENT READINESS CHECK

| Component | Status | Notes |
|-----------|--------|-------|
| Dockerfile | ✅ Ready | Multi-stage build, CPU-only |
| docker-compose.yml | ✅ Ready | Backend + Nginx |
| requirements.txt | ✅ Ready | All dependencies listed |
| main.py | ✅ Ready | Non-blocking startup |
| .env.example | ✅ Ready | Template provided |
| Health checks | ✅ Ready | /health, /health/live, /health/ready |
| TTS (Voice) | ✅ Ready | edge-tts (FREE, no API key) |
| STT (Speech) | ✅ Ready | Whisper (local model) |
| AI Brain | ✅ Ready | Uses api.ayureze.in (external) |

---

## 📋 HOSTINGER VPS REQUIREMENTS

### Minimum Specs (Recommended)
| Resource | Minimum | Recommended |
|----------|---------|-------------|
| **RAM** | 4 GB | 8 GB |
| **CPU** | 2 vCPUs | 4 vCPUs |
| **Storage** | 40 GB SSD | 80 GB SSD |
| **OS** | Ubuntu 22.04 | Ubuntu 22.04 LTS |

### Why These Specs?
- **RAM**: Whisper model (~1GB) + SentenceTransformer (~500MB) + App overhead
- **CPU**: ML inference is CPU-intensive on non-GPU VPS
- **Storage**: Docker images + model caches + logs

---

## 🔧 STEP-BY-STEP DEPLOYMENT

### Step 1: Connect to Your Hostinger VPS

```bash
ssh root@your-vps-ip
```

### Step 2: Update System & Install Docker

```bash
# Update packages
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
apt install docker-compose-plugin -y

# Verify installation
docker --version
docker compose version
```

### Step 3: Create Application Directory

```bash
mkdir -p /opt/astra
cd /opt/astra
```

### Step 4: Upload Your Code

**Option A: Using SCP from your local machine**
```bash
# From your Windows machine (PowerShell)
scp -r C:\Users\SUBHASH\Desktop\vultr_astra_2\* root@your-vps-ip:/opt/astra/
```

**Option B: Using Git**
```bash
# If you have a Git repository
git clone https://your-repo-url.git /opt/astra
```

### Step 5: Create .env File

```bash
cd /opt/astra
cp .env.example .env
nano .env  # Edit with your actual values
```

**Required Environment Variables:**
```env
# Core
ENV=production
SESSION_SECRET=your-secret-key
DATA_ENCRYPTION_KEY=your-encryption-key

# Auth0
AUTH0_DOMAIN=your-auth0-domain
AUTH0_AUDIENCE=your-audience
AUTH0_CLIENT_ID=your-client-id
AUTH0_CLIENT_SECRET=your-client-secret

# Database
DATABASE_URL=mysql+pymysql://user:pass@host:3306/db

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key

# Shopify
SHOPIFY_SHOP_URL=your-shop.myshopify.com
SHOPIFY_ACCESS_TOKEN=your-token

# WhatsApp (Optional)
CUSTOM_WA_API_BASE_URL=https://whatsapp.ayureze.in/api
CUSTOM_WA_BEARER_TOKEN=your-token

# HuggingFace (for model downloads)
HF_TOKEN=your-hf-token

# Voice (Optional - edge-tts works without API key)
ELEVENLABS_API_KEY=optional-for-premium-voice
```

### Step 6: Create Nginx Configuration

```bash
nano /opt/astra/nginx.conf
```

```nginx
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:5000;
    }

    server {
        listen 80;
        server_name your-domain.com;
        
        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
        }
        
        location / {
            return 301 https://$host$request_uri;
        }
    }

    server {
        listen 443 ssl;
        server_name your-domain.com;
        
        ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
        
        location / {
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_connect_timeout 120s;
            proxy_send_timeout 120s;
            proxy_read_timeout 120s;
        }
    }
}
```

### Step 7: Get SSL Certificate (Let's Encrypt)

```bash
# Install certbot
apt install certbot -y

# Get certificate (stop any service on port 80 first)
certbot certonly --standalone -d your-domain.com

# Certificate will be at:
# /etc/letsencrypt/live/your-domain.com/fullchain.pem
# /etc/letsencrypt/live/your-domain.com/privkey.pem
```

### Step 8: Build and Start

```bash
cd /opt/astra

# Build the Docker image (this takes 5-10 minutes)
docker compose build

# Start the services
docker compose up -d

# Check logs
docker compose logs -f backend
```

### Step 9: Verify Deployment

```bash
# Check if container is running
docker ps

# Test health endpoint (should respond immediately)
curl http://localhost:5000/health

# Test with your domain
curl https://your-domain.com/health
```

---

## 🔍 HEALTH CHECK ENDPOINTS

| Endpoint | Purpose | Expected Response |
|----------|---------|-------------------|
| `GET /health` | Full status with model loading | JSON with model status |
| `GET /health/live` | Liveness probe | `{"status": "alive"}` |
| `GET /health/ready` | Readiness probe | 200 when all models loaded |

**Example Response:**
```json
{
  "status": "ok",
  "uptime_seconds": 125.3,
  "api_ready": true,
  "pipeline_ready": true,
  "models": {
    "embeddings": {"status": "ready", "load_time_ms": 3456.7},
    "whisper": {"status": "loading", "load_time_ms": 0},
    "google_speech": {"status": "disabled"},
    "indictrans2": {"status": "not_started"}
  },
  "all_models_ready": false,
  "ai_connected": true
}
```

---

## ⚠️ IMPORTANT NOTES FOR HOSTINGER

### 1. First Startup Takes Time
- **Whisper model download**: ~500MB (first time only)
- **SentenceTransformer download**: ~100MB (first time only)
- API responds immediately, but full functionality after 1-2 minutes

### 2. Model Caching
Models are cached in `/app/.cache/huggingface`. To persist between restarts:
```yaml
# Add to docker-compose.yml volumes:
- ./model_cache:/app/.cache
```

### 3. Memory Optimization (for 4GB VPS)
If running on 4GB RAM, consider:
```bash
# Increase swap
fallocate -l 4G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo '/swapfile none swap sw 0 0' >> /etc/fstab
```

### 4. Domain Configuration
Point your domain's A record to your Hostinger VPS IP address.

### 5. Firewall
```bash
# Allow necessary ports
ufw allow 22    # SSH
ufw allow 80    # HTTP
ufw allow 443   # HTTPS
ufw allow 5000  # Backend (if direct access needed)
ufw enable
```

---

## 🚨 TROUBLESHOOTING

### Container Won't Start
```bash
# Check logs
docker compose logs backend

# Check container status
docker ps -a

# Restart
docker compose restart backend
```

### Out of Memory
```bash
# Check memory usage
free -h

# If low, add swap (see above)
# Or upgrade VPS plan
```

### Models Not Loading
```bash
# Check model registry status
curl http://localhost:5000/health

# Models should show "loading" then "ready"
# If stuck, check HF_TOKEN in .env
```

### SSL Certificate Issues
```bash
# Renew certificate
certbot renew

# Check certificate status
certbot certificates
```

---

## 📊 MONITORING

### View Logs
```bash
# Real-time logs
docker compose logs -f backend

# Last 100 lines
docker compose logs --tail=100 backend
```

### Resource Usage
```bash
# Docker stats
docker stats

# System resources
htop
```

---

## ✅ DEPLOYMENT CHECKLIST

- [ ] VPS has at least 4GB RAM
- [ ] Docker & Docker Compose installed
- [ ] Code uploaded to /opt/astra
- [ ] .env file configured
- [ ] SSL certificate obtained
- [ ] nginx.conf configured
- [ ] docker compose build successful
- [ ] docker compose up -d running
- [ ] /health endpoint responding
- [ ] Domain pointing to VPS IP
- [ ] HTTPS working

---

## 🎉 SUCCESS INDICATORS

1. `curl https://your-domain.com/health` returns JSON
2. `curl https://your-domain.com/health/live` returns `{"status": "alive"}`
3. Models show "ready" status in /health response
4. No errors in `docker compose logs backend`

---

**Your Astra backend is ready for Hostinger VPS deployment!** 🚀
