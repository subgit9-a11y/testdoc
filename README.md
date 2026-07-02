# 🚀 Astra Backend: Vultr Zero-Error Deployment

This folder contains the consolidated, optimized files for deploying the Astra Backend to a Vultr CPU-only instance.

## 📂 Folder Contents
This folder is a **self-contained** deployment package. It contains:
- `app/`, `static/`, `astra_memory/`: Core application files and assets.
- `main.py`, `main_enhanced.py`, `shopify_client.py`: Application entry points.
- `Dockerfile`: Optimized multi-stage build (CPU-only Torch).
- `docker-compose.yml`: Orchestrates Backend + Nginx Proxy.
- `nginx.conf`: SSL-ready Nginx configuration.
- `deploy.sh`: Automated bundle, upload, and deploy script.
- `.env.example`: Template for environment variables.
- `requirements.txt`: Python dependencies.

## 🛠️ Step-by-Step Deployment

### 1. Prepare Environment
Copy `.env.example` to the root directory (one level up from this folder) and fill in your actual credentials.
```bash
cp vultr_astra/.env.example .env
# Edit .env with your secrets
```

### 2. Configure Domain
Open `vultr_astra/nginx.conf` and replace `api.ayureze.in` with your actual domain or IP.

### 3. Update Deployment Script
Open `vultr_astra/deploy.sh` and set your `SERVER_IP`.

### 4. Run Deployment
From the project root directory, run:
```bash
bash vultr_astra/deploy.sh
```

## 🔐 SSL Setup (Recommended)
The `nginx.conf` is configured for Let's Encrypt. Once deployed, run this on your server:
```bash
docker run -it --rm --name certbot \
  -v "/etc/letsencrypt:/etc/letsencrypt" \
  -v "/var/www/certbot:/var/www/certbot" \
  certbot/certbot certonly --webroot -w /var/www/certbot -d yourdomain.com
```
Then restart Nginx: `docker restart aibackend_proxy`

---
**Zero Error Guarantee**: This setup uses a multi-stage Docker build to ensure Torch installs correctly on CPU instances without hanging or running out of memory.
