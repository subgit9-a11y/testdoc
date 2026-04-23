-- ==========================================
-- ADMIN PANEL (MYSQL) IMPLEMENTATION SQL
-- Run this in phpMyAdmin or MySQL Console
-- ==========================================

-- 1. Update Existing Doctor Table
-- Adds synchronization and verification fields to your main Laravel table
ALTER TABLE `doctor` 
ADD COLUMN IF NOT EXISTS `unique_id` VARCHAR(50) DEFAULT NULL AFTER `id`,
ADD COLUMN IF NOT EXISTS `is_face_verified` TINYINT(1) DEFAULT 0 AFTER `status`,
ADD COLUMN IF NOT EXISTS `post_mortem_hospital` VARCHAR(255) DEFAULT NULL AFTER `is_face_verified`,
ADD COLUMN IF NOT EXISTS `face_photo_url` TEXT DEFAULT NULL AFTER `post_mortem_hospital`,
ADD COLUMN IF NOT EXISTS `certificate` TEXT DEFAULT NULL AFTER `face_photo_url`;

-- 2. Create Audit/Sync Table (Optional but Recommended)
-- Used for logging verified doctors from the mobile app
CREATE TABLE IF NOT EXISTS `astra_verified_doctors` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `unique_id` VARCHAR(50) UNIQUE NOT NULL,
    `name` VARCHAR(255) NOT NULL,
    `email` VARCHAR(255) UNIQUE NOT NULL,
    `phone` VARCHAR(20),
    `is_face_verified` TINYINT(1) DEFAULT 0,
    `photo_url` TEXT,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
