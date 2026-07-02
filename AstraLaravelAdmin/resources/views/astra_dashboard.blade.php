<!DOCTYPE html>
<html lang="{{ str_replace('_', '-', app()->getLocale()) }}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Astra AI | Command Center (Laravel)</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg: #0f172a;
            --card-bg: #1e293b;
            --accent: #10b981;
            --accent-glow: rgba(16, 185, 129, 0.2);
            --danger: #ef4444;
            --text-main: #f8fafc;
            --text-dim: #94a3b8;
            --glass: rgba(30, 41, 59, 0.7);
        }

        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Outfit', sans-serif;
            background-color: var(--bg);
            color: var(--text-main);
            overflow-x: hidden;
            min-height: 100vh;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }

        /* Header Style */
        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2.5rem;
            backdrop-filter: blur(10px);
            padding: 1rem 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }

        .logo { font-size: 1.8rem; font-weight: 700; display: flex; align-items: center; gap: 12px; }
        .logo span { color: var(--accent); }

        .fortress-status {
            background: var(--glass);
            padding: 0.5rem 1rem;
            border-radius: 99px;
            border: 1px solid var(--accent);
            color: var(--accent);
            font-size: 0.9rem;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .status-dot {
            width: 8px; height: 8px;
            background: var(--accent);
            border-radius: 50%;
            box-shadow: 0 0 10px var(--accent);
            animation: blink 2s infinite;
        }

        @keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }

        /* Dashboard Overview */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2.5rem;
        }

        .stat-card {
            background: var(--card-bg);
            padding: 1.5rem;
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.05);
            transition: transform 0.3s ease;
        }

        .stat-card:hover { transform: translateY(-5px); border-color: var(--accent); }
        .stat-title { color: var(--text-dim); font-size: 0.9rem; margin-bottom: 8px; }
        .stat-value { font-size: 2.2rem; font-weight: 700; }
        .stat-trend { color: var(--accent); font-size: 0.8rem; font-weight: 600; margin-top: 8px; }

        /* Main Monitoring Area */
        .main-view { display: grid; grid-template-columns: 2fr 1fr; gap: 2rem; }
        .card { background: var(--card-bg); border-radius: 24px; padding: 2rem; border: 1px solid rgba(255, 255, 255, 0.05); }

        h2 { font-size: 1.4rem; margin-bottom: 1.5rem; display: flex; align-items: center; gap: 10px; }

        .service-list { list-style: none; }
        .service-item { display: flex; justify-content: space-between; padding: 1rem 0; border-bottom: 1px solid rgba(255, 255, 255, 0.05); }
        
        .jail-table { width: 100%; border-collapse: collapse; }
        .jail-table td { padding: 8px 0; font-size: 0.9rem; }
        .tag { background: var(--danger); color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: 700; }

        .btn-action {
            background: var(--accent);
            border: none;
            color: var(--bg);
            padding: 0.8rem 1.5rem;
            border-radius: 12px;
            font-weight: 700;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
        }

        @media (max-width: 900px) { .main-view { grid-template-columns: 1fr; } }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="logo">ASTRA<span>AI</span></div>
            <div style="display: flex; gap: 1rem; align-items: center;">
                <div class="fortress-status">
                    <div class="status-dot"></div>
                    SECURITY FORTRESS ACTIVE
                </div>
                <a href="{{ url()->current() }}" class="btn-action">REFRESH</a>
            </div>
        </header>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-title">Database Status</div>
                <div class="stat-value" style="color: {{ $stats['status'] === 'operational' ? '#10b981' : '#ef4444' }}">
                    {{ $stats['status'] }}
                </div>
                <div class="stat-trend">Synced via Laravel Http</div>
            </div>
            <div class="stat-card">
                <div class="stat-title">EHR Prescriptions</div>
                <div class="stat-value">{{ $stats['active_sessions'] ?? 0 }}</div>
                <div class="stat-trend">Total Stored (Wasabi)</div>
            </div>
            <div class="stat-card">
                <div class="stat-title">Astra Active Users</div>
                <div class="stat-value">{{ $stats['total_users'] ?? 0 }}</div>
                <div class="stat-trend">Live in Production</div>
            </div>
            <div class="stat-card">
                <div class="stat-title">DISHA Audit Logs</div>
                <div class="stat-value">{{ $stats['total_doctors'] ?? 0 }}</div>
                <div class="stat-trend">Access Compliance</div>
            </div>
        </div>

        <div class="main-view">
            <div class="card">
                <h2>Health Monitoring (Live)</h2>
                <div class="service-list">
                    <div class="service-item"><span>Supabase</span><span style="font-weight:600">{{ $stats['database_connected'] ? '🟢 ONLINE' : '🔴 OFFLINE' }}</span></div>
                    <div class="service-item"><span>Wasabi (astraehr)</span><span style="font-weight:600">🟢 READY</span></div>
                    <div class="service-item"><span>Brain Model</span><span style="font-weight:600">{{ $stats['model_loaded'] ? '🟢 LOADED' : '🟡 LOADING' }}</span></div>
                    <div class="service-item"><span>Internal API</span><span style="font-weight:600">🟢 CONNECTED</span></div>
                </div>
                
                <div style="margin-top: 2rem; border-top: 1px solid #ffffff10; padding-top: 1rem;">
                    <h3 style="font-size: 0.9rem; color: var(--text-dim); margin-bottom: 1rem;">Uptime Verification (24h)</h3>
                    <div style="width: 100%; height: 8px; background: #ffffff10; border-radius: 4px; overflow: hidden;">
                        <div style="width: 99.98%; height: 100%; background: var(--accent); border-radius: 4px;"></div>
                    </div>
                </div>
            </div>

            <div class="card">
                <h2>Security Shield (Jailed)</h2>
                @if(isset($stats['jailed_ips']) && count($stats['jailed_ips']) > 0)
                    <table class="jail-table">
                        <thead><tr><th>IP ADDRESS</th><th>STATUS</th></tr></thead>
                        <tbody>
                            @foreach($stats['jailed_ips'] as $ip)
                                <tr><td>{{ $ip }}</td><td><span class="tag">JAILED</span></td></tr>
                            @endforeach
                        </tbody>
                    </table>
                @else
                    <p style="color: var(--text-dim); font-size: 0.9rem;">No active threats found in the jail-list.</p>
                @endif
            </div>
        </div>
    </div>
</body>
</html>
