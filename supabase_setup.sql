-- ==========================================
-- COMPLETE SUPABASE SETUP SQL
-- Run this in the Supabase SQL Editor
-- ==========================================

-- 1. Enable Required Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 2. Create Doctors Table (Cloud Storage)
-- Dropping existing table to ensure the new schema with unique_id and email is applied
DROP TABLE IF EXISTS public.doctors CASCADE;

CREATE TABLE public.doctors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    unique_id TEXT UNIQUE NOT NULL,      -- e.g., DOC-2026-I-X
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT,
    gender TEXT,
    dob TEXT,
    photo_url TEXT,                      -- Link to identity photo
    certificate_url TEXT,                -- Link to medical certificate
    is_face_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Enable Row Level Security (RLS) on Table
ALTER TABLE public.doctors ENABLE ROW LEVEL SECURITY;

-- 4. Set Database Policies
-- Drop existing policies first to allow re-running the script
DROP POLICY IF EXISTS "Public Read Access" ON public.doctors;
DROP POLICY IF EXISTS "Enable Insert for All" ON public.doctors;
DROP POLICY IF EXISTS "Enable update for authenticated users" ON public.doctors;

-- Allow anyone to read doctor profiles. This is safe for public-facing data.
CREATE POLICY "Public Read Access" ON public.doctors FOR SELECT USING (true);

-- Allow any authenticated user to create a new doctor profile.
CREATE POLICY "Enable Insert for All" ON public.doctors FOR INSERT WITH CHECK (auth.role() = 'authenticated');

-- IMPORTANT: This allows any authenticated user (any doctor) to update any other doctor's record.
-- For true security, you should add a user_id column that links to auth.users(id)
-- and change this policy to: USING (auth.uid() = user_id)
CREATE POLICY "Enable update for authenticated users" ON public.doctors FOR UPDATE USING (auth.role() = 'authenticated') WITH CHECK (auth.role() = 'authenticated');

-- 5. Initialize Storage Bucket
-- Create the bucket if it doesn't exist
INSERT INTO storage.buckets (id, name, public)
VALUES ('doctor-profiles', 'doctor-profiles', true)
ON CONFLICT (id) DO NOTHING;

-- 6. Set Storage Policies (Allow app to upload/read)
-- Drop existing storage policies first
DROP POLICY IF EXISTS "Allow public read access to profiles" ON storage.objects;
DROP POLICY IF EXISTS "Allow authenticated inserts to profiles" ON storage.objects;
-- NOTE: A secure update/delete policy would require linking file ownership to a user ID.

-- Policy: Allow public access to read files
CREATE POLICY "Allow public read access to profiles"
ON storage.objects FOR SELECT
USING (bucket_id = 'doctor-profiles');

-- Policy: Allow authenticated users to upload files (e.g., profile photo, certificate)
CREATE POLICY "Allow authenticated inserts to profiles"
ON storage.objects FOR INSERT
WITH CHECK (bucket_id = 'doctor-profiles' AND auth.role() = 'authenticated');

-- WARNING: There is no UPDATE or DELETE policy. This means files cannot be easily overwritten or deleted.
-- A secure implementation requires more complex logic, often using Postgres Functions,
-- to check ownership before allowing updates or deletes. For now, this prevents malicious overwrites.

-- 7. Trigger for updated_at
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Drop trigger first to avoid conflicts on re-run
DROP TRIGGER IF EXISTS update_doctor_modtime ON public.doctors;

CREATE TRIGGER update_doctor_modtime
    BEFORE UPDATE ON public.doctors
    FOR EACH ROW
    EXECUTE PROCEDURE update_modified_column();
