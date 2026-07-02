-- ============================================================================
-- ASTRA AI - EARNINGS & PHARMACY INTELLIGENCE MIGRATION
-- ============================================================================

-- 1. DOCTOR WALLETS & EARNINGS
CREATE TABLE IF NOT EXISTS public.doctor_wallets (
    doctor_id TEXT PRIMARY KEY REFERENCES public.doctors(doctor_id) ON DELETE CASCADE,
    total_earned BIGINT DEFAULT 0, -- Total before commission
    available_balance BIGINT DEFAULT 0, -- Net amount (70% share) available to withdraw
    withdrawn_amount BIGINT DEFAULT 0, -- Total amount already transferred
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

CREATE TABLE IF NOT EXISTS public.withdrawal_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    doctor_id TEXT NOT NULL REFERENCES public.doctors(doctor_id),
    amount BIGINT NOT NULL, -- Total gross amount requested
    admin_commission_30 BIGINT NOT NULL, -- 30% cut
    doctor_payout_70 BIGINT NOT NULL, -- 70% share
    status TEXT DEFAULT 'pending', -- pending, approved, rejected, transferred
    transaction_id TEXT, -- Razorpay Payout ID or Bank Auth ID
    requested_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- Update consultations for payment tracking
ALTER TABLE public.consultations 
ADD COLUMN IF NOT EXISTS payment_status TEXT DEFAULT 'unpaid',
ADD COLUMN IF NOT EXISTS payment_id TEXT,
ADD COLUMN IF NOT EXISTS total_fee INTEGER DEFAULT 0;

-- 2. PHARMACY INTELLIGENCE CACHE (For real-time inventory sync)
CREATE TABLE IF NOT EXISTS public.medicine_inventory_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    medicine_name TEXT UNIQUE NOT NULL,
    shopify_variant_id TEXT,
    stock_quantity INTEGER DEFAULT 0,
    is_in_stock BOOLEAN DEFAULT TRUE,
    price_cents INTEGER,
    last_synced_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

CREATE INDEX IF NOT EXISTS idx_medicine_inventory_name ON public.medicine_inventory_cache(medicine_name);
