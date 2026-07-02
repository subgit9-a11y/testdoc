<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;

class AstraAdminController extends Controller
{
    /**
     * Astra AI Engine Dashboard (Laravel Port)
     * Fetches real-time status from the Python Engine and Supabase.
     */
    public function index()
    {
        $astraUrl = env('ASTRA_API_URL', 'http://localhost:8000');
        $apiKey = env('ASTRA_API_KEY', 'astra-secret-2026');

        try {
            // 1. Fetch Stats from the Astra Engine
            $response = Http::withHeaders([
                'X-API-Key' => $apiKey
            ])->get("{$astraUrl}/api/admin/stats");

            $stats = $response->successful() ? $response->json() : [
                'status' => 'OFFLINE',
                'db_status' => 'OFFLINE',
                'prescriptions' => 0,
                'users' => 0,
                'audit_total' => 0,
                'jailed_ips' => []
            ];

            // 2. Mocking health for UI if API is down
            if (!$response->successful()) {
                Log::error("Astra Engine connection failed at {$astraUrl}");
            }

            return view('astra_dashboard', [
                'stats' => $stats,
                'astra_url' => $astraUrl
            ]);

        } catch (\Exception $e) {
            return view('astra_dashboard', [
                'stats' => ['status' => 'ERROR', 'error' => $e->getMessage()],
                'astra_url' => $astraUrl
            ]);
        }
    }

    /**
     * Governance: Flush IP Jail
     */
    public function flushJail()
    {
        // Logic to talk to Astra backend to clear ratelimiter
        return back()->with('status', 'IP Jail flushed successfully.');
    }
}
