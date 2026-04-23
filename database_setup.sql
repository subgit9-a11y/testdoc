-- Run this in your MySQL database (phpMyAdmin)
ALTER TABLE `doctor` 
ADD COLUMN IF NOT EXISTS `unique_id` VARCHAR(50) DEFAULT NULL AFTER `id`,
ADD COLUMN IF NOT EXISTS `is_face_verified` TINYINT(1) DEFAULT 0 AFTER `status`,
ADD COLUMN IF NOT EXISTS `post_mortem_hospital` VARCHAR(255) DEFAULT NULL AFTER `is_face_verified`,
ADD COLUMN IF NOT EXISTS `face_photo_url` TEXT DEFAULT NULL AFTER `post_mortem_hospital`,
ADD COLUMN IF NOT EXISTS `certificate` TEXT DEFAULT NULL AFTER `face_photo_url`;

-- For Supabase (SQL Editor)
-- Create a table 'doctors' if not exists
CREATE TABLE IF NOT EXISTS public.doctors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    unique_id TEXT UNIQUE,
    name TEXT,
    email TEXT,
    photo_url TEXT,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE public.doctors ENABLE ROW LEVEL SECURITY;

-- Allow public read access
DROP POLICY IF EXISTS "Public Read Access" ON public.doctors;
CREATE POLICY "Public Read Access" ON public.doctors FOR SELECT USING (true);

-- Allow authenticated insert/update
DROP POLICY IF EXISTS "Auth Insert Access" ON public.doctors;
DROP POLICY IF EXISTS "Auth Update Access" ON public.doctors;

CREATE POLICY "Auth Insert Access" ON public.doctors FOR INSERT WITH CHECK (true);
CREATE POLICY "Auth Update Access" ON public.doctors FOR UPDATE USING (true);
