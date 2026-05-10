CREATE TABLE IF NOT EXISTS services_servicesherosettings (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(200) NOT NULL,
    subtitle VARCHAR(300) NOT NULL,
    background_image VARCHAR(100) NULL,
    background_url VARCHAR(500) NOT NULL,
    is_active BOOLEAN NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);

INSERT INTO services_servicesherosettings 
(title, subtitle, background_url, is_active, created_at, updated_at)
VALUES (
    'Our Services',
    'Comprehensive Real Estate Solutions',
    'https://images.unsplash.com/photo-1560518883-ce09059eeffa?auto=format&fit=crop&q=80&w=1920',
    1,
    datetime('now'),
    datetime('now')
);
