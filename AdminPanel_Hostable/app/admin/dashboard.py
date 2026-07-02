from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os
import time
import logging
from datetime import datetime, timedelta
from app.database import db_manager
from app.auth_middleware import rate_limiter # To show jailed IPs

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin", tags=["Astra Admin UI"])

# 1. Dashboard Service Logic
async def get_dashboard_data():
    """Gather all components for the Admin View"""
    now = datetime.now()
    
    # Database Status
    db_status = "ONLINE" if db_manager.is_connected() else "OFFLINE"
    
    # Counts
    user_count = 0
    presc_count = 0
    audit_count = 0
    
    if db_manager.client:
        try:
            # Stats (using head for performance)
            res_u = db_manager.client.table("user_accounts").select("*", count="exact").limit(0).execute()
            user_count = res_u.count or 0
            
            res_p = db_manager.client.table("prescription_records").select("*", count="exact").limit(0).execute()
            presc_count = res_p.count or 0
            
            res_a = db_manager.client.table("audit_logs").select("*", count="exact").limit(0).execute()
            audit_count = res_a.count or 0
        except: pass

    # Security Jail
    jailed_ips = list(rate_limiter.jail_list.keys())
    
    # External Services Health (Simulated/Status)
    health = {
        "AI Brain": "🟢 STABLE",
        "Wasabi": "🟢 READY (astraehr)",
        "Shopify": "🟢 CONNECTED",
        "Supabase": "🟢 SYNCED"
    }

    return {
        "db_status": db_status,
        "users": user_count,
        "prescriptions": presc_count,
        "audit_total": audit_count,
        "jailed_ips": jailed_ips,
        "health": health,
        "uptime": "99.98%",
        "last_refresh": now.strftime("%H:%M:%S")
    }

# 2. UI Template (Premium Astra Aesthetics)
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Astra AI | Global Admin Command</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --bg: #0b0f19;
            --sidebar-bg: #111827;
            --card-bg: #1f2937;
            --accent: #10b981;
            --accent-glow: rgba(16, 185, 129, 0.15);
            --danger: #ef4444;
            --text-main: #f9fafb;
            --text-dim: #9ca3af;
            --border: rgba(255, 255, 255, 0.05);
            --glass: rgba(31, 41, 55, 0.8);
        }

        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Outfit', sans-serif;
            background-color: var(--bg);
            color: var(--text-main);
            display: flex;
            min-height: 100vh;
        }

        /* Sidebar Navigation */
        .sidebar {
            width: 280px;
            background: var(--sidebar-bg);
            border-right: 1px solid var(--border);
            padding: 2rem 1.5rem;
            display: flex;
            flex-direction: column;
            gap: 2rem;
            position: fixed;
            height: 100vh;
        }

        .logo {
            font-size: 1.5rem;
            font-weight: 800;
            display: flex;
            align-items: center;
            gap: 12px;
            color: var(--text-main);
            text-decoration: none;
        }
        .logo span { color: var(--accent); }

        .nav-list { list-style: none; }
        .nav-item {
            padding: 0.8rem 1rem;
            border-radius: 12px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 12px;
            color: var(--text-dim);
            transition: all 0.3s;
            margin-bottom: 0.5rem;
        }
        .nav-item:hover { background: rgba(255,255,255,0.03); color: var(--text-main); }
        .nav-item.active { background: var(--accent-glow); color: var(--accent); font-weight: 600; }

        /* Main Content */
        .main {
            margin-left: 280px;
            flex: 1;
            padding: 2rem 3rem;
            max-width: 1600px;
        }

        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2.5rem;
        }

        .header-title h1 { font-size: 1.8rem; font-weight: 700; margin-bottom: 4px; }
        .header-title p { color: var(--text-dim); font-size: 0.9rem; }

        .status-badge {
            background: var(--glass);
            padding: 0.5rem 1rem;
            border-radius: 99px;
            border: 1px solid var(--accent);
            color: var(--accent);
            font-size: 0.8rem;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        /* Tab Content */
        .tab-content { display: none; animation: fadeIn 0.4s ease-out; }
        .tab-content.active { display: block; }

        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

        /* Stats Grid */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2.5rem;
        }

        .stat-card {
            background: var(--card-bg);
            padding: 1.5rem;
            border-radius: 20px;
            border: 1px solid var(--border);
        }
        .stat-label { color: var(--text-dim); font-size: 0.85rem; margin-bottom: 8px; }
        .stat-value { font-size: 2rem; font-weight: 700; }

        /* Tables & Lists */
        .card {
            background: var(--card-bg);
            border-radius: 20px;
            padding: 1.5rem;
            border: 1px solid var(--border);
            margin-bottom: 2rem;
            overflow: hidden;
        }
        .card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; }
        
        table { width: 100%; border-collapse: collapse; }
        th { text-align: left; padding: 1rem; color: var(--text-dim); font-size: 0.8rem; font-weight: 600; border-bottom: 1px solid var(--border); }
        td { padding: 1rem; border-bottom: 1px solid var(--border); font-size: 0.9rem; }
        tr:last-child td { border: none; }

        .btn {
            padding: 0.5rem 1rem;
            border-radius: 8px;
            border: none;
            font-weight: 600;
            cursor: pointer;
            font-size: 0.85rem;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            transition: opacity 0.2s;
        }
        .btn-primary { background: var(--accent); color: var(--bg); }
        .btn-outline { background: transparent; border: 1px solid var(--border); color: var(--text-main); }
        .btn-danger { background: var(--danger); color: white; }

        /* Inputs */
        .form-group { margin-bottom: 1.5rem; }
        label { display: block; font-size: 0.85rem; color: var(--text-dim); margin-bottom: 6px; }
        input, select {
            width: 100%;
            background: #111827;
            border: 1px solid var(--border);
            padding: 0.8rem 1rem;
            border-radius: 10px;
            color: var(--text-main);
            font-family: inherit;
        }

        /* Commission Preview */
        .com-split {
            display: flex; gap: 8px; font-weight: 700; font-size: 0.8rem;
        }
        .com-admin { color: var(--danger); }
        .com-doctor { color: var(--accent); }

    </style>
</head>
<body>
    <div class="sidebar">
        <a href="#" class="logo">ASTRA<span>CORE</span></a>
        
        <nav class="nav-list">
            <div class="nav-item active" onclick="showTab('overview')"><i class="fas fa-chart-line"></i> Overview</div>
            <div class="nav-item" onclick="showTab('doctors')"><i class="fas fa-user-doctor"></i> Doctors</div>
            <div class="nav-item" onclick="showTab('payouts')"><i class="fas fa-wallet"></i> Financials</div>
            <div class="nav-item" onclick="showTab('users')"><i class="fas fa-users"></i> User Accounts</div>
            <div class="nav-item" onclick="showTab('config')"><i class="fas fa-cog"></i> System Config</div>
        </nav>

        <div style="margin-top:auto; padding: 1rem; background: rgba(0,0,0,0.2); border-radius: 12px;">
            <p style="font-size: 0.7rem; color: var(--text-dim);">SYSTEM MODE</p>
            <p style="font-size: 0.8rem; font-weight: 700; color: var(--accent);">PRODUCTION ENFORCED</p>
        </div>
    </div>

    <div class="main">
        <header>
            <div class="header-title">
                <h1 id="tab-title">System Overview</h1>
                <p id="tab-subtitle">Real-time Astra AI Infrastructure Monitoring</p>
            </div>
            <div class="status-badge">
                <i class="fas fa-shield-halved"></i> 🛡️ ASTRA SECURITY FORTRESS ONLINE
            </div>
        </header>

        <!-- TAB: OVERVIEW -->
        <div id="overview" class="tab-content active">
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-label">Total Users</div>
                    <div class="stat-value" id="stat-users">-</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Active Doctors</div>
                    <div class="stat-value" id="stat-doctors" style="color: var(--accent);">-</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Daily Consultations</div>
                    <div class="stat-value" id="stat-sessions">-</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">DB Sync Rate</div>
                    <div class="stat-value" style="color: var(--accent);">99.9%</div>
                </div>
            </div>

            <div class="card">
                <div class="card-header">
                    <h2>Governance Health</h2>
                    <button class="btn btn-outline" onclick="loadStats()"><i class="fas fa-sync"></i> Refresh</button>
                </div>
                <table id="health-table">
                    <thead><tr><th>SERVICE</th><th>ENDPOINT</th><th>STATUS</th></tr></thead>
                    <tbody>
                        <tr><td>Astra AI Engine</td><td>api.ayureze.in</td><td><span style="color:var(--accent);">● OPERATIONAL</span></td></tr>
                        <tr><td>Supabase DB</td><td>supabase.co</td><td><span style="color:var(--accent);">● CONNECTED</span></td></tr>
                        <tr><td>Wasabi Storage</td><td>s3.wasabisys.com</td><td><span style="color:var(--accent);">● READY</span></td></tr>
                        <tr><td>Firebase Auth</td><td>firebase.google.com</td><td><span style="color:var(--accent);">● ACTIVE</span></td></tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- TAB: DOCTORS -->
        <div id="doctors" class="tab-content">
            <div class="card">
                <div class="card-header">
                    <h2>Doctor Directory</h2>
                    <button class="btn btn-primary" onclick="loadDoctors()">Load Doctors</button>
                </div>
                <table id="doctor-table">
                    <thead><tr><th>DOCTOR</th><th>SPECIALIZATION</th><th>WALLET BAL</th><th>STATUS</th><th>ACTIONS</th></tr></thead>
                    <tbody id="doctor-list"></tbody>
                </table>
            </div>
        </div>

        <!-- TAB: PAYOUTS -->
        <div id="payouts" class="tab-content">
            <div class="card">
                <div class="card-header">
                    <h2>Revenue Distribution (30/70)</h2>
                    <p style="font-size: 0.8rem; color: var(--text-dim);">Commision split enforced by Astra Financial Guard</p>
                </div>
                <table id="payout-table">
                    <thead><tr><th>ID</th><th>DOCTOR</th><th>AMOUNT</th><th>SPLIT (Admin/Doc)</th><th>STATUS</th><th>ACTIONS</th></tr></thead>
                    <tbody id="payout-list"></tbody>
                </table>
            </div>
        </div>

        <!-- TAB: USERS -->
        <div id="users" class="tab-content">
            <div class="card">
                <div class="card-header">
                    <h2>Astra User Registry</h2>
                    <button class="btn btn-outline" onclick="loadUsers()">Sync Firebase</button>
                </div>
                <table id="user-table">
                    <thead><tr><th>UID</th><th>EMAIL</th><th>NAME</th><th>JOINED</th></tr></thead>
                    <tbody id="user-list"></tbody>
                </table>
            </div>
        </div>

        <!-- TAB: CONFIG -->
        <div id="config" class="tab-content">
            <div class="stats-grid">
                <div class="card">
                    <h3>Astra AI Pipeline</h3>
                    <div class="form-group" style="margin-top: 1rem;">
                        <label>Base Model</label>
                        <input type="text" id="cfg-base-model" value="Llama-3-8B-Instruct">
                    </div>
                    <div class="form-group">
                        <label>LoRA Adapter</label>
                        <input type="text" id="cfg-lora-model" value="astra-clinical-v4">
                    </div>
                    <button class="btn btn-primary">Deploy Configuration</button>
                </div>
                <div class="card">
                    <h3>Wasabi Cloud S3</h3>
                    <div class="form-group" style="margin-top: 1rem;">
                        <label>Bucket Name</label>
                        <input type="text" id="cfg-wasabi-bucket" value="astraehr">
                    </div>
                    <div class="form-group">
                        <label>Endpoint</label>
                        <input type="text" id="cfg-wasabi-endpoint" value="s3.wasabisys.com">
                    </div>
                    <button class="btn btn-primary w-full shadow-lg">Save Storage Settings</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        async function fetchAPI(endpoint) {
            const res = await fetch('/api/admin' + endpoint);
            return res.json();
        }

        async function loadStats() {
            const data = await fetchAPI('/stats');
            document.getElementById('stat-users').innerText = data.total_users;
            document.getElementById('stat-doctors').innerText = data.total_doctors;
            document.getElementById('stat-sessions').innerText = data.active_sessions;
        }

        async function loadDoctors() {
            const data = await fetchAPI('/doctors');
            const list = document.getElementById('doctor-list');
            list.innerHTML = data.map(doc => `
                <tr>
                    <td><strong>${doc.name}</strong><br><small style="color:var(--text-dim)">${doc.doctor_id}</small></td>
                    <td>${doc.specialization}</td>
                    <td>INR ${doc.doctor_wallets ? doc.doctor_wallets[0].available_balance : 0}</td>
                    <td><span style="color:${doc.is_active ? 'var(--accent)' : 'var(--danger)'}">${doc.is_active ? 'ACTIVE' : 'INACTIVE'}</span></td>
                    <td><button class="btn btn-outline btn-sm" onclick="toggleDoctor('${doc.doctor_id}', ${!doc.is_active})">Toggle</button></td>
                </tr>
            `).join('');
        }

        async function loadPayouts() {
            const data = await fetchAPI('/payouts');
            const list = document.getElementById('payout-list');
            list.innerHTML = data.map(p => `
                <tr>
                    <td>#${p.id.slice(0,8)}</td>
                    <td>${p.doctors.name}</td>
                    <td>INR ${p.amount}</td>
                    <td>
                        <div class="com-split">
                            <span class="com-admin">30%: ${p.admin_commission_30}</span>
                            <span class="com-doctor">70%: ${p.doctor_payout_70}</span>
                        </div>
                    </td>
                    <td><span class="btn ${p.status === 'completed' ? 'btn-primary' : 'btn-outline'}" style="padding:2px 8px; font-size:10px">${p.status.toUpperCase()}</span></td>
                    <td>
                        ${p.status === 'pending' ? `<button class="btn btn-primary" onclick="approvePayout('${p.id}')">Process Payout</button>` : '---'}
                    </td>
                </tr>
            `).join('');
        }

        async function loadUsers() {
            const data = await fetchAPI('/users');
            const list = document.getElementById('user-list');
            list.innerHTML = data.map(u => `
                <tr>
                    <td><code>${u.id.slice(0,12)}...</code></td>
                    <td>${u.email}</td>
                    <td>${u.name || '---'}</td>
                    <td>${new Date(u.created_at).toLocaleDateString()}</td>
                </tr>
            `).join('');
        }

        async function toggleDoctor(id, status) {
            await fetch(`/api/admin/doctors/${id}/toggle-status?active=${status}`, {method: 'POST'});
            loadDoctors();
        }

        async function approvePayout(id) {
            if(confirm("Process this 30/70 Split Payout?")) {
                await fetch(`/api/admin/payouts/${id}/approve`, {method: 'POST'});
                loadPayouts();
            }
        }

        function showTab(tabId) {
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
            
            document.getElementById(tabId).classList.add('active');
            event.currentTarget.classList.add('active');
            
            const titles = {
                'overview': 'System Overview',
                'doctors': 'Doctor Governance',
                'payouts': 'Financial Ecosystem',
                'users': 'User Management',
                'config': 'Unified Configuration'
            };
            document.getElementById('tab-title').innerText = titles[tabId];

            if(tabId === 'overview') loadStats();
            if(tabId === 'doctors') loadDoctors();
            if(tabId === 'payouts') loadPayouts();
            if(tabId === 'users') loadUsers();
        }

        // Init
        loadStats();
    </script>
</body>
</html>
"""

@router.get("/dashboard", response_class=HTMLResponse)
async def admin_dashboard():
    """Renders the Unified Astra Admin Command Center"""
    return DASHBOARD_HTML
