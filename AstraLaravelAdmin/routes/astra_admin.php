<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\AstraAdminController;

/*
|--------------------------------------------------------------------------
| Astra AI Engine Admin Governance Routes
|--------------------------------------------------------------------------
|
| These routes handle the remote management and monitoring of the Astra AI engine.
| Use 'auth' middleware to protect this dashboard in production.
|
*/

Route::prefix('admin/astra')->group(function () {
    // 1. Live Dashboard UI
    Route::get('/dashboard', [AstraAdminController::class, 'index'])->name('astra.dashboard');

    // 2. Governance Actions
    Route::post('/flush-jail', [AstraAdminController::class, 'flushJail'])->name('astra.flush_jail');
});
