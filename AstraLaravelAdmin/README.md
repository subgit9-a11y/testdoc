# 🚀 Astra AI Dashboard: Laravel Integration Guide

This package allows you to govern your Astra AI Engine directly from your existing Laravel application. It communicates with the Python-based AI Engine via secure API calls.

## 📁 Package Contents
- `app/Http/Controllers/AstraAdminController.php`: Handles API communication with Astra.
- `resources/views/astra_dashboard.blade.php`: The premium Blade template for governance.
- `routes/astra_admin.php`: Unified routes for the dashboard.

## 🛠️ Step-by-Step Integration:

1. **Copy Files**:
   - Copy `AstraAdminController.php` to your Laravel `app/Http/Controllers/` directory.
   - Copy `astra_dashboard.blade.php` to your `resources/views/` directory.
   - (Optional) Copy/Merge the contents of `routes/astra_admin.php` into your Laravel `web.php` or `api.php`.

2. **Configure Environment (`.env`)**:
   Add the following variables to your Laravel `.env` file:
   ```env
   # The URL where your Python AI Engine is running
   ASTRA_API_URL=http://localhost:8000
   
   # The secret key for clinical/admin actions
   ASTRA_API_KEY=astra-secret-2026
   ```

3. **Protection (Middleware)**:
   In `routes/astra_admin.php`, wrap the dashboard routes in your Laravel `auth` middleware for production:
   ```php
   Route::middleware(['auth', 'can:admin'])->prefix('admin/astra')->group(function () {
       // ... routes ...
   });
   ```

4. **Namespace Check**:
   Ensure `AstraAdminController.php` matches your Laravel app namespace (default is `App\Http\Controllers`).

## 🔗 Governance URL:
Once integrated, visit:
**`https://your-laravel-domain.com/admin/astra/dashboard`**

---
**Astra AI Governance System - Scalpel-Ready for Ayureze**
