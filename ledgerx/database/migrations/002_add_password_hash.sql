-- Add password_hash for JWT auth (optional; use Supabase Auth in production)
ALTER TABLE users ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255);
