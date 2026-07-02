-- ============================================================================
-- ASTRA AI - SUPABASE SCHEMA (Astra Features)
-- ============================================================================

-- 1. FAMILY & CAREGIVER SYSTEM
CREATE TABLE IF NOT EXISTS public.family_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    family_id UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
    primary_patient_id TEXT NOT NULL, -- Auth0/Firebase ID
    name TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

CREATE TABLE IF NOT EXISTS public.family_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    member_id UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
    family_id UUID NOT NULL REFERENCES public.family_profiles(family_id) ON DELETE CASCADE,
    patient_id TEXT, -- Optional, if they have their own account
    name TEXT NOT NULL,
    relation TEXT NOT NULL,
    age INTEGER,
    gender TEXT,
    permissions JSONB DEFAULT '{"view": true, "remind": true}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- 2. HEALTH TIMELINE ENGINE
CREATE TABLE IF NOT EXISTS public.health_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_id UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
    patient_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    summary TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    source TEXT NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- 3. FOLLOW-UP ORCHESTRATION
CREATE TABLE IF NOT EXISTS public.follow_up_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    condition TEXT NOT NULL,
    after_days INTEGER NOT NULL,
    action TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- 4. LONG-TERM WELLNESS & HABIT ENGINE
CREATE TABLE IF NOT EXISTS public.wellness_habits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    habit_id UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
    patient_id TEXT NOT NULL,
    category TEXT NOT NULL,
    name TEXT NOT NULL,
    frequency TEXT NOT NULL,
    reminders_enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- 5. DOCTOR AUTHORITY & SAFETY (Audit Logs)
CREATE TABLE IF NOT EXISTS public.audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    action TEXT NOT NULL,
    source TEXT NOT NULL DEFAULT 'astra',
    patient_id TEXT,
    doctor_id TEXT,
    details JSONB DEFAULT '{}'::jsonb,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- 6. USER & SESSION MANAGEMENT
CREATE TABLE IF NOT EXISTS public.astra_users (
    id TEXT PRIMARY KEY, -- Auth0/Firebase ID
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
    last_accessed TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);
