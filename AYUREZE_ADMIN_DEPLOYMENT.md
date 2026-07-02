# 🚀 Ayureze Super Admin Deployment Guide

This guide will walk you through packaging your locally modified `public_html Ayureze` Laravel Admin panel and deploying it to your host (Vultr server, cPanel, or Hostinger).

---

## 📦 Phase 1: Preparing the Source Code

Before zipping the files, we need to clear cached views and configurations to ensure it runs cleanly on the target server.

1. **Clear Caches**: If you have PHP installed locally, open PowerShell inside `c:\Users\SUBHASH\Music\vultr_astra_2\public_html Ayureze` and run:
   ```bash
   php artisan optimize:clear
   php artisan view:clear
   ```
2. *(Optional)* Delete the `/storage/logs/laravel.log` file so you don't upload a massive log file to your server.
3. Select everything **INSIDE** the `public_html Ayureze` folder (e.g. `app`, `bootstrap`, `public`, `vendor`, `.env.example`, etc.).
4. Right-click and **Compress to ZIP file**. Name it `ayureze_admin_update.zip`.

> **Note:** Do not include the `.env` file containing local credentials if your live server already has its own `.env` file set up! 

---

## 🌐 Phase 2: Uploading to the Host (Hostinger / cPanel)

1. Log into your **cPanel** or **Hostinger hPanel**.
2. Navigate to the **File Manager**.
3. Go directly to your domain's public root. For Hostinger, this is usually `public_html/`. 
   - *If your sub-domain (like `admin.ayureze.org`) maps to a different folder, open that specific folder.*
4. Click **Upload** and select your `ayureze_admin_update.zip`.
5. Once uploaded, right-click the zip file and **Extract**. Choose to overwrite existing files.

---

## ⚙️ Phase 3: Post-Deployment Configuration

1. Locate the `.env` file on your server. Right-click it and select **Edit**.
2. Ensure you have the new Astra API keys we developed properly populated:
   ```env
   # --- ASTRA ECOSYSTEM ---
   ASTRA_UI_URL=https://astra.ayureze.in
   ASTRA_API_URL=https://api.ayureze.in/health
   
   # --- SUPABASE (Doctor Wallet / Payouts) ---
   SUPABASE_URL=https://<your-project>.supabase.co
   SUPABASE_KEY=ey...
   
   # --- WASABI (Medical Vault) ---
   WASABI_ACCESS_KEY_ID=yr_access_key
   WASABI_SECRET_ACCESS_KEY=yr_secret_key
   WASABI_DEFAULT_REGION=us-east-1
   WASABI_BUCKET=ayureze-vault
   
   # --- SHOPIFY ---
   SHOPIFY_STORE_URL=ayureze-healthcare.myshopify.com
   SHOPIFY_TOKEN=shpat_364637...
   
   # --- FIREBASE ---
   FIREBASE_PROJECT_ID=ayurease-healthcare
   ```
3. Save the `.env` file.

---

## 🔥 Phase 4: Server Warmup

If you have SSH access (like on a **Vultr** instance):
1. Connect via SSH into your VPS.
2. Navigate to your project root `cd /var/www/ayureze_admin` (or wherever it's located)
3. Run the following commands:
   ```bash
   php artisan optimize
   php artisan route:cache
   ```
4. If this is a Hostinger Shared hosting where you don't have SSH, simply visit your website url: `https://ayureze.org/clear-cache` (our `routes/web.php` already has a fast cache-clearing route!).

**Done! The beautiful modern Astra command center UI and the massive new Ecosystem integrations are now LIVE! 🚀🌟**
