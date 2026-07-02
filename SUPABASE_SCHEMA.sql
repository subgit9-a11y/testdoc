-- ============================================================================
-- ASTRA AI - SUPABASE SCHEMA (Hybrid Architecture)
-- Run this script in your Supabase SQL Editor to create the necessary tables.
-- ============================================================================

-- 1. CHAT HISTORY MANAGEMENT
-- Stores all chat sessions and messages for the Astra AI Assistant.

CREATE TABLE IF NOT EXISTS public.astra_chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL, -- Links to your User table (Firebase UID or Auth0 ID)
    language TEXT DEFAULT 'en',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Index for fast lookup by user
CREATE INDEX IF NOT EXISTS idx_chat_sessions_user ON public.astra_chat_sessions(user_id);

CREATE TABLE IF NOT EXISTS public.astra_chat_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES public.astra_chat_sessions(id) ON DELETE CASCADE,
    user_id TEXT NOT NULL, -- Added to match save_chat_message logic
    user_message TEXT NOT NULL,
    assistant_response TEXT NOT NULL,
    language TEXT DEFAULT 'en',
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- Index for fast retrieval of session history
CREATE INDEX IF NOT EXISTS idx_chat_messages_session ON public.astra_chat_history(session_id);


-- 2. ASTRA AUTOPILOT STATE
-- Stores the behavioral state for the Autopilot Engine.
-- This replaces the MySQL implementation of `PatientCareState`.

CREATE TABLE IF NOT EXISTS public.patient_care_states (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id TEXT NOT NULL UNIQUE, -- Links to your Legacy MySQL Patient ID
    
    -- Autopilot Switch
    is_autopilot_enabled BOOLEAN DEFAULT FALSE,
    
    -- Observation Signals ( synced from MySQL )
    last_consultation_date TIMESTAMP WITH TIME ZONE,
    last_consultation_id TEXT,
    active_prescription_id TEXT,
    medicine_end_date TIMESTAMP WITH TIME ZONE,

    -- Calculated Windows
    next_followup_window_start TIMESTAMP WITH TIME ZONE,
    next_followup_window_end TIMESTAMP WITH TIME ZONE,

    -- State Machine
    care_journey_stage TEXT DEFAULT 'new', -- new, consultation_done, treatment_active, needs_review, dropped_off
    
    -- Draft Actions (The "Pending" work)
    pending_autopilot_action JSONB, -- e.g. {"type": "booking_draft", "payload": {...}}
    
    last_autopilot_check TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- Index for the daily scheduler to find enabled patients quickly
CREATE INDEX IF NOT EXISTS idx_autopilot_enabled ON public.patient_care_states(is_autopilot_enabled);


-- 3. ASTRA CONSENT MANAGER
-- Stores user consent records for DISHA compliance.

CREATE TABLE IF NOT EXISTS public.astra_consents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    profile_id TEXT NOT NULL,
    purpose TEXT NOT NULL, -- e.g., 'astra_usage', 'document_upload'
    
    granted BOOLEAN DEFAULT FALSE,
    granted_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    expires_at TIMESTAMP WITH TIME ZONE,
    revoked_at TIMESTAMP WITH TIME ZONE,
    
    is_active BOOLEAN DEFAULT TRUE,
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_consents_lookup ON public.astra_consents(user_id, profile_id, purpose);


-- 4. ASTRA RAG MEMORY (Fallback Storage)
-- Backup storage for RAG vectors/metadata if FAISS is not persistent.

CREATE TABLE IF NOT EXISTS public.astra_rag_memory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id TEXT NOT NULL,
    memory_type TEXT NOT NULL, -- e.g., 'user_preferences'
    
    content TEXT NOT NULL,
    full_metadata JSONB DEFAULT '{}'::jsonb,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    expires_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_rag_profile ON public.astra_rag_memory(profile_id);


-- 5. PATIENT & MEDICAL RECORDS (EHR)
-- Stores structured patient profiles and their medical history.

CREATE TABLE IF NOT EXISTS public.patient_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id TEXT NOT NULL UNIQUE, -- Global Unique ID
    patient_code TEXT NOT NULL UNIQUE, -- Short code for quick lookup (PAT001)
    name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    age INTEGER,
    gender TEXT,
    address TEXT,
    emergency_contact TEXT,
    medical_conditions JSONB DEFAULT '[]'::jsonb,
    allergies JSONB DEFAULT '[]'::jsonb,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

CREATE INDEX IF NOT EXISTS idx_patient_code ON public.patient_profiles(patient_code);
CREATE INDEX IF NOT EXISTS idx_patient_phone ON public.patient_profiles(phone);

CREATE TABLE IF NOT EXISTS public.doctors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    doctor_id TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    specialization TEXT DEFAULT 'General Physician',
    qualifications JSONB DEFAULT '[]'::jsonb,
    experience_years INTEGER DEFAULT 0,
    consultation_fee INTEGER DEFAULT 500,
    languages JSONB DEFAULT '["English"]'::jsonb,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

CREATE TABLE IF NOT EXISTS public.consultations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    consultation_id TEXT NOT NULL UNIQUE,
    patient_id TEXT NOT NULL REFERENCES public.patient_profiles(patient_id),
    doctor_id TEXT NOT NULL REFERENCES public.doctors(doctor_id),
    doctor_name TEXT NOT NULL,
    appointment_date TIMESTAMP WITH TIME ZONE,
    consultation_type TEXT DEFAULT 'online', -- online, clinic
    status TEXT DEFAULT 'scheduled', -- scheduled, completed, cancelled
    diagnosis TEXT,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

CREATE TABLE IF NOT EXISTS public.prescription_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    prescription_id TEXT NOT NULL UNIQUE,
    patient_id TEXT NOT NULL REFERENCES public.patient_profiles(patient_id),
    doctor_id TEXT NOT NULL REFERENCES public.doctors(doctor_id),
    consultation_id TEXT REFERENCES public.consultations(consultation_id),
    diagnosis TEXT NOT NULL,
    notes TEXT,
    status TEXT DEFAULT 'created', -- created, notified, paid, shipped
    prescribed_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

CREATE TABLE IF NOT EXISTS public.prescribed_medicines (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    prescription_id TEXT NOT NULL REFERENCES public.prescription_records(prescription_id) ON DELETE CASCADE,
    medicine_name TEXT NOT NULL,
    quantity INTEGER DEFAULT 1,
    dose TEXT NOT NULL,
    schedule TEXT NOT NULL, -- 1-0-1
    timing TEXT NOT NULL, -- Before meals
    duration TEXT NOT NULL, -- 7 days
    instructions TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);


-- 6. MEDICINE REMINDERS & ADHERENCE
-- Tracks when patients should take medicine and if they did.

CREATE TABLE IF NOT EXISTS public.medicine_schedules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    prescription_id TEXT NOT NULL REFERENCES public.prescription_records(prescription_id),
    patient_id TEXT NOT NULL REFERENCES public.patient_profiles(patient_id),
    medicine_name TEXT NOT NULL,
    dose_amount TEXT NOT NULL,
    schedule_pattern TEXT NOT NULL,
    timing_type TEXT NOT NULL,
    start_date TIMESTAMP WITH TIME ZONE NOT NULL,
    end_date TIMESTAMP WITH TIME ZONE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

CREATE TABLE IF NOT EXISTS public.medicine_reminders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    schedule_id UUID NOT NULL REFERENCES public.medicine_schedules(id) ON DELETE CASCADE,
    patient_id TEXT NOT NULL REFERENCES public.patient_profiles(patient_id),
    reminder_datetime TIMESTAMP WITH TIME ZONE NOT NULL,
    dose_type TEXT NOT NULL, -- morning, afternoon, evening
    status TEXT DEFAULT 'scheduled', -- scheduled, sent, taken, missed
    patient_response TEXT,
    response_time TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);


-- 7. DISHA COMPLIANCE (EXTENDED)
-- Audit trails and consent records for health data.

CREATE TABLE IF NOT EXISTS public.patient_consents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id TEXT NOT NULL REFERENCES public.patient_profiles(patient_id),
    consent_type TEXT NOT NULL, -- data_storage, research, sharing
    purpose TEXT NOT NULL,
    granted BOOLEAN DEFAULT TRUE,
    granted_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    expires_at TIMESTAMP WITH TIME ZONE,
    revoked BOOLEAN DEFAULT FALSE,
    revoked_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS public.data_access_audits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id TEXT NOT NULL REFERENCES public.patient_profiles(patient_id),
    accessed_by_id TEXT NOT NULL,
    accessed_by_type TEXT NOT NULL, -- doctor, patient, system
    access_type TEXT NOT NULL, -- view, export, delete
    data_type TEXT NOT NULL, -- profile, prescription, audit
    purpose TEXT NOT NULL,
    success BOOLEAN DEFAULT TRUE,
    accessed_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);


-- 8. USER & SESSION MANAGEMENT (ASTRA CORE)
-- Tracks ASTRA users and their active sessions.

CREATE TABLE IF NOT EXISTS public.astra_users (
    id TEXT PRIMARY KEY, -- Firebase UID
    email TEXT UNIQUE NOT NULL,
    name TEXT,
    picture TEXT,
    email_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

CREATE TABLE IF NOT EXISTS public.astra_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL REFERENCES public.astra_users(id) ON DELETE CASCADE,
    session_token TEXT UNIQUE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);


-- 10. FINANCIAL ECOSYSTEM (PHASE 5)
-- Tracks doctor earnings and withdrawal requests.

CREATE TABLE IF NOT EXISTS public.doctor_wallets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    doctor_id TEXT NOT NULL UNIQUE REFERENCES public.doctors(doctor_id),
    total_earned INTEGER DEFAULT 0, -- Gross amount (100%)
    available_balance INTEGER DEFAULT 0, -- Net amount (70% share)
    withdrawn_amount INTEGER DEFAULT 0,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

CREATE TABLE IF NOT EXISTS public.withdrawal_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    doctor_id TEXT NOT NULL REFERENCES public.doctors(doctor_id),
    amount INTEGER NOT NULL,
    admin_commission_30 INTEGER NOT NULL,
    doctor_payout_70 INTEGER NOT NULL,
    status TEXT DEFAULT 'pending', -- pending, approved, rejected, completed
    payment_id TEXT, -- Razorpay Payout ID
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- Index for wallet lookups
CREATE INDEX IF NOT EXISTS idx_wallet_doctor ON public.doctor_wallets(doctor_id);

-- 11. MEDICINE INVENTORY CACHE
-- Cache for Shopify medicine catalog to allow ultra-fast in-stock prescription checks.
CREATE TABLE IF NOT EXISTS public.medicine_inventory_cache (
    medicine_name TEXT PRIMARY KEY,
    shopify_variant_id TEXT,
    is_in_stock BOOLEAN DEFAULT TRUE,
    price_cents INTEGER DEFAULT 0,
    stock_quantity INTEGER DEFAULT 100,
    last_synced_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

