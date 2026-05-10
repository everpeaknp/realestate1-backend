-- Create the missing services_servicesherosettings table
CREATE TABLE IF NOT EXISTS "services_servicesherosettings" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "title" varchar(200) NOT NULL,
    "subtitle" varchar(300) NOT NULL,
    "background_image" varchar(100) NULL,
    "background_url" varchar(500) NOT NULL,
    "is_active" bool NOT NULL,
    "created_at" datetime NOT NULL,
    "updated_at" datetime NOT NULL
);

-- Insert default record
INSERT INTO "services_servicesherosettings" 
(title, subtitle, background_url, is_active, created_at, updated_at)
VALUES (
    'Our Services',
    'Comprehensive Real Estate Solutions',
    'https://images.unsplash.com/photo-1560518883-ce09059eeffa?auto=format&fit=crop&q=80&w=1920',
    1,
    datetime('now'),
    datetime('now')
);

-- Verify the table was created
SELECT * FROM services_servicesherosettings;
