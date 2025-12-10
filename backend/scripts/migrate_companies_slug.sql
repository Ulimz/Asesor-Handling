-- Add slug column
ALTER TABLE companies ADD COLUMN IF NOT EXISTS slug VARCHAR;

-- Truncate to reset data
TRUNCATE TABLE companies RESTART IDENTITY;

-- Insert with explicit slugs
INSERT INTO companies (name, slug, sector, is_active) VALUES 
('Aviapartner', 'aviapartner', 'Handling', true),
('AzulHandling', 'azul', 'Handling', true),
('EasyJet', 'easyjet', 'Handling', true),
('Groundforce', 'groundforce', 'Handling', true),
('South Europe Ground Services (Iberia)', 'iberia', 'Handling', true),
('Menzies', 'menzies', 'Handling', true),
('Swissport', 'swissport', 'Handling', true),
('WFS', 'wfs', 'Handling', true),
('Jet2', 'jet2', 'Handling', true),
('Norwegian', 'norwegian', 'Handling', true),
('Clece', 'clece', 'Handling', true),
('Acciona', 'acciona', 'Handling', true);

-- Ensure slug is not null
UPDATE companies SET slug = LOWER(REPLACE(name, ' ', '-')) WHERE slug IS NULL;
ALTER TABLE companies ALTER COLUMN slug SET NOT NULL;
CREATE UNIQUE INDEX IF NOT EXISTS idx_companies_slug ON companies(slug);
