-- Migration V2: Add User Profile Fields
ALTER TABLE users ADD COLUMN IF NOT EXISTS preferred_name VARCHAR;
ALTER TABLE users ADD COLUMN IF NOT EXISTS company_slug VARCHAR;
ALTER TABLE users ADD COLUMN IF NOT EXISTS job_group VARCHAR;
ALTER TABLE users ADD COLUMN IF NOT EXISTS salary_level INTEGER;
ALTER TABLE users ADD COLUMN IF NOT EXISTS contract_type VARCHAR;
ALTER TABLE users ADD COLUMN IF NOT EXISTS seniority_date VARCHAR;

-- Verify columns
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'users';
