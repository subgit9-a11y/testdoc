# 🚀 Astra Backend Deployment Guide

Your Astra Backend code is **FULLY READY** for Vultr. All logic errors are fixed, and the automation engine is installed.

## Step 1: Create the Deployment Package
I have already created a script that bundles your code into a clean zip file, excluding junk files.

1.  **Run this command locally:**
    ```powershell
    python prepare_deployment.py
    ```
    ✅ This creates `vultr_astra_deploy.zip`.

## Step 2: Upload to Vultr
Use PowerShell (or any terminal) to send the file to your server.

**Command:**
```powershell
scp vultr_astra_deploy.zip root@<YOUR_VULTR_IP>:/root/
```
*(Replace `<YOUR_VULTR_IP>` with your actual server IP, e.g., 220.158.156.97)*

## Step 3: Deployment on Server
Log in to your server and run the update.

1.  **SSH into Server:**
    ```powershell
    ssh root@<YOUR_VULTR_IP>
    ```

2.  **Run these commands on the server:**
    ```bash
    # 1. Create directory if not exists
    mkdir -p /root/aiastra-backend
    
    # 2. Move zip there
    mv /root/vultr_astra_deploy.zip /root/aiastra-backend/
    
    # 3. Go to folder
    cd /root/aiastra-backend
    
    # 4. Unzip (install unzip if missing: apt install unzip)
    unzip -o vultr_astra_deploy.zip
    
    # 5. Build and Start Docker
    docker compose down
    docker compose up -d --build
    ```

## Step 4: Verify
After about 60 seconds, check if it's running:
```bash
docker ps
docker logs -f aibackend
```

### ⚠️ IMPORTANT: SSL Certificates
Your `nginx.conf` is configured for SSL/HTTPS (`astra.ayureze.in`). 
- **If you already have certs** on the server in standard Certbot paths, it will work immediately.
- **If this is a fresh server**, Nginx will fail to start. You must generate certs using Certbot first.

**To fix SSL if Nginx fails:**
```bash
# Stop Nginx temporarily
docker stop aibackend_proxy

# Run Certbot (install if valid)
certbot certonly --standalone -d astra.ayureze.in

# Restart
docker compose up -d
```
